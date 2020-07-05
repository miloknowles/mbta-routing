import json
from math import radians, cos, sin, asin, sqrt


def print_json(d):
  print(json.dumps(d, indent=2))


def haversine_distance(lon1, lat1, lon2, lat2):
  """
  Haversine distance formula.

  From: https://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points
  Calculate the great circle distance between two points
  on the earth (specified in decimal degrees)
  """
  # convert decimal degrees to radians
  lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

  # haversine formula
  dlon = lon2 - lon1
  dlat = lat2 - lat1
  a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
  c = 2 * asin(sqrt(a))
  r = 6371 # Radius of earth in kilometers. Use 3956 for miles

  return c * r


def dict_argmin_argmax(d, fn=lambda x: x):
  """
  Returns the min and max keys and values from a dictionary, where the value ordering is determined
  by some function 'fn'.
  """
  key_minmax = [None, None]
  value_minmax = [float('inf'), float('-inf')]

  for key in d:
    if fn(d[key]) < value_minmax[0]:
      value_minmax[0] = fn(d[key])
      key_minmax[0] = key
    if fn(d[key]) > value_minmax[1]:
      value_minmax[1] = fn(d[key])
      key_minmax[1] = key

  return key_minmax, value_minmax
