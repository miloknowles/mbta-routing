import unittest

from utils.routing import find_coarse_route, preprocess_find_coarse_route
from utils.utils import *


# Just do this once and use cached results.
_ROUTES_CONTAINING_STOP = preprocess_find_coarse_route()

class RoutingTest(unittest.TestCase):
  def test_red_to_green_C(self):
    """
    If A and B are on the same line, should return just that one.
    """
    S = find_coarse_route("Kendall/MIT", "Boston College", _ROUTES_CONTAINING_STOP)
    print_coarse_route(S, "Kendall/MIT", "Boston College")
