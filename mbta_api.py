import requests


def get_routes(route_types=["0", "1"], sort_by="long_name", descending=False):
  """
  Query routes from the MBTA API, optionally filtering by a route type.
  https://api-v3.mbta.com/docs/swagger/index.html#/Route/ApiWeb_RouteController_index

  route_types (list of str) :
    A list of route types to include in the query (i.e 0=Light Rail, 1=Heavy Rail, etc). If None,
    or an empty list, all of the route types will be returned.
  sort_by (str) :
    An attribute to sort by (e.g. "long_name").
  descending (bool) : Return results in descending order, according to the sort_by attribute.

  Returns:
    (bool) Whether the GET was successful
    (dict) the JSON response.
  """
  params = {}

  if route_types is not None and len(route_types) > 0:
    params["filter[type]"] = route_types

  if sort_by is not None:
    params["sort"] = ("-" if descending else "") + sort_by

  r = requests.get("https://api-v3.mbta.com/routes", params=params)
  success = (r.status_code == 200)

  return success, r.json()


def parse_get_routes_json(json):
  long_names = [item["attributes"]["long_name"] for item in json["data"]]
  return long_names
