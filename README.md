# MBTA Routing Coding Challenge

This repository implements solutions for the ADAPT coding challenge.

## Setup

- `pip3 install jsonpointer`
- **NOTE**: I tested this repository with `Python3.6`. Any Python3 version should work, but not Python2 due to the import syntax that's used.

## Running the Code

- Problems 1 and 2:  `python3 mbta_main.py`
- Run Problem 3 with `python3 routing_main.py --interactive`
- Run Problem 4 with `python3 routing_main.py --interactive --covid`

## Running the Tests

Some additional edge-cases are tested in the `test` folder. They must be run from the main directory:
```python
python3 -m unittest test.test_mbta_api
python3 -m unittest test.test_routing
```
