import unittest, json

from mbta_api import *
from utils import print_json


class MbtaApiTest(unittest.TestCase):
  def test_get_routes_lightheavy_asc(self):
    """
    Queries all "Light" and "Heavy" rail routes, sorted by ascending long name.
    """
    success, routes_json = get_routes(route_types=[0, 1], sort_by="long_name", descending=False)
    self.assertTrue(success)

    # NOTE: Because our query is sorted (ascending) by long_name, it will always be in this order.
    long_names_actual = strip_attributes(routes_json, "/attributes/long_name")
    long_names_expected = ['Blue Line', 'Green Line B', 'Green Line C', 'Green Line D',
                           'Green Line E', 'Mattapan Trolley', 'Orange Line', 'Red Line']
    self.assertEqual(long_names_actual, long_names_expected)

  def test_get_routes_lightheavy_desc(self):
    """
    Queries all "Light" and "Heavy" rail routes, sorted by descending long name.
    """
    success, routes_json = get_routes(route_types=[0, 1], sort_by="long_name", descending=True)
    self.assertTrue(success)

    long_names_actual = strip_attributes(routes_json, "/attributes/long_name")
    long_names_expected = ['Blue Line', 'Green Line B', 'Green Line C', 'Green Line D',
                           'Green Line E', 'Mattapan Trolley', 'Orange Line', 'Red Line']
    long_names_expected.reverse()
    self.assertEqual(long_names_actual, long_names_expected)

  def test_get_routes_all(self):
    """
    Get routes across all types (should be a slow query).
    """
    success, _ = get_routes(route_types=[], sort_by="long_name", descending=False)
    self.assertTrue(success)
    success, _ = get_routes(route_types=None, sort_by="long_name", descending=False)
    self.assertTrue(success)

  def test_get_stops_for_route(self):
    """
    Get all of the stops along the "Blue" line.
    """
    success, stops_json = get_stops(["Blue"], sort_by="name", descending=False)
    stop_names_actual = strip_attributes(stops_json, "/attributes/name")
    self.assertTrue(success)

    stop_names_expected = [
        'Airport', 'Aquarium', 'Beachmont', 'Bowdoin', 'Government Center', 'Maverick',
        'Orient Heights', 'Revere Beach', 'State', 'Suffolk Downs', 'Wonderland', 'Wood Island']
    self.assertEqual(stop_names_actual, stop_names_expected)


if __name__ == "__main__":
  unittest.main()
