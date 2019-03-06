#!/bin/bash

################
# Add $PYTHON_VERSION=python3.6
################

export PYTHON_VERSION=python3.7

rm -rf /tmp/build/
rm /tmp/rsstotwitter.zip
mkdir /tmp/build

virtualenv -p $PYTHON_VERSION /tmp/build; \
source /tmp/build/bin/activate; \
pip install -r requirements.txt; \
pushd /tmp/build/lib/$PYTHON_VERSION/site-packages/; \
zip -r9 /tmp/rsstotwitter.zip --exclude=*pip* --exclude=*setuptools* *; \
popd; \
cd src/; \
zip -rg /tmp/rsstotwitter.zip --exclude=*.pyc *; \
cd ../config; \
zip -g /tmp/rsstotwitter.zip twPostsConfig; \


