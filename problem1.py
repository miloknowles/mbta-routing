from mbta_api import get_routes, parse_get_routes_json


if __name__ == "__main__":
  """
  Solution to Problem 1:
    - To speed up the API request, I use the filter[type]=0,1 option.
    - Some other configurable options are demonstrated in test_mbta_api.py
  """
  success, json = get_routes(route_types=["0", "1"], sort_by="long_names", descending=False)

  if success:
    long_names = parse_get_routes_json(json)
    print("Found {} routes: {}".format(len(long_names), long_names))
  else:
    print("Error during API request:\n", json)
