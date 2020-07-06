# stop ==> line(s) its on
# nodes are connections between lines
# returns a coarse list of ordered lines

# figure out which line the input is on (could be multiple)
# figure out which line the output is on (could be multiple)

# for input/output line pair:
  # find_line_path(input, output)

# return candidates

from collections import defaultdict, deque, namedtuple
from itertools import combinations
import pickle, os

from utils.mbta_api import get_routes, get_stops
from utils.utils import *


RouteNode = namedtuple("RouteNode", ["name", "parent_node", "connect_stop"])


def preprocess_find_coarse_route(allow_cache=True):
  """
  Builds a dictionary that maps the name of each stop to the names of routes that service it.

  allow_cache (bool) : If True, will try to load precomputed results. If the cache is unavailable,
                       will compute the data structure and save it.
  """
  path_to_output = os.path.abspath(os.path.join(os.path.abspath(__file__), "../../output/"))
  path_to_save = os.path.join(path_to_output, "routes_containing_stop.pkl")

  if os.path.exists(path_to_save) and allow_cache:
    with open(path_to_save, "rb") as f:
      return pickle.load(f)

  route_name_to_id = {
    "Blue Line": "Blue",
    "Green Line B": "Green-B",
    "Green Line C": "Green-C",
    "Green Line D": "Green-D",
    "Green Line E": "Green-E",
    "Mattapan Trolley": "Mattapan",
    "Orange Line": "Orange",
    "Red Line": "Red"
  }

  routes_containing_stop = defaultdict(lambda: set())

  for (route_name, route_id) in route_name_to_id.items():
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


def find_coarse_route(stop_A, stop_B, routes_containing_stop):
  """
  Finds an ordered list of routes that someone could take to go from stop_A to stop_B.

  Uses a graph representation where routes are nodes, and edges are shared stops where
  you could transfer from one route to the other.
  """
  # Adjacency list where node (route) maps to a set of other nodes that it can connect to.
  adjacent = defaultdict(lambda: set())

  possible_routes_A = routes_containing_stop[stop_A] # Possible routes to start on.
  possible_routes_B = routes_containing_stop[stop_B] # Possible routes to end on.

  # Build the graph: for each pair of nodes (routes), add an edge if they share a stop.
  for stop in routes_containing_stop:
    if len(routes_containing_stop[stop]) > 1:
      route_pairs = list(combinations(routes_containing_stop[stop], r=2))
      for (route_i, route_j) in route_pairs:
        adjacent[route_i].add((route_j, stop))
        adjacent[route_j].add((route_i, stop))

  # Easy case: If stop_A and stop_B are on the same route already, return that one.
  if len(possible_routes_A.intersection(possible_routes_B)) > 0:
    shared_route = possible_routes_A.intersection(possible_routes_B).pop()
    return [RouteNode(name=shared_route, parent_node=None, connect_stop=stop_A)]

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
  sequence = [node]
  while node.parent_node is not None:
    node = node.parent_node
    sequence.append(node)
  sequence.reverse()

  return sequence
