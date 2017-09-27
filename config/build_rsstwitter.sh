#! /bin/sh

rm ~/rsstotwitter.zip
rm -rf /tmp/rssToTwitter

virtualenv /tmp/rssToTwitter
source /tmp/rssToTwitter/bin/activate
pip install -r requirements.txt

cd $VIRTUAL_ENV/lib/python3.6/site-packages/
zip -r9 --exclude=*pip* --exclude=*setuptools* ~/rsstotwitter.zip *

cd ~/projects/rssToTwitter/src/
zip -rg --exclude=*.pyc ~/rsstotwitter.zip *

cd ~/projects/rssToTwitter/config/
zip -g ~/rsstotwitter.zip twPostsConfig
