#!/bin/bash

virtualenv build; \
source build/bin/activate; \
pip install -r config/requirements.txt; \
pushd build/lib/$PYTHON_VERSION/site-packages/; \
zip -r9 ../../../../rsstotwitter.zip --exclude=*pip* --exclude=*setuptools* *; \
popd; \
cd src/; \
zip -rg ../rsstotwitter.zip --exclude=*.pyc *; \
cd ../config; \
zip -g ../rsstotwitter.zip twPostsConfig;

