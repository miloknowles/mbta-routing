import unittest

from utils.routing import *
from utils.utils import *


# Just do this once and use cached results.
_ROUTES_CONTAINING_STOP_NOMINAL = preprocess_nominal(allow_cache=True)
_ROUTES_CONTAINING_STOP_COVID = preprocess_covid(allow_cache=True)


class NominalRoutingTest(unittest.TestCase):
  def test_red_to_green_C(self):
    is_feasible, S = find_coarse_route("Kendall/MIT", "Boston College", _ROUTES_CONTAINING_STOP_NOMINAL)
    print_coarse_route(S, "Kendall/MIT", "Boston College")

    self.assertTrue(is_feasible)

    self.assertEqual(S[0].name, "Red Line")
    self.assertEqual(S[0].parent_node, None)
    self.assertEqual(S[0].connect_stop, "Kendall/MIT")

    self.assertEqual(S[1].name, "Green Line B")
    self.assertEqual(S[1].parent_node.name, "Red Line")
    self.assertEqual(S[1].connect_stop, "Park Street")

  def test_green_C_to_red(self):
    is_feasible, S = find_coarse_route("Boston College", "Kendall/MIT", _ROUTES_CONTAINING_STOP_NOMINAL)
    print_coarse_route(S, "Boston College", "Kendall/MIT")

    self.assertTrue(is_feasible)

    self.assertEqual(S[0].name, "Green Line B")
    self.assertEqual(S[0].parent_node, None)
    self.assertEqual(S[0].connect_stop, "Boston College")

    self.assertEqual(S[1].name, "Red Line")
    self.assertEqual(S[1].parent_node.name, "Green Line B")
    self.assertEqual(S[1].connect_stop, "Park Street")

  def test_mattapan_to_mattapan(self):
    is_feasible, S = find_coarse_route("Valley Road", "Ashmont", _ROUTES_CONTAINING_STOP_NOMINAL)
    print_coarse_route(S, "Valley Road", "Ashmont")

    self.assertTrue(is_feasible)

    self.assertEqual(S[0].name, "Mattapan Trolley")
    self.assertEqual(S[0].parent_node, None)
    self.assertEqual(S[0].connect_stop, "Valley Road")

  def test_same_start_and_end(self):
    is_feasible, S = find_coarse_route("Forest Hills", "Forest Hills", _ROUTES_CONTAINING_STOP_NOMINAL)
    print_coarse_route(S, "Forest Hills", "Forest Hills")

    self.assertTrue(is_feasible)

  def test_blue_green_OR_orange_red(self):
    """
    This test is under-constrained, since you could take
      Blue ==> Green X ==> Red  OR
      Blue ==> Orange ==> Red
    """
    is_feasible, S = find_coarse_route("Revere Beach", "Braintree", _ROUTES_CONTAINING_STOP_NOMINAL)
    print_coarse_route(S, "Reverse Beach", "Braintree")

    self.assertTrue(is_feasible)

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


class CovidRoutingTest(unittest.TestCase):
  def test_red_to_green_C_infeasible(self):
    is_feasible, S = find_coarse_route("Kendall/MIT", "Boston College", _ROUTES_CONTAINING_STOP_COVID)
    self.assertFalse(is_feasible)

  def test_green_C_to_red_infeasible(self):
    is_feasible, S = find_coarse_route("Boston College", "Kendall/MIT", _ROUTES_CONTAINING_STOP_COVID)
    self.assertFalse(is_feasible)

  def test_feasible_01(self):
    is_feasible, S = find_coarse_route("Harvard", "Porter", _ROUTES_CONTAINING_STOP_COVID)
    print_coarse_route(S, "Harvard", "Porter")
    self.assertTrue(is_feasible)

  def test_feasible_02(self):
    is_feasible, S = find_coarse_route("North Station", "Airport", _ROUTES_CONTAINING_STOP_COVID)
    print_coarse_route(S, "North Station", "Airport")
    self.assertTrue(is_feasible)

  def test_feasible_03(self):
    is_feasible, S = find_coarse_route("Wollaston", "South Station", _ROUTES_CONTAINING_STOP_COVID)
    print_coarse_route(S, "Wollaston", "South Station")
    self.assertTrue(is_feasible)
