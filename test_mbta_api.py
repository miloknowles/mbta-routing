import unittest, json

from mbta_api import get_routes, parse_get_routes_json
from utils import print_json


class MbtaApiTest(unittest.TestCase):
  def test_get_routes_lightheavy(self):
    """
    Nominal request (based on the coding challenge description), queries all "Light" and "Heavy"
    rail routes. As of (7/2/2020) there are (3) lines running, although this test may break when
    the Green Line reopens.
    """
    success, routes_json = get_routes(route_types=["0", "1"], sort_by="long_name", descending=False)
    self.assertTrue(success)

    # NOTE: Because our query is sorted (ascending) by long_name, it will always be in this order.
    long_names = parse_get_routes_json(routes_json)
    self.assertEqual(long_names, ["Blue Line", "Orange Line", "Red Line"])

    # Try a descending request.
    success, routes_json = get_routes(route_types=["0", "1"], sort_by="long_name", descending=True)
    self.assertTrue(success)
    long_names = parse_get_routes_json(routes_json)
    self.assertEqual(long_names, ["Red Line", "Orange Line", "Blue Line"])

  def test_get_routes_alltypes(self):
    """
    If [] or None is passed in for route_types, all route types should be returned (slow query).
    """
    success, _ = get_routes(route_types=[], sort_by="long_name", descending=False)
    self.assertTrue(success)
    success, _ = get_routes(route_types=None, sort_by="long_name", descending=False)
    self.assertTrue(success)


if __name__ == "__main__":
  unittest.main()
