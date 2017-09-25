#!/bin/bash

virtualenv build; \
source build/bin/activate; \
pip install -r config/requirements.txt; \
python -m unittest discover;