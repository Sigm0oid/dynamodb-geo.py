# Geo Library for Amazon DynamoDB

This project is an unofficial port of [awslabs/dynamodb-geo][dynamodb-geo], bringing creation and querying of geospatial data to Python developers using [Amazon DynamoDB][dynamodb].

## Features

- **Box Queries:** Return all of the items that fall within a pair of geo points that define a rectangle as projected onto a sphere.
- **Radius Queries:** Return all of the items that are within a given radius of a geo point.
- **Basic CRUD Operations:** Create, retrieve, update, and delete geospatial data items.
- **Customizable:** Access to raw request and result objects from the AWS SDK for python.

## Installation

```python
pip install s2sphere
pip install boto3
pip install dynamodbgeo
```

## Getting started

First you'll need to import the AWS sdk and set up your DynamoDB connection:

```python
import boto3
import dynamodbgeo
import uuid
dynamodb = boto3.client('dynamodb', region_name='us-east-2')
```

Next you must create an instance of `GeoDataManagerConfiguration` for each geospatial table you wish to interact with. This is a container for various options (see API below), but you must always provide a `DynamoDB` instance and a table name.

```python
config = dynamodbgeo.GeoDataManagerConfiguration(dynamodb, 'geo_test_8')
```

Finally, you should instantiate a manager to query and write to the table using this config object.

```python
geoDataManager = dynamodbgeo.GeoDataManager(config)
```

## Choosing a `hashKeyLength` (optimising for performance and cost)

The `hashKeyLength` is the number of most significant digits (in base 10) of the 64-bit geo hash to use as the hash key. Larger numbers will allow small geographical areas to be spread across DynamoDB partitions, but at the cost of performance as more [queries][dynamodb-query] need to be executed for box/radius searches that span hash keys. See [these tests from the JS version][hashkeylength-tests](TODO) for an idea of how query performance scales with `hashKeyLength` for different search radii.

If your data is sparse, a large number will mean more RCUs since more empty queries will be executed and each has a minimum cost. However if your data is dense and `hashKeyLength` too short, more RCUs will be needed to read a hash key and a higher proportion will be discarded by server-side filtering.

From the [AWS `Query` documentation][dynamodb-query]

> DynamoDB calculates the number of read capacity units consumed based on item size, not on the amount of data that is returned to an application. ... **The number will also be the same whether or not you use a `FilterExpression`**

Optimally, you should pick the largest `hashKeyLength` your usage scenario allows. The wider your typical radius/box queries, the smaller it will need to be.

Note that the [Java version][dynamodb-geo] uses a `hashKeyLength` of `6` by default. The same value will need to be used if you access the same data with both clients.

This is an important early choice, since changing your `hashKeyLength` will mean recreating your data.

From the [AWS `Query` documentation][dynamodb-query]

> DynamoDB calculates the number of read capacity units consumed based on item size, not on the amount of data that is returned to an application. ... **The number will also be the same whether or not you use a `FilterExpression`**

Optimally, you should pick the largest `hashKeyLength` your usage scenario allows. The wider your typical radius/box queries, the smaller it will need to be.

Note that the [Java version][dynamodb-geo] uses a `hashKeyLength` of `6` by default. The same value will need to be used if you access the same data with both clients.

This is an important early choice, since changing your `hashKeyLength` will mean recreating your data.

## Creating a table

`GeoTableUtil` has a static method `getCreateTableRequest` for helping you prepare a [DynamoDB CreateTable request][createtable] request, given a `GeoDataManagerConfiguration`.

You can modify this request as desired before executing it using AWS's DynamoDB SDK.

Example:

```python
# Pick a hashKeyLength appropriate to your usage
config.hashKeyLength = 3

# Use GeoTableUtil to help construct a CreateTableInput.
table_util = dynamodbgeo.GeoTableUtil(config)
create_table_input=table_util.getCreateTableRequest()

#tweaking the base table parameters as a dict
create_table_input["ProvisionedThroughput"]['ReadCapacityUnits']=5

# Use GeoTableUtil to create the table
table_util.create_table(create_table_input)
```

## Adding data

```python
#preparing non key attributes for the item to add

PutItemInput = {
        'Item': {
            'Country': {'S': "Tunisia"},
            'Capital': {'S': "Tunis"},
            'year': {'S': '2020'}
        },
        'ConditionExpression': "attribute_not_exists(hashKey)" # ... Anything else to pass through to `putItem`, eg ConditionExpression

}
geoDataManager.put_Point(dynamodbgeo.PutPointInput(
        dynamodbgeo.GeoPoint(36.879163, 10.243120), # latitude then latitude longitude
         str( uuid.uuid4()), # Use this to ensure uniqueness of the hash/range pairs.
         PutItemInput # pass the dict here
        ))

```

See also [DynamoDB PutItem request][putitem]

## Updating a specific point

Note that you cannot update the hash key, range key, geohash or geoJson. If you want to change these, you'll need to recreate the record.

You must specify a `RangeKeyValue`, a `GeoPoint`, and an `UpdateItemInput dict` matching the [DynamoDB UpdateItem][updateitem] request (`TableName` and `Key` are filled in for you).

#### Note : You must NOT update geoJson and geohash attributes.

```python
#define a dict of the item to update
UpdateItemDict= { # Dont provide TableName and Key, they are filled in for you
        "UpdateExpression": "set Capital = :val1",
        "ConditionExpression": "Capital = :val2",
        "ExpressionAttributeValues": {
            ":val1": {"S": "Tunis"},
            ":val2": {"S": "Ariana"}
        },
        "ReturnValues": "ALL_NEW"
}
geoDataManager.update_Point(dynamodbgeo.UpdateItemInput(
        dynamodbgeo.GeoPoint(36.879163,10.24312), # latitude then latitude longitude
         "1e955491-d8ba-483d-b7ab-98370a8acf82", # Use this to ensure uniqueness of the hash/range pairs.
         UpdateItemDict # pass the dict that contain the remaining parameters here
         ))
```

## Deleting a specific point

You must specify a `RangeKeyValue` and a `GeoPoint`. Optionally, you can pass `DeleteItemInput` matching [DynamoDB DeleteItem][deleteitem] request (`TableName` and `Key` are filled in for you).

```python
# Preparing dict of the item to delete
DeleteItemDict= {
            "ConditionExpression": "attribute_exists(Country)",
            "ReturnValues": "ALL_OLD"
            # Don't put keys here, they will be generated for you implecitly
        }
geoDataManager.delete_Point(
    dynamodbgeo.DeleteItemInput(
    dynamodbgeo.GeoPoint(36.879163,10.24312), # latitude then latitude longitude
        "0df9742f-619b-49e5-b79e-9fb94279d30c", # Use this to ensure uniqueness of the hash/range pairs.
        DeleteItemDict # pass the dict that contain the remaining parameters here
        ))
```

## Rectangular queries

Query by rectangle by specifying a `MinPoint` and `MaxPoint`. You can also pass filtring criteria in a dictionary as explained in the example.
#### NOTE: You cannot add filtring criteria related to the key attributes as they're used in the geo spacial filtring.

```python
# Querying a rectangle
QueryRectangleInput={
        "FilterExpression": "Country = :val1",
        "ExpressionAttributeValues": {
            ":val1": {"S": "Italy"},
        }
    }
print(geoDataManager.queryRectangle(
        dynamodbgeo.QueryRectangleRequest(
            dynamodbgeo.GeoPoint(36.878184, 10.242358),
            dynamodbgeo.GeoPoint(36.879317, 10.243648),QueryRectangleInput)))

```

## Radius queries

Query by radius by specifying a `CenterPoint` and `RadiusInMeter`. You can also pass filtring criteria in a dictionary as explained in the example.

#### NOTE: 
Same as in query rectangle, you cannot add filtring criteria related to the key attributes as they're used in the geo spacial filtring.

```python
# Querying 95 meter from the center point (36.879131, 10.243057)
QueryRadiusInput={
        "FilterExpression": "Country = :val1",
        "ExpressionAttributeValues": {
            ":val1": {"S": "Italy"},
        }
    }

query_reduis_result=geoDataManager.queryRadius(
    dynamodbgeo.QueryRadiusRequest(
        dynamodbgeo.GeoPoint(36.879131, 10.243057), # center point
        95, QueryRadiusInput, sort = True)) # diameter

```

## Batch operations

TODO:

## Configuration reference

These are public properties of a `GeoDataManagerConfiguration` instance. After creating the config object you may modify these properties.

#### geohashAttributeName: string = "geohash"

The name of the attribute storing the full 64-bit geohash. Its value is auto-generated based on item coordinates.

#### hashKeyAttributeName: string = "hashKey"

The name of the attribute storing the first `hashKeyLength` digits (default 2) of the geo hash, used as the hash (aka partition) part of a [hash/range primary key pair][hashrange]. Its value is auto-generated based on item coordinates.

#### hashKeyLength: number = 2

See [above][choosing-hashkeylength].

#### rangeKeyAttributeName: string = "rangeKey"

The name of the attribute storing the range key, used as the range (aka sort) part of a [hash/range key primary key pair][hashrange]. Its value must be specified by you (hash-range pairs must be unique).

#### geoJsonAttributeName: string = "geoJson"

The name of the attribute which will contain the longitude/latitude pair in a GeoJSON-style point (see also `longitudeFirst`).

#### geohashIndexName: string = "geohash-index"

The name of the index to be created against the geohash. Only used for creating new tables.

## Example

TODO

## Limitations

### No composite key support

Currently, the library does not support composite keys. You may want to add tags such as restaurant, bar, and coffee shop, and search locations of a specific category; however, it is currently not possible. You need to create a table for each tag and store the items separately.

### Queries retrieve all paginated data

Although low level [DynamoDB Query][dynamodb-query] requests return paginated results, this library automatically pages through the entire result set. When querying a large area with many points, a lot of Read Capacity Units may be consumed.

### More Read Capacity Units

The library retrieves candidate Geo points from the cells that intersect the requested bounds. The library then post-processes the candidate data, filtering out the specific points that are outside the requested bounds. Therefore, the consumed Read Capacity Units will be higher than the final results dataset. Typically 8 queries are exectued per radius or box search.

### High memory consumption

Because all paginated `Query` results are loaded into memory and processed, it may consume substantial amounts of memory for large datasets.

### Dataset density limitation

The Geohash used in this library is roughly centimeter precision. Therefore, the library is not suitable if your dataset has much higher density.

[updateitem]: http://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_UpdateItem.html
[deleteitem]: http://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_DeleteItem.html
[putitem]: http://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_PutItem.html
[createtable]: http://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_CreateTable.html
[hashrange]: http://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.CoreComponents.html#HowItWorks.CoreComponents.PrimaryKey
[readconsistency]: http://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.ReadConsistency.html
[geojson]: https://geojson.org/geojson-spec.html
[example]: https://github.com/rh389/dynamodb-geo.js/tree/master/example
[dynamodb-geo]: https://github.com/awslabs/dynamodb-geo
[dynamodb]: http://aws.amazon.com/dynamodb
[dynamodb-query]: http://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_Query.html
[hashkeylength-tests]: https://github.com/rh389/dynamodb-geo.js/blob/master/test/integration/hashKeyLength.ts
[choosing-hashkeylength]: #choosing-a-hashkeylength-optimising-for-performance-and-cost
