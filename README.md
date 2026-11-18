# dynamodbgeo — Geospatial Library for Amazon DynamoDB in Python

[![PyPI version](https://img.shields.io/pypi/v/dynamodbgeo.svg)](https://pypi.org/project/dynamodbgeo/)
[![Python versions](https://img.shields.io/pypi/pyversions/dynamodbgeo.svg)](https://pypi.org/project/dynamodbgeo/)
[![CI](https://github.com/Sigm0oid/dynamodb-geo.py/actions/workflows/ci.yml/badge.svg)](https://github.com/Sigm0oid/dynamodb-geo.py/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

`dynamodbgeo` is a Python port of [awslabs/dynamodb-geo][dynamodb-geo] that enables storing, updating, and querying geospatial point data in [Amazon DynamoDB][dynamodb] using Google S2 Geometry geohashes.

---

## Key Features

- **Radius Queries:** Find all points within a given radius (in meters) of a center coordinate, with optional nearest-first distance sorting (`sort=True`), including accurate handling across the `±180°` antimeridian and near the poles.
- **Bounding-Box (Rectangle) Queries:** Retrieve all points falling within a geographic bounding rectangle defined by southwest (`minPoint`) and northeast (`maxPoint`) coordinates.
- **Cursor-Based Pagination:** Stream spatial query results page-by-page via `queryRadiusPaginated` and `queryRectanglePaginated` using `limit` and `next_token` to bound memory and Read Capacity Unit (RCU) usage.
- **Point CRUD Operations:** Create (`put_Point`), read (`get_Point`), update (`update_Point`), and delete (`delete_Point`) geospatial items while passing native `boto3` `Table` parameters such as `ConditionExpression`, `FilterExpression`, and `ProjectionExpression`.
- **Table Provisioning Utilities:** Generate customizable `CreateTable` payloads (with the required Local Secondary Index) and create or delete tables via `GeoTableUtil`.

---

## How It Works

1. **Indexing on Write:** Each `(latitude, longitude)` coordinate is mapped onto a 64-bit [S2 Cell ID][s2geometry] (`geohash`). The first `hashKeyLength` digits become the DynamoDB partition key (`hashKey`), your application-supplied identifier becomes the sort key (`rangeKey`), and a Local Secondary Index (`geohash-index`) indexes `(hashKey, geohash)`.
2. **Querying on Read:** Given a search circle or bounding rectangle, `dynamodbgeo` computes a covering set of S2 cells, fans out `BETWEEN` range queries against `geohash-index`, and post-filters candidate items using exact spherical geometry so only points strictly inside your target region are returned.

---

## Installation

```bash
pip install dynamodbgeo
```

**Requirements:** Python 3.7+ (`boto3>=1.11.8` and `s2sphere>=0.2.5` are installed automatically).

---

## Quick Start

```python
import uuid
import boto3
import dynamodbgeo

# 1. Connect to DynamoDB using the high-level boto3 ServiceResource
dynamodb = boto3.resource("dynamodb", region_name="us-east-2")

# 2. Configure your geospatial table
config = dynamodbgeo.GeoDataManagerConfiguration("places_geo", dynamodb)
config.hashKeyLength = 3  # Tune based on your typical search radius (see guide below)

# 3. Create the table (with Local Secondary Index) if it does not exist yet
table_util = dynamodbgeo.GeoTableUtil(config)
create_table_input = table_util.getCreateTableRequest()
create_table_input["ProvisionedThroughput"]["ReadCapacityUnits"] = 5
table_util.create_table(create_table_input)

# 4. Initialize GeoDataManager
geo_manager = dynamodbgeo.GeoDataManager(config)

# 5. Insert a geospatial point (latitude first, then longitude)
point_id = str(uuid.uuid4())
geo_manager.put_Point(
    dynamodbgeo.PutPointInput(
        dynamodbgeo.GeoPoint(36.879163, 10.243120),
        point_id,
        {
            "Item": {
                "name": "Carthage Station",
                "country": "Tunisia",
                "category": "transit",
            },
            "ConditionExpression": "attribute_not_exists(hashKey)",
        },
    )
)

# 6. Query within a 500-meter radius, sorted nearest-first
nearby = geo_manager.queryRadius(
    dynamodbgeo.QueryRadiusRequest(
        dynamodbgeo.GeoPoint(36.879131, 10.243057),
        500,
        {
            "FilterExpression": "country = :country",
            "ExpressionAttributeValues": {":country": "Tunisia"},
        },
        sort=True,
    )
)
print(nearby)
```

---

## Usage Guide

> **Coordinate Convention:** `dynamodbgeo.GeoPoint(latitude, longitude)` always takes **`latitude` first** (`-90` to `90`) and **`longitude` second** (`-180` to `180`), in decimal degrees.

### 1. Creating and Deleting Tables

`GeoTableUtil.getCreateTableRequest()` returns a standard `boto3` [`create_table`][createtable] dictionary preconfigured with `(hashKey, rangeKey)` primary keys and the `geohash-index` Local Secondary Index. Customize it (for example, switching to `BillingMode="PAY_PER_REQUEST"` or adjusting throughput) before calling `create_table`:

```python
table_util = dynamodbgeo.GeoTableUtil(config)
create_table_input = table_util.getCreateTableRequest()

# Optional: use on-demand capacity instead of provisioned throughput
create_table_input.pop("ProvisionedThroughput", None)
create_table_input["BillingMode"] = "PAY_PER_REQUEST"

table_util.create_table(create_table_input)

# Delete the table when cleaning up test/ephemeral environments
# table_util.delete_table()
```

### 2. Adding a Point (`put_Point`)

Provide a `GeoPoint`, a unique `RangeKeyValue` (such as a UUID), and an optional dictionary of parameters forwarded to [`Table.put_item`][putitem]:

```python
response = geo_manager.put_Point(
    dynamodbgeo.PutPointInput(
        dynamodbgeo.GeoPoint(36.879163, 10.243120),
        str(uuid.uuid4()),
        {
            "Item": {
                "Country": "Tunisia",
                "Capital": "Tunis",
                "year": "2020",
            },
            "ConditionExpression": "attribute_not_exists(hashKey)",
        },
    )
)
```

### 3. Retrieving a Point (`get_Point`)

Retrieve a single item when you know both its `GeoPoint` (used to derive `hashKey`) and its `RangeKeyValue`:

```python
response = geo_manager.get_Point(
    dynamodbgeo.GetPointInput(
        dynamodbgeo.GeoPoint(36.879163, 10.243120),
        "1e955491-d8ba-483d-b7ab-98370a8acf82",
    )
)
item = response.get("Item")
```

### 4. Updating a Point (`update_Point`)

Pass `GeoPoint`, `RangeKeyValue`, and a dictionary matching [`Table.update_item`][updateitem] (`Key` is populated automatically):

> **Important:** Do **not** modify `hashKey`, `rangeKey`, `geohash`, or `geoJson` via `update_Point`. If a point's coordinates change, delete the existing item and insert a new one.

```python
response = geo_manager.update_Point(
    dynamodbgeo.UpdateItemInput(
        dynamodbgeo.GeoPoint(36.879163, 10.243120),
        "1e955491-d8ba-483d-b7ab-98370a8acf82",
        {
            "UpdateExpression": "SET Capital = :new_cap",
            "ConditionExpression": "Capital = :old_cap",
            "ExpressionAttributeValues": {
                ":new_cap": "Tunis",
                ":old_cap": "Ariana",
            },
            "ReturnValues": "ALL_NEW",
        },
    )
)
```

### 5. Deleting a Point (`delete_Point`)

Pass `GeoPoint`, `RangeKeyValue`, and an optional dictionary matching [`Table.delete_item`][deleteitem]:

```python
response = geo_manager.delete_Point(
    dynamodbgeo.DeleteItemInput(
        dynamodbgeo.GeoPoint(36.879163, 10.243120),
        "0df9742f-619b-49e5-b79e-9fb94279d30c",
        {
            "ConditionExpression": "attribute_exists(Country)",
            "ReturnValues": "ALL_OLD",
        },
    )
)
```

### 6. Rectangular (Bounding-Box) Queries (`queryRectangle`)

Query all items inside the spherical rectangle bounded by `minPoint` (southwest corner) and `maxPoint` (northeast corner). Optional [`Table.query`][dynamodb-query] parameters such as `FilterExpression` or `ProjectionExpression` can be passed via `query_input_dict`:

> **Note:** Do not specify `KeyConditionExpression` on key attributes, as `dynamodbgeo` manages `KeyConditionExpression` internally for geohash range scans. If you pass `ProjectionExpression`, ensure `geoJson` (`config.geoJsonAttributeName`) is included so post-filtering can read item coordinates.

```python
items = geo_manager.queryRectangle(
    dynamodbgeo.QueryRectangleRequest(
        dynamodbgeo.GeoPoint(36.878184, 10.242358),  # minPoint (SW)
        dynamodbgeo.GeoPoint(36.879317, 10.243648),  # maxPoint (NE)
        {
            "FilterExpression": "Country = :country",
            "ExpressionAttributeValues": {":country": "Tunisia"},
        },
    )
)
```

### 7. Radius Queries (`queryRadius`)

Query all items within `radiusInMeter` meters of `centerPoint`. Set `sort=True` to return results ordered from nearest to farthest:

```python
items = geo_manager.queryRadius(
    dynamodbgeo.QueryRadiusRequest(
        dynamodbgeo.GeoPoint(36.879131, 10.243057),  # centerPoint
        95,                                          # radius in meters
        {
            "FilterExpression": "Country = :country",
            "ExpressionAttributeValues": {":country": "Tunisia"},
        },
        sort=True,
    )
)
```

### 8. Paginated Queries (`queryRadiusPaginated` & `queryRectanglePaginated`)

For large datasets or wide search areas, use `queryRadiusPaginated` or `queryRectanglePaginated` to fetch pages of `limit` items using an opaque `next_token` cursor:

```python
next_token = None
all_items = []

while True:
    page = geo_manager.queryRadiusPaginated(
        dynamodbgeo.QueryRadiusRequest(
            dynamodbgeo.GeoPoint(36.879131, 10.243057),
            5000,
            sort=False,
        ),
        limit=25,
        next_token=next_token,
    )
    all_items.extend(page["Items"])
    next_token = page["NextToken"]
    if not next_token:
        break
```

Rectangle pagination follows the exact same pattern:

```python
page = geo_manager.queryRectanglePaginated(
    dynamodbgeo.QueryRectangleRequest(
        dynamodbgeo.GeoPoint(36.878184, 10.242358),
        dynamodbgeo.GeoPoint(36.879317, 10.243648),
    ),
    limit=25,
    next_token=None,
)
```

> **Note on `sort=False` vs `sort=True`:** When `sort=False` (and in `queryRectanglePaginated`), pagination streams lazily across S2 geohash ranges and DynamoDB pages, stopping as soon as `limit` matching points are collected to conserve RCUs and memory. When `sort=True`, all matching candidates within the radius must be evaluated and sorted by distance before slicing pages.

---

## Examples

Runnable scripts are also available in the [`examples/`](https://github.com/Sigm0oid/dynamodb-geo.py/tree/master/examples) directory.

### Example 1: Store Locator — Nearest Open Coffee Shops Within 2 km

Seed multiple locations and query only **open** shops within a 2 km radius, ordered nearest-first:

```python
import uuid
import boto3
import dynamodbgeo

dynamodb = boto3.resource("dynamodb", endpoint_url="http://localhost:8000", region_name="local")
config = dynamodbgeo.GeoDataManagerConfiguration("coffee_shops", dynamodb)
config.hashKeyLength = 5  # Good fit for ~1-5 km neighborhood searches

table_util = dynamodbgeo.GeoTableUtil(config)
table_util.create_table()

geo = dynamodbgeo.GeoDataManager(config)

shops = [
    ("Blue Bottle Ferry Building", 37.7955, -122.3937, True, 4.7),
    ("Sightglass SoMa", 37.7771, -122.4084, True, 4.6),
    ("Ritual Coffee Valencia", 37.7565, -122.4212, False, 4.5),  # closed
    ("Philz Embarcadero", 37.7999, -122.3982, True, 4.8),
]

for name, lat, lng, is_open, rating in shops:
    geo.put_Point(
        dynamodbgeo.PutPointInput(
            dynamodbgeo.GeoPoint(lat, lng),
            str(uuid.uuid4()),
            {
                "Item": {
                    "name": name,
                    "is_open": is_open,
                    "rating": str(rating),
                }
            },
        )
    )

# Search within 2,000m of Montgomery Station (37.7894, -122.4013), open shops only, nearest first
results = geo.queryRadius(
    dynamodbgeo.QueryRadiusRequest(
        dynamodbgeo.GeoPoint(37.7894, -122.4013),
        2000,
        {
            "FilterExpression": "is_open = :open",
            "ExpressionAttributeValues": {":open": True},
        },
        sort=True,
    )
)

for shop in results:
    print(f"{shop['name']} ({shop['geoJson']}) - rating {shop['rating']}")
```

### Example 2: Map Viewport Bounding-Box API with Cursor Pagination & Projection

Back an interactive web/mobile map (`SW` / `NE` bounds) while projecting only lightweight marker attributes and paginating with `next_token`:

```python
import dynamodbgeo


def list_viewport_markers(
    geo: dynamodbgeo.GeoDataManager,
    sw_lat: float,
    sw_lng: float,
    ne_lat: float,
    ne_lng: float,
    page_size: int = 50,
    cursor: str = None,
) -> dict:
    """Return one page of map markers inside the visible bounding box."""
    request = dynamodbgeo.QueryRectangleRequest(
        dynamodbgeo.GeoPoint(sw_lat, sw_lng),
        dynamodbgeo.GeoPoint(ne_lat, ne_lng),
        {
            # Always include geoJson so post-filtering can verify exact bounds
            "ProjectionExpression": "rangeKey, geoJson, #n, category",
            "ExpressionAttributeNames": {"#n": "name"},
        },
    )
    page = geo.queryRectanglePaginated(request, limit=page_size, next_token=cursor)
    return {
        "markers": page["Items"],
        "next_cursor": page["NextToken"],
    }
```

### Example 3: Updating a Moving Entity's Coordinates (Courier / Vehicle Tracking)

Because `hashKey` and `geohash` are derived from a point's coordinates, moving an entity to a new location is performed by deleting the previous coordinate record and inserting the updated one under the same `RangeKeyValue`:

```python
import dynamodbgeo


def move_courier(
    geo: dynamodbgeo.GeoDataManager,
    courier_id: str,
    old_point: dynamodbgeo.GeoPoint,
    new_point: dynamodbgeo.GeoPoint,
    attributes: dict,
):
    geo.delete_Point(dynamodbgeo.DeleteItemInput(old_point, courier_id))
    return geo.put_Point(
        dynamodbgeo.PutPointInput(
            new_point,
            courier_id,
            {"Item": attributes},
        )
    )
```

---

## Choosing `hashKeyLength` (Performance & Cost Tuning)

`hashKeyLength` controls how many leading base-10 digits of the 64-bit S2 geohash are used as the DynamoDB partition key (`hashKey`).

- **Too small** (e.g., `1`–`2` for dense local queries): Fewer queries are dispatched per search, but each partition holds a very large geographic region, consuming more RCUs and discarding more out-of-bounds items during post-filtering.
- **Too large** (e.g., `7+` for wide radius searches): Data spreads evenly across DynamoDB partitions, but wide box/radius searches span many `hashKey` prefixes and trigger many individual `Query` calls.

As a rule of thumb, choose the **largest `hashKeyLength` that keeps query fan-out reasonable for your typical search radius**:

| Typical Search Radius | Suggested `hashKeyLength` |
| :--- | :--- |
| ~100 km+ (regional) | `2` – `3` |
| ~10 km (city-wide) | `4` – `5` |
| ~1 km or less (neighborhood) | `5` – `6` |

See the [hashKeyLength benchmarks from dynamodb-geo.js][hashkeylength-tests] for detailed measurements across radii.

> **Cross-language compatibility:** The [Java `awslabs/dynamodb-geo` library][dynamodb-geo] defaults to `hashKeyLength = 6`, whereas `dynamodbgeo` defaults to `hashKeyLength = 2`. Set `config.hashKeyLength` explicitly if sharing a table across runtimes. Changing `hashKeyLength` later requires re-creating/re-indexing your items.

---

## Configuration Reference

Modify these attributes on your `GeoDataManagerConfiguration` instance before creating tables or running queries:

| Property | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `tableName` | `str` | *(required)* | Target DynamoDB table name. |
| `dynamodbResource` | `ServiceResource` | *(required)* | `boto3.resource("dynamodb", ...)` instance. |
| `hashKeyLength` | `int` | `2` | Number of leading digits of `geohash` used for `hashKey`. |
| `hashKeyAttributeName` | `str` | `"hashKey"` | Partition key attribute name (`N`). |
| `rangeKeyAttributeName` | `str` | `"rangeKey"` | Sort key attribute name (`S`), supplied per item by caller. |
| `geohashAttributeName` | `str` | `"geohash"` | Full 64-bit S2 geohash attribute name (`N`). |
| `geoJsonAttributeName` | `str` | `"geoJson"` | Coordinate attribute name (`S`), stored as `"<latitude>,<longitude>"`. |
| `geohashIndexName` | `str` | `"geohash-index"` | Local Secondary Index name over `(hashKey, geohash)`. |

---

## Upgrading from `0.0.3` to `0.0.4+`

- **Use `boto3.resource` instead of `boto3.client`:** Pass `boto3.resource("dynamodb", ...)` to `GeoDataManagerConfiguration`. Both `GeoDataManagerConfiguration(table_name, dynamodb)` and `GeoDataManagerConfiguration(dynamodb, table_name)` are accepted.
- **Native Python attribute values:** Item fields and `ExpressionAttributeValues` now use high-level `boto3.resource` types (`"Tunisia"`, `123`, `Decimal("1.5")`) rather than low-level wire-format dicts (`{"S": "Tunisia"}`).

---

## Known Limitations

- **No composite partition keys:** Filtering by category (e.g., restaurant vs. coffee shop) uses DynamoDB `FilterExpression` after reading candidate geohash cells, or separate tables per high-cardinality partition.
- **Post-filtering RCU overhead:** DynamoDB calculates RCU consumption based on all items scanned in the intersecting S2 geohash cells before exact circle/rectangle post-filtering removes false positives near cell boundaries.
- **Precision:** The 64-bit S2 cell ID provides roughly centimeter-level spatial resolution on Earth.

---

## Local Development & Running Tests

Start [DynamoDB Local][dynamodb-local] on port `8000` using Docker (or Homebrew on macOS):

```bash
# Via Docker (Linux / macOS / Windows)
docker run --rm -p 8000:8000 amazon/dynamodb-local

# Or on macOS via Homebrew
brew install --cask dynamodb-local
dynamodb-local
```

Install dependencies and run the test suite:

```bash
pip install -r requirements.txt pytest
pip install -e .
pytest -v
```

---

## License

Released under the [MIT License](LICENSE).

[dynamodb-geo]: https://github.com/awslabs/dynamodb-geo
[dynamodb]: https://aws.amazon.com/dynamodb/
[dynamodb-local]: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html
[s2geometry]: https://s2geometry.io/
[createtable]: https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_CreateTable.html
[putitem]: https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_PutItem.html
[updateitem]: https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_UpdateItem.html
[deleteitem]: https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_DeleteItem.html
[dynamodb-query]: https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_Query.html
[hashkeylength-tests]: https://github.com/rh389/dynamodb-geo.js/blob/master/test/integration/hashKeyLength.ts
