"""
Example: Seed coffee shop locations in DynamoDB Local and query open shops
within a 2 km radius sorted from nearest to farthest.

Prerequisites:
    docker run --rm -p 8000:8000 amazon/dynamodb-local
"""
import uuid
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

    config = dynamodbgeo.GeoDataManagerConfiguration("coffee_shops_demo", dynamodb)
    config.hashKeyLength = 5

    table_util = dynamodbgeo.GeoTableUtil(config)
    table_util.create_table()

    geo = dynamodbgeo.GeoDataManager(config)

    shops = [
        ("Blue Bottle Ferry Building", 37.7955, -122.3937, True, "4.7"),
        ("Sightglass SoMa", 37.7771, -122.4084, True, "4.6"),
        ("Ritual Coffee Valencia", 37.7565, -122.4212, False, "4.5"),
        ("Philz Embarcadero", 37.7999, -122.3982, True, "4.8"),
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
                        "rating": rating,
                    }
                },
            )
        )

    center = dynamodbgeo.GeoPoint(37.7894, -122.4013)
    nearby_open = geo.queryRadius(
        dynamodbgeo.QueryRadiusRequest(
            center,
            2000,
            {
                "FilterExpression": "is_open = :open",
                "ExpressionAttributeValues": {":open": True},
            },
            sort=True,
        )
    )

    print("Open coffee shops within 2 km (nearest first):")
    for idx, item in enumerate(nearby_open, start=1):
        print(f"  {idx}. {item['name']} @ ({item['geoJson']}) — rating {item['rating']}")

    table_util.delete_table()


if __name__ == "__main__":
    main()
