import pickle, os
from collections import defaultdict, deque, namedtuple
from itertools import combinations

from utils.mbta_api import get_routes, get_stops
from utils.utils import *


ROUTE_LONGNAME_TO_ID = {
  "Blue Line": "Blue",
  "Green Line B": "Green-B",
  "Green Line C": "Green-C",
  "Green Line D": "Green-D",
  "Green Line E": "Green-E",
  "Mattapan Trolley": "Mattapan",
  "Orange Line": "Orange",
  "Red Line": "Red"
}


# Represents a transfer from one route to another.
# "name" is the long_name of the route being travelled.
# "parent_node" points to the previous route (None if this the first route).
# "connect_stop" is the name of the stop where the transfer to this route occurred.
RouteNode = namedtuple("RouteNode", ["name", "parent_node", "connect_stop"])


def preprocess_nominal(allow_cache=True):
  """
  Builds a dictionary that maps the name of each stop to the names of routes that service it.

  allow_cache (bool) : If True, will try to load precomputed results. If the cache is unavailable,
                       will compute the data structure and save it.
  """
  path_to_output = os.path.abspath(os.path.join(os.path.abspath(__file__), "../../output/"))
  path_to_save = os.path.join(path_to_output, "routes_containing_stop_nominal.pkl")

  if os.path.exists(path_to_save) and allow_cache:
    with open(path_to_save, "rb") as f:
      return pickle.load(f)

  routes_containing_stop = defaultdict(lambda: set())

  for (route_name, route_id) in ROUTE_LONGNAME_TO_ID.items():
    success, stops_json = get_stops([route_id], sort_by="name", descending=False)
    if not success:
      print("Error during API call:", stops_json)
    stop_names = strip_attributes(stops_json, "/attributes/name")
    for stop_name in stop_names:
      routes_containing_stop[stop_name].add(route_name)

  if allow_cache:
    with open(path_to_save, "wb") as f:
      f.write(pickle.dumps(dict(routes_containing_stop)))

  return routes_containing_stop


def check_covid_shutdown(stop_name):
  for word in stop_name.split(" "):
    if word[0].upper() in "COVID":
      return True
  return False


def preprocess_covid(allow_cache=True):
  path_to_output = os.path.abspath(os.path.join(os.path.abspath(__file__), "../../output/"))
  path_to_save = os.path.join(path_to_output, "routes_containing_stop_covid.pkl")

  if os.path.exists(path_to_save) and allow_cache:
    with open(path_to_save, "rb") as f:
      return pickle.load(f)

  # Get an ordered list of stops for each route.
  ordered_stop_names = {}
  for (route_name, route_id) in ROUTE_LONGNAME_TO_ID.items():
    # NOTE: Important to sort_by None here, so that the ordering of stops is preserved.
    success, stops_json = get_stops([route_id], sort_by=None, descending=False)
    if not success:
      print("Error during API call:", stops_json)
    ordered_stop_names[route_name] = strip_attributes(stops_json, "/attributes/name")

  # Find connected components along each route - each route will be broken into
  # segments due to closures.
  routes_containing_stop = defaultdict(lambda: set())
  for route_name, stop_names in ordered_stop_names.items():
    components = [[]]
    for stop in stop_names:
      is_shutdown = check_covid_shutdown(stop)
      if is_shutdown: # If this stop is shutdown, start a new component.
        if len(components[-1]) > 0:
          components.append([])
      else: # Otherwise, keep adding stops to the current component.
        components[-1].append(stop)

    # Create a new route name for each componenent (i.e Green-B-0).
    for cmp_id, cmp_stops in enumerate(components):
      for stop in cmp_stops:
        routes_containing_stop[stop].add("{}-{}".format(route_name, cmp_id))

  # NOTE: The Red Line split (Ashmont branch and Braintree branch) cause problems here,
  # since the linear ordering of stops doesn't reflect connectivity. As a workaround, make
  # sure that both branches on the same route as JFK/UMass.
  jfk_umass_route = list(routes_containing_stop["JFK/UMass"])[0]
  for stop in ["Savin Hill", "North Quincy", "Wollaston"]:
    routes_containing_stop[stop].add(jfk_umass_route)

  if allow_cache:
    with open(path_to_save, "wb") as f:
      f.write(pickle.dumps(dict(routes_containing_stop)))

  return routes_containing_stop


def find_coarse_route(stop_A, stop_B, routes_containing_stop):
  """
  Finds an ordered list of routes that someone could take to go from stop_A to stop_B.

  Uses a graph representation where routes are nodes, and edges are shared stops where
  you could transfer from one route to the other.
  """
  # Adjacency list where node (route) maps to a set of other nodes that it can connect to.
  adjacent = defaultdict(lambda: set())

  # Easy case #0 (COVID): If stop_A or stop_B are no longer operating, return failure.
  if stop_A not in routes_containing_stop or stop_B not in routes_containing_stop:
    print("WARNING: one of {} or {} is either invalid or closed due to COVID".format(stop_A, stop_B))
    return False, []

  possible_routes_A = routes_containing_stop[stop_A] # Possible routes to start on.
  possible_routes_B = routes_containing_stop[stop_B] # Possible routes to end on.

  # Build the graph: for each pair of nodes (routes), add an edge if they share a stop.
  for stop in routes_containing_stop:
    if len(routes_containing_stop[stop]) > 1:
      route_pairs = list(combinations(routes_containing_stop[stop], r=2))
      for (route_i, route_j) in route_pairs:
        adjacent[route_i].add((route_j, stop))
        adjacent[route_j].add((route_i, stop))

  # Easy case #1: stop_A and stop_B are the same.
  if stop_A == stop_B:
    return True, []

  # Easy case #2: If stop_A and stop_B are on the same route already, return that one.
  if len(possible_routes_A.intersection(possible_routes_B)) > 0:
    shared_route = possible_routes_A.intersection(possible_routes_B).pop()
    return True, [RouteNode(name=shared_route, parent_node=None, connect_stop=stop_A)]

  # Otherwise, do BFS to find the path with the minimum # of transfers.
  frontier = deque([RouteNode(name=name, parent_node=None, connect_stop=stop_A) for name in possible_routes_A])
  explored = possible_routes_A.copy()

  while len(frontier) > 0:
    node = frontier.pop()
    explored.add(node.name)

    # If any route that contains the goal is explored, done.
    if node.name in possible_routes_B:
      break

    # Add all adjacent routes that haven't been explored yet.
    for other_name, connect_stop in adjacent[node.name]:
      if other_name not in explored:
        frontier.appendleft(RouteNode(name=other_name, parent_node=node, connect_stop=connect_stop))

  # Trace back parent points to reconstruction sequence, then reverse order.
  did_find_route = (node.name in possible_routes_B)

  sequence = [node]
  while node.parent_node is not None:
    node = node.parent_node
    sequence.append(node)
  sequence.reverse()

  return did_find_route, sequence
