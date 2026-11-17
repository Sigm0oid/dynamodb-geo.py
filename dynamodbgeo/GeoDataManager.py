"""
Purpose: A wrapper on the top of DynamoDBManager for performing CRUD operation on our DynamoBD table
"""
import base64
from decimal import Decimal
import json

from DynamoDBManager import DynamoDBManager
from model import Covering
from s2 import *
from s2sphere import LatLng as S2LatLng
EARTH_RADIUS_METERS = 6367000.0


def _token_json_default(obj):
    if isinstance(obj, Decimal):
        return {"__decimal__": str(obj)}
    if isinstance(obj, set):
        return {"__set__": list(obj)}
    if isinstance(obj, (bytes, bytearray)):
        return {"__bytes__": base64.b64encode(bytes(obj)).decode("ascii")}
    if hasattr(obj, "value") and isinstance(getattr(obj, "value"), (bytes, bytearray)):
        # Handles boto3.dynamodb.types.Binary without requiring boto3 import here
        return {"__bytes__": base64.b64encode(bytes(obj.value)).decode("ascii")}
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def _token_json_object_hook(data):
    if len(data) == 1:
        if "__decimal__" in data:
            return Decimal(data["__decimal__"])
        if "__set__" in data:
            return set(data["__set__"])
        if "__bytes__" in data:
            return base64.b64decode(data["__bytes__"].encode("ascii"))
    return data


def _encode_pagination_token(payload: dict) -> str:
    raw = json.dumps(payload, default=_token_json_default, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii")


def _decode_pagination_token(token: str) -> dict:
    try:
        raw = base64.urlsafe_b64decode(token.encode("ascii"))
        decoded = json.loads(raw.decode("utf-8"), object_hook=_token_json_object_hook)
        if not isinstance(decoded, dict):
            raise ValueError("Invalid pagination token")
        return decoded
    except Exception as exc:
        raise ValueError("Invalid pagination token") from exc


class GeoDataManager:

    def __init__(self, config):
        self.config = config
        self.dynamoDBManager = DynamoDBManager(config)

    def put_Point(self, putPointInput):
        return self.dynamoDBManager.put_Point(putPointInput)

    def get_Point(self, getPointInput: 'getPointInput'):
        return self.dynamoDBManager.get_Point(getPointInput)

    def update_Point(self, UpdateItemInput: 'UpdateItemInput'):
        return self.dynamoDBManager.update_Point(UpdateItemInput)

    def delete_Point(self, DeleteItemInput: 'DeleteItemInput'):
        return self.dynamoDBManager.delete_Point(DeleteItemInput)

    def _itemLatLng(self, item: dict) -> S2LatLng:
        geoJson = item[self.config.geoJsonAttributeName]
        coordinates = geoJson.split(",")
        latitude = float(coordinates[0])
        longitude = float(coordinates[1])
        return S2LatLng.from_degrees(latitude, longitude)

    def dispatchQueries(self, covering: 'Covering', geoQueryInput: 'GeoQueryInput'):
        """
        Generating multiple query from the covering area and running query on the DynamoDB table
        """
        ranges = covering.getGeoHashRanges(self.config.hashKeyLength)
        results = []
        for range in ranges:
            hashKey = S2Manager().generateHashKey(range.rangeMin, self.config.hashKeyLength)
            results.extend(self.dynamoDBManager.queryGeohash(
                geoQueryInput.QueryInput, hashKey, range))
        return results

    def _paginateCovering(self, covering: 'Covering', geoQueryInput: 'GeoQueryInput', predicate_fn, limit: int, next_token: str = None):
        if limit is None or not isinstance(limit, int) or isinstance(limit, bool) or limit <= 0:
            raise ValueError("limit must be a positive integer")

        ranges = covering.getGeoHashRanges(self.config.hashKeyLength)
        range_index = 0
        exclusive_start_key = None
        buffer = []

        if next_token is not None:
            token_data = _decode_pagination_token(next_token)
            if token_data.get("mode") != "stream":
                raise ValueError("Pagination token mode does not match query configuration")
            range_index = token_data.get("range_index", 0)
            if not isinstance(range_index, int) or range_index < 0:
                raise ValueError("Invalid pagination token")
            exclusive_start_key = token_data.get("exclusive_start_key")
            buffer = list(token_data.get("buffer") or [])

        if len(buffer) > limit:
            items = buffer[:limit]
            remaining = buffer[limit:]
            token = _encode_pagination_token({
                "mode": "stream",
                "range_index": range_index,
                "exclusive_start_key": exclusive_start_key,
                "buffer": remaining,
            })
            return {"Items": items, "NextToken": token}

        collected = buffer
        if len(collected) == limit:
            has_more = (exclusive_start_key is not None) or (range_index < len(ranges))
            token = (
                _encode_pagination_token({
                    "mode": "stream",
                    "range_index": range_index,
                    "exclusive_start_key": exclusive_start_key,
                })
                if has_more
                else None
            )
            return {"Items": collected, "NextToken": token}

        while range_index < len(ranges):
            current_range = ranges[range_index]
            hash_key = S2Manager().generateHashKey(
                current_range.rangeMin, self.config.hashKeyLength
            )
            raw_items, lek = self.dynamoDBManager.queryGeohashPage(
                geoQueryInput.QueryInput,
                hash_key,
                current_range,
                exclusiveStartKey=exclusive_start_key,
            )

            for idx, item in enumerate(raw_items):
                if predicate_fn(item):
                    collected.append(item)
                    if len(collected) == limit:
                        leftover = [
                            candidate for candidate in raw_items[idx + 1:]
                            if predicate_fn(candidate)
                        ]
                        if lek is not None:
                            next_range_idx = range_index
                            next_esk = lek
                        else:
                            next_range_idx = range_index + 1
                            next_esk = None

                        has_more = bool(leftover) or (next_esk is not None) or (next_range_idx < len(ranges))
                        if not has_more:
                            return {"Items": collected, "NextToken": None}

                        payload = {
                            "mode": "stream",
                            "range_index": next_range_idx,
                            "exclusive_start_key": next_esk,
                        }
                        if leftover:
                            payload["buffer"] = leftover
                        return {"Items": collected, "NextToken": _encode_pagination_token(payload)}

            if lek is not None:
                exclusive_start_key = lek
            else:
                exclusive_start_key = None
                range_index += 1

        return {"Items": collected, "NextToken": None}

    def queryRectangle(self, QueryRectangleInput: 'QueryRectangleRequest'):
        latLngRect = S2Util().latLngRectFromQueryRectangleInput(
            QueryRectangleInput)

        covering = Covering(
            self.config.S2RegionCoverer().get_covering(latLngRect))
        results = self.dispatchQueries(covering, QueryRectangleInput)
        return self.filterByRectangle(results, QueryRectangleInput)

    def queryRectanglePaginated(self, QueryRectangleInput: 'QueryRectangleRequest', limit: int, next_token: str = None):
        """
        Execute a paginated rectangular query, returning {'Items': [...], 'NextToken': str | None}.
        """
        latLngRect = S2Util().latLngRectFromQueryRectangleInput(
            QueryRectangleInput)
        covering = Covering(
            self.config.S2RegionCoverer().get_covering(latLngRect))
        return self._paginateCovering(
            covering,
            QueryRectangleInput,
            lambda item: latLngRect.contains(self._itemLatLng(item)),
            limit=limit,
            next_token=next_token,
        )

    def queryRadius(self, QueryRadiusInput: 'QueryRadiusRequest'):
        latLngRect = S2Util().getBoundingLatLngRectFromQueryRadiusInput(
            QueryRadiusInput)
        covering = Covering(
            self.config.S2RegionCoverer().get_covering(latLngRect))
        results = self.dispatchQueries(covering, QueryRadiusInput)
        filtered_results = self.filterByRadius(results, QueryRadiusInput)
        if QueryRadiusInput.sort == True:
            # Tuples list (distance to the center point, the point data returned from dynamoDB)
            tuples = []
            centerLatLng = S2LatLng.from_degrees(QueryRadiusInput.getCenterPoint(
            ).getLatitude(), QueryRadiusInput.getCenterPoint().getLongitude())
            for item in filtered_results:
                latLng = self._itemLatLng(item)
                tuples.append((centerLatLng.get_distance(
                    latLng).radians * EARTH_RADIUS_METERS, item))
            # Sort the list by distance (x [0] is the distance)
            tuples.sort(key=lambda x: x[0])
            return [item[1] for item in tuples]
        else:
            return filtered_results

    def queryRadiusPaginated(self, QueryRadiusInput: 'QueryRadiusRequest', limit: int, next_token: str = None):
        """
        Execute a paginated radius query, returning {'Items': [...], 'NextToken': str | None}.
        When sort=False (default), streams across S2 ranges/DynamoDB pages and stops once `limit` items are found.
        When sort=True, evaluates and distance-sorts all matching items in the radius and slices by cursor offset.
        """
        if limit is None or not isinstance(limit, int) or isinstance(limit, bool) or limit <= 0:
            raise ValueError("limit must be a positive integer")

        if QueryRadiusInput.sort == True:
            offset = 0
            if next_token is not None:
                token_data = _decode_pagination_token(next_token)
                if token_data.get("mode") != "sorted":
                    raise ValueError("Pagination token mode does not match query configuration")
                offset = token_data.get("offset", 0)
                if not isinstance(offset, int) or offset < 0:
                    raise ValueError("Invalid pagination token")
            sorted_items = self.queryRadius(QueryRadiusInput)
            page_items = sorted_items[offset:offset + limit]
            next_offset = offset + limit
            token = (
                _encode_pagination_token({"mode": "sorted", "offset": next_offset})
                if next_offset < len(sorted_items)
                else None
            )
            return {"Items": page_items, "NextToken": token}

        latLngRect = S2Util().getBoundingLatLngRectFromQueryRadiusInput(
            QueryRadiusInput)
        covering = Covering(
            self.config.S2RegionCoverer().get_covering(latLngRect))
        centerLatLng = S2LatLng.from_degrees(
            QueryRadiusInput.getCenterPoint().getLatitude(),
            QueryRadiusInput.getCenterPoint().getLongitude(),
        )
        radiusInMeter = QueryRadiusInput.getRadiusInMeter()
        return self._paginateCovering(
            covering,
            QueryRadiusInput,
            lambda item: centerLatLng.get_distance(self._itemLatLng(item)).radians * EARTH_RADIUS_METERS <= radiusInMeter,
            limit=limit,
            next_token=next_token,
        )

    def filterByRadius(self, ItemList: 'points retrieved from dynamoDB', QueryRadiusInput: 'QueryRadiusRequest'):
        centerLatLng = S2LatLng.from_degrees(QueryRadiusInput.getCenterPoint(
        ).getLatitude(), QueryRadiusInput.getCenterPoint().getLongitude())
        radiusInMeter = QueryRadiusInput.getRadiusInMeter()
        result = []
        for item in ItemList:
            latLng = self._itemLatLng(item)
            if centerLatLng.get_distance(latLng).radians * EARTH_RADIUS_METERS <= radiusInMeter:
                result.append(item)
        return result

    def filterByRectangle(self, ItemList: 'points retrieved from dynamoDB', QueryRectangleInput: 'QueryRectangleRequest'):
        latLngRect = S2Util().latLngRectFromQueryRectangleInput(
            QueryRectangleInput)
        result = []
        for item in ItemList:
            latLng = self._itemLatLng(item)
            if latLngRect.contains(latLng):
                result.append(item)
        return result
