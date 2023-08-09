#!/bin/bash
set -e
python3 -m coverage run -m pytest $@
python3 -m coverage xml
python3 -m coverage report -m