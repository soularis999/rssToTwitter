#! /bin/sh

export PYTHON_VERSION="python3.7"

rm ~/rsstotwitter.zip
rm -rf /tmp/rssToTwitter

virtualenv -p $PYTHON_VERSION /tmp/rssToTwitter
source /tmp/rssToTwitter/bin/activate
pip install -r requirements.txt

cd $VIRTUAL_ENV/lib/$PYTHON_VERSION/site-packages/
zip -r9 --exclude=*pip* --exclude=*setuptools* ~/rsstotwitter.zip *

cd ~/projects/rssToTwitter/src/
zip -rg --exclude=*.pyc ~/rsstotwitter.zip *

cd ~/projects/rssToTwitter/config/
zip -g ~/rsstotwitter.zip twPostsConfig

cd ~/projects/rssToTwitter/bin/
zip -g ~/rsstotwitter.zip *.sh
