import requests
from jsonpointer import resolve_pointer


def get_routes(route_types=[0,1], sort_by="long_name", descending=False):
  """
  Query routes from the MBTA API, optionally filtering by a route type.
  https://api-v3.mbta.com/docs/swagger/index.html#/Route/ApiWeb_RouteController_index

  route_types (list of int/str) :
    A list of route types to include in the query (i.e 0=Light Rail, 1=Heavy Rail, etc). If None,
    or an empty list, all of the route types will be returned.
  sort_by (str) :
    An attribute to sort by (e.g. "long_name").
  descending (bool) :
    Return results in descending order, according to the sort_by attribute.

  Returns:
    (bool) Whether the GET was successful
    (dict) the JSON response.
  """
  params = {}

  if route_types is not None:
    params["filter[type]"] = ",".join([str(r) for r in route_types])

  if sort_by is not None:
    params["sort"] = ("-" if descending else "") + sort_by

  r = requests.get("https://api-v3.mbta.com/routes", params=params)
  success = (r.status_code == 200)

  return success, r.json()


def get_stops(route_ids, sort_by="name", descending=False):
  """
  Query all of the stops along a given route. Optionally sort by an attribute.
  https://api-v3.mbta.com/docs/swagger/index.html#/Stop/ApiWeb_StopController_index

  route_ids (list of str) :
    A list of IDs to filter by. Based on a get_routes query, the valid route IDs are:
    'Blue', 'Green-B', 'Green-C', 'Green-D', 'Green-E', 'Mattapan', 'Orange', 'Red'
  sort_by (str) :
    An attribute to sort by (e.g. "name").
  descending (bool) :
    Return results in descending order, according to the sort_by attribute.
  """
  params = {}
  params["include"] = "route" # NOTE: Must include the "route" relationship to filter by it.
  params["filter[route]"] = ",".join(route_ids)

  if sort_by is not None:
    params["sort"] = ("-" if descending else "") + sort_by

  r = requests.get("https://api-v3.mbta.com/stops", params=params)
  success = (r.status_code == 200)

  return success, r.json()


def strip_attributes(json, ptr):
  """
  Convenience function for getting one or more attributes from a list of objects.
  """
  return [resolve_pointer(obj, ptr) for obj in json["data"]]


def index_by_attribute(json, key_ptr):
  index = {}
  for obj in json["data"]:
    index[resolve_pointer(obj, key_ptr)] = obj
  return index


def count_stops_each_route(stops_json):
  stops_each_route = {}

  print(stops_json)

  # for stop in stops_json["data"]:
    # print(stop["relationships"]["route"])
