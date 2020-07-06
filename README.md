# MBTA Routing Coding Challenge

This repository implements solutions for the ADAPT coding challenge.

## Setup

- There shouldn't be any packages to install - they all ship with Python.
- **NOTE**: I implemented and tested this repository with `Python3.6`. Any Python3 version should work, but probably not Python2.

## Running the Code

- Problems 1 and 2:  `python mbta_main.py`
- Run Problem 3 with `python routing_main.py --interactive`
- Run Problem 4 with `python routing_main.py --interactive --covid`

## Running the Tests

Some additional edge-cases are tested in the `test` folder. They must be run from the main directory:
```python
python -m unittest test.test_mbta_api
python -m unittest test.test_routing
```
