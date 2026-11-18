"""
Example: Paginate through points inside a map viewport bounding box using
queryRectanglePaginated with limit and next_token.

Prerequisites:
    docker run --rm -p 8000:8000 amazon/dynamodb-local
"""
import boto3
import dynamodbgeo


def main():
    dynamodb = boto3.resource(
        "dynamodb",
        endpoint_url="http://localhost:8000",
        region_name="local",
        aws_access_key_id="test",
        aws_secret_access_key="test",
    )

    config = dynamodbgeo.GeoDataManagerConfiguration("viewport_markers_demo", dynamodb)
    config.hashKeyLength = 4

    table_util = dynamodbgeo.GeoTableUtil(config)
    table_util.create_table()
    geo = dynamodbgeo.GeoDataManager(config)

    # Insert 10 sample landmarks around Tunis
    for i in range(10):
        lat = 36.8750 + i * 0.0010
        lng = 10.2400 + i * 0.0010
        geo.put_Point(
            dynamodbgeo.PutPointInput(
                dynamodbgeo.GeoPoint(lat, lng),
                f"landmark-{i + 1}",
                {"Item": {"name": f"Landmark #{i + 1}", "category": "museum"}},
            )
        )

    request = dynamodbgeo.QueryRectangleRequest(
        dynamodbgeo.GeoPoint(36.8740, 10.2390),  # SW corner
        dynamodbgeo.GeoPoint(36.8860, 10.2520),  # NE corner
        {
            "ProjectionExpression": "rangeKey, geoJson, #n, category",
            "ExpressionAttributeNames": {"#n": "name"},
        },
    )

    page_num = 1
    next_token = None
    while True:
        page = geo.queryRectanglePaginated(request, limit=3, next_token=next_token)
        print(f"Page {page_num}: {[item['name'] for item in page['Items']]}")
        next_token = page["NextToken"]
        if not next_token:
            break
        page_num += 1

    table_util.delete_table()


if __name__ == "__main__":
    main()
