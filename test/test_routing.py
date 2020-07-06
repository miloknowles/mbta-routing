import unittest

from utils.routing import find_coarse_route, preprocess_find_coarse_route
from utils.utils import *


# Just do this once and use cached results.
_ROUTES_CONTAINING_STOP = preprocess_find_coarse_route()


class RoutingTest(unittest.TestCase):
  def test_red_to_green_C(self):
    S = find_coarse_route("Kendall/MIT", "Boston College", _ROUTES_CONTAINING_STOP)
    print_coarse_route(S, "Kendall/MIT", "Boston College")

    self.assertEqual(S[0].name, "Red Line")
    self.assertEqual(S[0].parent_node, None)
    self.assertEqual(S[0].connect_stop, "Kendall/MIT")

    self.assertEqual(S[1].name, "Green Line B")
    self.assertEqual(S[1].parent_node.name, "Red Line")
    self.assertEqual(S[1].connect_stop, "Park Street")

  def test_green_C_to_red(self):
    S = find_coarse_route("Boston College", "Kendall/MIT", _ROUTES_CONTAINING_STOP)
    print_coarse_route(S, "Boston College", "Kendall/MIT")

    self.assertEqual(S[0].name, "Green Line B")
    self.assertEqual(S[0].parent_node, None)
    self.assertEqual(S[0].connect_stop, "Boston College")

    self.assertEqual(S[1].name, "Red Line")
    self.assertEqual(S[1].parent_node.name, "Green Line B")
    self.assertEqual(S[1].connect_stop, "Park Street")

  def test_mattapan_to_mattapan(self):
    S = find_coarse_route("Valley Road", "Ashmont", _ROUTES_CONTAINING_STOP)
    print_coarse_route(S, "Valley Road", "Ashmont")

    self.assertEqual(S[0].name, "Mattapan Trolley")
    self.assertEqual(S[0].parent_node, None)
    self.assertEqual(S[0].connect_stop, "Valley Road")

  def test_blue_green_OR_orange_red(self):
    """
    This test is under-constrained, since you could take
      Blue ==> Green X ==> Red  OR
      Blue ==> Orange ==> Red
    """
    S = find_coarse_route("Revere Beach", "Braintree", _ROUTES_CONTAINING_STOP)
    print_coarse_route(S, "Reverse Beach", "Braintree")

    self.assertEqual(S[0].name, "Blue Line")
    self.assertEqual(S[0].parent_node, None)
    self.assertEqual(S[0].connect_stop, "Revere Beach")

    self.assertIn(S[1].name, ["Green Line B", "Green Line C", "Green Line D", "Green Line E", "Orange Line"])
    self.assertEqual(S[1].parent_node.name, "Blue Line")

    if "Green Line" in S[1].name:
      self.assertEqual(S[1].connect_stop, "Government Center")
    else:
      self.assertEqual(S[1].connect_stop, "State")

    self.assertEqual(S[2].name, "Red Line")

    if "Green Line" in S[2].parent_node.name:
      self.assertEqual(S[2].connect_stop, "Park Street")
    else:
      self.assertEqual(S[2].connect_stop, "Downtown Crossing")