#!/bin/bash
pip list
cd src
python -m process_rss -t db -d ../config/twPostsConfigTest
