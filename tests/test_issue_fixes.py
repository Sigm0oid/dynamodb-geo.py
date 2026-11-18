from decimal import Decimal
import math
import sys
import types
import unittest
from unittest.mock import MagicMock


def _ensure_stub_dependencies():
    """
    Provide lightweight spherical/boto3 stubs ONLY when optional runtime packages
    are absent in minimal unit-test environments; uses real boto3/s2sphere whenever installed.
    """
    try:
        import boto3  # noqa: F401
    except ImportError:
        boto3_mod = types.ModuleType("boto3")
        dynamodb_mod = types.ModuleType("boto3.dynamodb")
        conditions_mod = types.ModuleType("boto3.dynamodb.conditions")
        conditions_mod.Attr = MagicMock()
        conditions_mod.Key = MagicMock()
        sys.modules["boto3"] = boto3_mod
        sys.modules["boto3.dynamodb"] = dynamodb_mod
        sys.modules["boto3.dynamodb.conditions"] = conditions_mod

    try:
        import s2sphere  # noqa: F401
    except ImportError:
        s2_mod = types.ModuleType("s2sphere")

        class FakeAngle:
            def __init__(self, radians: float):
                self.radians = radians
                self.degrees = math.degrees(radians)

            @classmethod
            def from_radians(cls, rad: float):
                return cls(rad)

            @classmethod
            def from_degrees(cls, deg: float):
                return cls(math.radians(deg))

        class FakeLatLng:
            def __init__(self, lat_deg: float, lng_deg: float):
                self.lat_deg = lat_deg
                self.lng_deg = lng_deg

            @classmethod
            def from_degrees(cls, lat_deg: float, lng_deg: float):
                return cls(lat_deg, lng_deg)

            def to_point(self):
                return (self.lat_deg, self.lng_deg)

            def get_distance(self, other: "FakeLatLng") -> FakeAngle:
                # Haversine central angle in radians
                lat1, lon1 = math.radians(self.lat_deg), math.radians(self.lng_deg)
                lat2, lon2 = math.radians(other.lat_deg), math.radians(other.lng_deg)
                dlat = lat2 - lat1
                dlon = lon2 - lon1
                a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
                return FakeAngle.from_radians(2 * math.asin(min(1.0, math.sqrt(a))))

        class FakeLatLngRect:
            def __init__(self, min_ll: FakeLatLng, max_ll: FakeLatLng):
                self.min_lat = min(min_ll.lat_deg, max_ll.lat_deg)
                self.max_lat = max(min_ll.lat_deg, max_ll.lat_deg)
                self.lng_lo = min_ll.lng_deg
                self.lng_hi = max_ll.lng_deg

            @classmethod
            def from_point_pair(cls, p1: FakeLatLng, p2: FakeLatLng):
                return cls(
                    FakeLatLng(min(p1.lat_deg, p2.lat_deg), min(p1.lng_deg, p2.lng_deg)),
                    FakeLatLng(max(p1.lat_deg, p2.lat_deg), max(p1.lng_deg, p2.lng_deg)),
                )

            def contains(self, ll: FakeLatLng) -> bool:
                if not (self.min_lat <= ll.lat_deg <= self.max_lat):
                    return False
                if self.lng_lo <= self.lng_hi:
                    return self.lng_lo <= ll.lng_deg <= self.lng_hi
                return ll.lng_deg >= self.lng_lo or ll.lng_deg <= self.lng_hi

        class FakeCap:
            def __init__(self, point, angle: FakeAngle):
                self.point = point
                self.angle = angle

            @classmethod
            def from_axis_angle(cls, point, angle: FakeAngle):
                return cls(point, angle)

            def get_rect_bound(self) -> FakeLatLngRect:
                lat_deg, lng_deg = self.point
                dlat = self.angle.degrees
                min_lat = max(-90.0, lat_deg - dlat)
                max_lat = min(90.0, lat_deg + dlat)
                if min_lat <= -90.0 or max_lat >= 90.0:
                    return FakeLatLngRect(FakeLatLng(min_lat, -180.0), FakeLatLng(max_lat, 180.0))
                dlng = dlat / max(math.cos(math.radians(lat_deg)), 1e-6)
                if dlng >= 180.0:
                    return FakeLatLngRect(FakeLatLng(min_lat, -180.0), FakeLatLng(max_lat, 180.0))
                lo = ((lng_deg - dlng + 180.0) % 360.0) - 180.0
                hi = ((lng_deg + dlng + 180.0) % 360.0) - 180.0
                return FakeLatLngRect(FakeLatLng(min_lat, lo), FakeLatLng(max_lat, hi))

        class FakeCellId:
            def __init__(self, val: int, rmin: int = None, rmax: int = None):
                self._val = val
                self._rmin = val if rmin is None else rmin
                self._rmax = val if rmax is None else rmax

            def id(self):
                return self._val

            def range_min(self):
                return FakeCellId(self._rmin)

            def range_max(self):
                return FakeCellId(self._rmax)

        class FakeCell:
            def __init__(self, cell_id: int):
                self._id = FakeCellId(cell_id)

            @classmethod
            def from_lat_lng(cls, ll: FakeLatLng):
                # Deterministic 19-digit positive integer for test coordinates
                scaled = int((ll.lat_deg + 90.0) * 10**7) * 10**9 + int((ll.lng_deg + 180.0) * 10**6)
                return cls(10**18 + abs(scaled))

            def id(self):
                return self._id

        class FakeRegionCoverer:
            def get_covering(self, region):
                return [
                    FakeCellId(1100000000000000000, 1100000000000000000, 1199999999999999999),
                    FakeCellId(1200000000000000000, 1200000000000000000, 1299999999999999999),
                    FakeCellId(1300000000000000000, 1300000000000000000, 1399999999999999999),
                ]

        s2_mod.Angle = FakeAngle
        s2_mod.Cap = FakeCap
        s2_mod.Cell = FakeCell
        s2_mod.CellId = FakeCellId
        s2_mod.LatLng = FakeLatLng
        s2_mod.LatLngRect = FakeLatLngRect
        s2_mod.RegionCoverer = FakeRegionCoverer
        sys.modules["s2sphere"] = s2_mod


_ensure_stub_dependencies()

import dynamodbgeo  # noqa: E402
from dynamodbgeo.model import GeohashRange  # noqa: E402
from dynamodbgeo.s2 import S2Util  # noqa: E402
from dynamodbgeo.util import GeoTableUtil  # noqa: E402


class FakeClientError(Exception):
    def __init__(self, code: str):
        super().__init__(code)
        self.response = {"Error": {"Code": code}}


def _make_config(table_name="geo_test"):
    resource = MagicMock()
    table = MagicMock()
    resource.Table.return_value = table
    config = dynamodbgeo.GeoDataManagerConfiguration(table_name, resource)
    return config, resource, table


class FakeCellIdRange:
    def __init__(self, lo: int, hi: int):
        self._lo = lo
        self._hi = hi

    def range_min(self):
        m = MagicMock()
        m.id.return_value = self._lo
        return m

    def range_max(self):
        m = MagicMock()
        m.id.return_value = self._hi
        return m


class TestOpenIssueFixes(unittest.TestCase):

    def test_issue_50_config_accepts_both_argument_orders(self):
        resource = MagicMock()
        cfg_standard = dynamodbgeo.GeoDataManagerConfiguration("my_table", resource)
        self.assertEqual(cfg_standard.tableName, "my_table")
        self.assertIs(cfg_standard.dynamodbResource, resource)

        cfg_legacy = dynamodbgeo.GeoDataManagerConfiguration(resource, "my_table")
        self.assertEqual(cfg_legacy.tableName, "my_table")
        self.assertIs(cfg_legacy.dynamodbResource, resource)

    def test_issue_50_put_point_forwards_extra_fields_without_mutating_caller(self):
        config, _, table = _make_config()
        manager = dynamodbgeo.GeoDataManager(config)
        put_input_dict = {
            "Item": {"Country": "Tunisia"},
            "ConditionExpression": "attribute_not_exists(hashKey)",
        }

        manager.put_Point(
            dynamodbgeo.PutPointInput(
                dynamodbgeo.GeoPoint(36.879163, 10.243120),
                "rk-1",
                put_input_dict,
            )
        )

        # Caller dict must not be mutated with generated key fields
        self.assertEqual(put_input_dict, {
            "Item": {"Country": "Tunisia"},
            "ConditionExpression": "attribute_not_exists(hashKey)",
        })
        table.put_item.assert_called_once()
        kwargs = table.put_item.call_args.kwargs
        self.assertEqual(kwargs["ConditionExpression"], "attribute_not_exists(hashKey)")
        self.assertEqual(kwargs["Item"]["Country"], "Tunisia")
        self.assertEqual(kwargs["Item"]["rangeKey"], "rk-1")
        self.assertIn("hashKey", kwargs["Item"])
        self.assertIn("geohash", kwargs["Item"])

    def test_issue_43_pagination_does_not_leak_exclusive_start_key_across_ranges(self):
        config, _, table = _make_config()
        gdm = dynamodbgeo.GeoDataManager(config)

        recorded_calls = []

        def fake_query(**kwargs):
            recorded_calls.append(kwargs)
            hk = kwargs["ExpressionAttributeValues"][":hashKey"]
            esk = kwargs.get("ExclusiveStartKey")
            if hk == 11:
                if esk is None:
                    return {
                        "Items": [{"rangeKey": "p1", "geoJson": "36.8785,10.2430"}],
                        "LastEvaluatedKey": {"hashKey": Decimal("11"), "rangeKey": "p1", "geohash": Decimal("1150000000000000000")},
                    }
                return {
                    "Items": [{"rangeKey": "p2", "geoJson": "36.8786,10.2431"}],
                }
            # Second range (hk == 12) MUST NOT receive range 1's ExclusiveStartKey
            if esk is not None:
                raise AssertionError(f"Stale ExclusiveStartKey leaked into next range query: {esk}")
            return {
                "Items": [{"rangeKey": "p3", "geoJson": "36.8787,10.2432"}],
            }

        table.query.side_effect = fake_query
        coverer_instance = MagicMock()
        coverer_instance.get_covering.return_value = [
            FakeCellIdRange(1100000000000000000, 1199999999999999999),
            FakeCellIdRange(1200000000000000000, 1299999999999999999),
        ]
        config.S2RegionCoverer = MagicMock(return_value=coverer_instance)

        caller_query_dict = {
            "ProjectionExpression": "geoJson, hashKey, rangeKey",
            "ExpressionAttributeValues": {":custom": "val"},
        }
        req = dynamodbgeo.QueryRectangleRequest(
            dynamodbgeo.GeoPoint(36.8780, 10.2420),
            dynamodbgeo.GeoPoint(36.8795, 10.2440),
            caller_query_dict,
        )
        items = gdm.queryRectangle(req)

        self.assertEqual([i["rangeKey"] for i in items], ["p1", "p2", "p3"])
        self.assertEqual(len(recorded_calls), 3)
        self.assertNotIn("ExclusiveStartKey", caller_query_dict)
        self.assertEqual(caller_query_dict["ExpressionAttributeValues"], {":custom": "val"})

    def test_issue_43_no_shared_mutable_default_query_dict(self):
        r1 = dynamodbgeo.QueryRadiusRequest(dynamodbgeo.GeoPoint(0.0, 0.0), 100)
        r2 = dynamodbgeo.QueryRadiusRequest(dynamodbgeo.GeoPoint(1.0, 1.0), 100)
        r1.QueryInput["FilterExpression"] = "Country = :c"
        self.assertNotIn("FilterExpression", r2.QueryInput)

    def test_issue_49_streaming_pagination_across_ranges_and_pages(self):
        config, _, table = _make_config()
        gdm = dynamodbgeo.GeoDataManager(config)

        queried_hash_keys = []

        def fake_query(**kwargs):
            hk = kwargs["ExpressionAttributeValues"][":hashKey"]
            esk = kwargs.get("ExclusiveStartKey")
            queried_hash_keys.append((hk, esk))
            if hk == 11:
                if esk is None:
                    return {
                        "Items": [
                            {"rangeKey": "in-1", "geoJson": "36.8785,10.2430", "score": Decimal("1.5"), "tags": {"a"}},
                            {"rangeKey": "out-1", "geoJson": "40.0000,10.2430"},
                        ],
                        "LastEvaluatedKey": {"hashKey": Decimal("11"), "rangeKey": "out-1", "geohash": Decimal("115")},
                    }
                return {
                    "Items": [
                        {"rangeKey": "in-2", "geoJson": "36.8786,10.2431", "score": Decimal("2.5")},
                        {"rangeKey": "in-3", "geoJson": "36.8787,10.2432", "score": Decimal("3.5")},
                    ]
                }
            if hk == 12:
                return {
                    "Items": [
                        {"rangeKey": "in-4", "geoJson": "36.8788,10.2433", "score": Decimal("4.5")},
                    ]
                }
            return {"Items": []}

        table.query.side_effect = fake_query
        coverer_instance = MagicMock()
        coverer_instance.get_covering.return_value = [
            FakeCellIdRange(1100000000000000000, 1199999999999999999),
            FakeCellIdRange(1200000000000000000, 1299999999999999999),
            FakeCellIdRange(1300000000000000000, 1399999999999999999),
        ]
        config.S2RegionCoverer = MagicMock(return_value=coverer_instance)

        req = dynamodbgeo.QueryRectangleRequest(
            dynamodbgeo.GeoPoint(36.8780, 10.2420),
            dynamodbgeo.GeoPoint(36.8795, 10.2440),
        )

        # Page 1 (limit=2): should only touch range hk=11 (2 pages) and NOT query hk=12 or hk=13 yet!
        page1 = gdm.queryRectanglePaginated(req, limit=2)
        self.assertEqual([i["rangeKey"] for i in page1["Items"]], ["in-1", "in-2"])
        self.assertIsNotNone(page1["NextToken"])
        self.assertEqual([hk for hk, _ in queried_hash_keys], [11, 11])

        # Page 2 (limit=2): consumes buffered 'in-3' and queries hk=12 for 'in-4', still without querying hk=13!
        page2 = gdm.queryRectanglePaginated(req, limit=2, next_token=page1["NextToken"])
        self.assertEqual([i["rangeKey"] for i in page2["Items"]], ["in-3", "in-4"])
        self.assertEqual(page2["Items"][0]["score"], Decimal("3.5"))
        self.assertIsNotNone(page2["NextToken"])
        self.assertEqual([hk for hk, _ in queried_hash_keys], [11, 11, 12])

        # Page 3 (limit=2): checks empty hk=13 and terminates with NextToken=None
        page3 = gdm.queryRectanglePaginated(req, limit=2, next_token=page2["NextToken"])
        self.assertEqual(page3["Items"], [])
        self.assertIsNone(page3["NextToken"])

    def test_issue_49_sorted_radius_pagination(self):
        config, _, table = _make_config()
        gdm = dynamodbgeo.GeoDataManager(config)

        table.query.return_value = {
            "Items": [
                {"rangeKey": "far", "geoJson": "36.874617,10.241441"},
                {"rangeKey": "near", "geoJson": "36.874419,10.241062"},
                {"rangeKey": "mid", "geoJson": "36.874507,10.240857"},
            ]
        }
        coverer_instance = MagicMock()
        coverer_instance.get_covering.return_value = [
            FakeCellIdRange(1100000000000000000, 1199999999999999999),
        ]
        config.S2RegionCoverer = MagicMock(return_value=coverer_instance)

        req = dynamodbgeo.QueryRadiusRequest(
            dynamodbgeo.GeoPoint(36.874444, 10.241059),
            95,
            sort=True,
        )
        p1 = gdm.queryRadiusPaginated(req, limit=2)
        self.assertEqual([i["rangeKey"] for i in p1["Items"]], ["near", "mid"])
        self.assertIsNotNone(p1["NextToken"])

        p2 = gdm.queryRadiusPaginated(req, limit=2, next_token=p1["NextToken"])
        self.assertEqual([i["rangeKey"] for i in p2["Items"]], ["far"])
        self.assertIsNone(p2["NextToken"])

    def test_issue_48_s2util_handles_poles_and_antimeridian(self):
        # Antimeridian crossing near New Zealand
        nz_req = dynamodbgeo.QueryRadiusRequest(
            dynamodbgeo.GeoPoint(-42.02055565757218, 172.38910316227407),
            1188035.19116924,
        )
        nz_rect = S2Util().getBoundingLatLngRectFromQueryRadiusInput(nz_req)
        from s2sphere import LatLng
        self.assertTrue(nz_rect.contains(LatLng.from_degrees(-42.0, -179.0)))

        # Exact North Pole (previously ZeroDivisionError)
        pole_req = dynamodbgeo.QueryRadiusRequest(
            dynamodbgeo.GeoPoint(90.0, 0.0),
            10000.0,
        )
        pole_rect = S2Util().getBoundingLatLngRectFromQueryRadiusInput(pole_req)
        self.assertTrue(pole_rect.contains(LatLng.from_degrees(89.95, -135.0)))
        self.assertTrue(pole_rect.contains(LatLng.from_degrees(89.95, 135.0)))

    def test_issue_39_geotableutil_create_and_delete_table(self):
        config, resource, table = _make_config("geo_test")
        util = GeoTableUtil(config)

        # 1. Existing table skips create_table cleanly via meta.client.describe_table
        resource.meta.client.describe_table.return_value = {"Table": {"TableName": "geo_test"}}
        util.create_table()
        resource.create_table.assert_not_called()

        # 2. ResourceNotFoundException triggers table creation
        resource.meta.client.describe_table.side_effect = FakeClientError("ResourceNotFoundException")
        created_table = MagicMock()
        resource.create_table.return_value = created_table
        util.create_table()
        resource.create_table.assert_called_once()
        created_table.wait_until_exists.assert_called_once()

        # 3. Unexpected ClientError is propagated instead of swallowed
        resource.meta.client.describe_table.side_effect = FakeClientError("AccessDeniedException")
        with self.assertRaises(FakeClientError):
            util.create_table()

        # 4. delete_table deletes existing table and waits
        resource.meta.client.describe_table.side_effect = None
        resource.meta.client.describe_table.return_value = {"Table": {"TableName": "geo_test"}}
        util.delete_table()
        table.delete.assert_called_once()
        table.wait_until_not_exists.assert_called_once()

    def test_s2manager_generate_hash_key_64bit_precision(self):
        s2_mgr = dynamodbgeo.S2Manager()
        self.assertEqual(s2_mgr.generateHashKey(1199999999999999999, 2), 11)
        self.assertEqual(s2_mgr.generateHashKey(-1199999999999999999, 2), -11)
        self.assertEqual(s2_mgr.generateHashKey(9223372036854775807, 6), 922337)

    def test_issue_49_rejects_invalid_limit_and_mismatched_token_mode(self):
        config, _, table = _make_config()
        gdm = dynamodbgeo.GeoDataManager(config)
        table.query.return_value = {
            "Items": [
                {"rangeKey": "p1", "geoJson": "36.874419,10.241062"},
                {"rangeKey": "p2", "geoJson": "36.874507,10.240857"},
            ]
        }
        coverer_instance = MagicMock()
        coverer_instance.get_covering.return_value = [
            FakeCellIdRange(1100000000000000000, 1199999999999999999),
        ]
        config.S2RegionCoverer = MagicMock(return_value=coverer_instance)

        sorted_req = dynamodbgeo.QueryRadiusRequest(
            dynamodbgeo.GeoPoint(36.874444, 10.241059), 95, sort=True
        )
        unsorted_req = dynamodbgeo.QueryRadiusRequest(
            dynamodbgeo.GeoPoint(36.874444, 10.241059), 95, sort=False
        )

        with self.assertRaises(ValueError):
            gdm.queryRadiusPaginated(unsorted_req, limit=0)
        with self.assertRaises(ValueError):
            gdm.queryRadiusPaginated(unsorted_req, limit=True)

        sorted_page = gdm.queryRadiusPaginated(sorted_req, limit=1)
        with self.assertRaises(ValueError):
            gdm.queryRadiusPaginated(unsorted_req, limit=1, next_token=sorted_page["NextToken"])

    def test_issue_52_find_packages_excludes_tests(self):
        import setuptools
        packages = setuptools.find_packages(exclude=["tests", "tests.*"])
        self.assertIn("dynamodbgeo", packages)
        self.assertNotIn("tests", packages)
        self.assertFalse(any(pkg.startswith("tests") for pkg in packages))


if __name__ == "__main__":
    unittest.main()
