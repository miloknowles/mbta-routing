import argparse

from utils.routing import find_coarse_route, preprocess_nominal, preprocess_covid
from utils.utils import print_coarse_route


def main(args):
  print("\n======================= MBTA Routing ========================")
  if not args.interactive and (args.A is None or args.B is None):
    raise ValueError("If not in interactive mode, you must provide --A and --B")

  # Get cached stop data if possible. If unavailable, will query the MBTA API
  # for a list of stops.
  if args.covid:
    routes_containing_stop = preprocess_covid(allow_cache=True, verbose=False)
  else:
    routes_containing_stop = preprocess_nominal(allow_cache=True, verbose=False)

  try:
    while True:
      if args.interactive:
        print("\n==> Enter stop names for A and B. Press CTRL+C to exit.")
        print("==> For example, try 'Wonderland' and 'Boston College'")

      stop_A = args.A if args.A is not None else input("Stop A: ")
      stop_B = args.B if args.B is not None else input("Stop B: ")

      if stop_A not in routes_containing_stop:
        print("Invalid choice for Stop A:", stop_A)
        if args.covid:
          print("This stop might be shut down by COVID")
        continue
      if stop_B not in routes_containing_stop:
        print("Invalid choice for Stop B:", stop_B)
        if args.covid:
          print("This stop might be shut down by COVID")
        continue

      is_feasible, S = find_coarse_route(stop_A, stop_B, routes_containing_stop)

      if is_feasible:
        print_coarse_route(S, stop_A, stop_B)
      else:
        print("Couldn't find a feasible route between {} and {}".format(stop_A, stop_B))
        if args.covid:
          print("This is probably due to COVID shutdowns")

      if not args.interactive:
        return

  except KeyboardInterrupt:
    print("Exiting")
    return


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Find a route from A to B using the MBTA")
  parser.add_argument("--covid", action="store_true", help="Close any stations with a word beginning with C, O, V, I, or D")
  parser.add_argument("--interactive", action="store_true",
                      help="If true, accept user input from command line. False means only do a single query and exit.")
  parser.add_argument("--A", default=None, type=str, help="Initial stop name")
  parser.add_argument("--B", default=None, type=str, help="Destination stop name")
  args = parser.parse_args()
  main(args)
