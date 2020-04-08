# Geo Library for Amazon DynamoDB
This project is an unofficial port of [awslabs/dynamodb-geo][dynamodb-geo], bringing creation and querying of geospatial data to Python developers using [Amazon DynamoDB][dynamodb].

## Features
* **Box Queries:** Return all of the items that fall within a pair of geo points that define a rectangle as projected onto a sphere.
* **Radius Queries:** Return all of the items that are within a given radius of a geo point.
* **Basic CRUD Operations:** Create, retrieve geospatial data items. TODO: update, and delete
* **Customizable:** Access to raw request and result objects from the AWS SDK for python.

## Installation
TODO

## Getting started
First you'll need to import the AWS sdk and set up your DynamoDB connection:

```python
import boto3
dynamodb = boto3.client('dynamodb', region_name='us-east-2')
```

Next you must create an instance of `GeoDataManagerConfiguration` for each geospatial table you wish to interact with. This is a container for various options (see API below), but you must always provide a `DynamoDB` instance and a table name.

```python
config = GeoDataManagerConfiguration(dynamodb, 'geo_test')
geoDataManager = GeoDataManager(config)
```

Finally, you should instantiate a manager to query and write to the table using this config object.

```python
geoDataManager = GeoDataManager(config)
```

## Choosing a `hashKeyLength` (optimising for performance and cost)
TODO

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
table_util = GeoTableUtil(config)
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
geoDataManager.put_Point(PutPointInput(
    GeoPoint(36.879163, 10.243120), # latitude then latitude longitude
        str( uuid.uuid4()), # Use this to ensure uniqueness of the hash/range pairs.
        PutItemInput # pass the dict here
        ))
            
```
See also [DynamoDB PutItem request][putitem]

## Updating a specific point
Note that you cannot update the hash key, range key, geohash or geoJson. If you want to change these, you'll need to recreate the record.

You must specify a `RangeKeyValue`, a `GeoPoint`, and an `UpdateItemInput` matching the [DynamoDB UpdateItem][updateitem] request (`TableName` and `Key` are filled in for you).

```python
#TODO
```

## Deleting a specific point
You must specify a `RangeKeyValue` and a `GeoPoint`. Optionally, you can pass `DeleteItemInput` matching [DynamoDB DeleteItem][deleteitem] request (`TableName` and `Key` are filled in for you).

```python
#TODO
```
## Rectangular queries
Query by rectangle by specifying a `MinPoint` and `MaxPoint`.

```python
# Querying a rectangle
geoDataManager.queryRectangle(
            QueryRectangleRequest(
                GeoPoint(36.878184, 10.242358), # min point
                GeoPoint(36.879317, 10.243648))) # max point
```

## Radius queries
Query by radius by specifying a `CenterPoint` and `RadiusInMeter`.

```python
# Querying 95 meter from the center point (36.879131, 10.243057)
geoDataManager.queryRadius(
    QueryRadiusRequest(
        GeoPoint(36.879131, 10.243057), # center point
        95)) # diameter
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
See the [example on Github][example]

## Limitations

### No Delete and Update Item supported
Currently, the library does not support update and delete item for now. The items for now can be deleted using AWS SDK [UpdateItem][updateitem] and [DeleteItem][deleteitem]

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

