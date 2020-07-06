import json, os
from jsonpointer import resolve_pointer

from utils.mbta_api import get_routes, get_stops
from utils.utils import *


def problem1_demo():
  """
  Problem 1: Return  a list of the MBTA route "long names".
    - To speed up the API request, I use the filter[type]=0,1 option.
    - Some other configurable options for filtering/sorting are shown in test_mbta_api.py
  """
  print("=====================" * 5)
  success, routes_json = get_routes(route_types=[0, 1], sort_by="long_name", descending=False)

  if success:
    long_names = strip_attributes(routes_json, "/attributes/long_name")
    print("Found {} routes".format(len(long_names)))
    print("Long names:", long_names)
  else:
    print("Error during API request:\n", routes_json)

  print("Done with Problem 1!")


def compute_route_distances(stops_by_name, routes_by_name):
  route_distances_and_endpoints = {}
  for long_name in routes_by_name:
    endpoints_A = []
    endpoints_B = []

    dest_A, dest_B = resolve_pointer(routes_by_name[long_name], "/attributes/direction_destinations")

    # Handle compound destinations such as Ashmont/Braintree (two separate endpoints of the Red line).
    if dest_A not in stops_by_name and "/" in dest_A:
      subnames = dest_A.split("/")
      for name in subnames:
        if name in stops_by_name:
          endpoints_A.append(name)
    else:
      endpoints_A.append(dest_A)

    if dest_B not in stops_by_name and "/" in dest_B:
      subnames = dest_B.split("/")
      for name in subnames:
        if name in stops_by_name:
          endpoints_B.append(name)
    else:
      endpoints_B.append(dest_B)

    if len(endpoints_A) == 0 or len(endpoints_B) == 0:
      print("Couldn't find {} or {} on the {} route".format(dest_A, dest_B, long_name))

    route_distances_and_endpoints[long_name] = (0, None, None)
    for stop_A in endpoints_A:
      for stop_B in endpoints_B:
        latA = resolve_pointer(stops_by_name[stop_A], "/attributes/latitude")
        lngA = resolve_pointer(stops_by_name[stop_A], "/attributes/longitude")
        latB = resolve_pointer(stops_by_name[stop_B], "/attributes/latitude")
        lngB = resolve_pointer(stops_by_name[stop_B], "/attributes/longitude")

        distance_km = haversine_distance(lngA, latA, lngB, latB)

        if distance_km > route_distances_and_endpoints[long_name][0]:
          route_distances_and_endpoints[long_name] = (distance_km, stop_A, stop_B)

  return route_distances_and_endpoints


def problem2_demo():
  """
  Problem 2: (a) Compute the number of unique MBTA stops
             (b) Determine the route with fewest/most stops
             (c) (Bonus) Compute the distance of the shortest/longest route

  NOTE: Occasionally, this will fail due to rate limiting. An error message should be printed
  out in that case, just try running the file again and it should work.
  """
  print("=====================" * 5)
  success, routes_json = get_routes(route_types=[0, 1], sort_by="long_name", descending=False)

  if not success:
    print("Error during API request:\n", routes_json)

  # For convenience, make a dictionary that maps route long names to their JSON objects.
  routes_by_name = index_by_attribute(routes_json, "/attributes/long_name")
  route_ids = strip_attributes(routes_json, "/id")
  print("Found route IDs:", route_ids)

  success, stops_json = get_stops(route_ids, sort_by="name", descending=False)

  if not success:
    print("Error during API request:\n", stops_json)

  #======== (a) Get all unique stops. The MBTA API will automatically filter out duplicates.
  stop_names = strip_attributes(stops_json, "/attributes/name")

  #======== (b) Determine which route has the most stops. Unfortunately, when multiple route IDs
  # are used to filter, the route relationship disappears from the returned items... query one route
  # at a time as a workaround.
  stops_each_route = {}
  for long_name in routes_by_name:
    route_id = resolve_pointer(routes_by_name[long_name], "/id")
    success, stops_this_route_json = get_stops([route_id], sort_by="name", descending=False)

    if not success:
      print("Error during API request:\n", stops_this_route_json)

    stops_each_route[long_name] = strip_attributes(stops_this_route_json, "/attributes/name")

  minmax_stops_route_names, minmax_stops_num = dict_argmin_argmax(stops_each_route, fn=len)

  #======== (c) Determine the geographically longest route (distance between endpoints).
  stops_by_name = index_by_attribute(stops_json, "/attributes/name")
  route_distances_and_endpoints = compute_route_distances(stops_by_name, routes_by_name)
  minmax_dist_route_names, minmax_dist_km = dict_argmin_argmax(route_distances_and_endpoints, fn=lambda x: x[0])

  print("==> MBTA Route Statistics:")
  print("  Number of unique stops:       ", len(stop_names))
  print("  Route with FEWEST stops:       {} (has {} stops)".format(minmax_stops_route_names[0], minmax_stops_num[0]))
  print("  Route with MOST stops:         {} (has {} stops)".format(minmax_stops_route_names[1], minmax_stops_num[1]))
  print("  Geographically SHORTEST route: {} ({:.04f} km)".format(minmax_dist_route_names[0], minmax_dist_km[0]))
  print("  Geographically LONGEST route:  {} ({:.04f} km)".format(minmax_dist_route_names[1], minmax_dist_km[1]))
  print("Done with Problem 2!")


if __name__ == "__main__":
  problem1_demo()
  problem2_demo()
