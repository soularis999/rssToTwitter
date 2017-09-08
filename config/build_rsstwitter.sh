#! /bin/sh

rm ~/rsstotwitter.zip
rm -rf /tmp/rssToTwitter

virtualenv /tmp/rssToTwitter
source /tmp/rssToTwitter/bin/activate
pip install -r requirements.txt

cd $VIRTUAL_ENV/lib/python2.7/site-packages/
zip -r9 ~/rsstotwitter.zip *

cd ~/projects/rssToTwitter/src/
zip -rg ~/rsstotwitter.zip *

cd ~/projects/rssToTwitter/config/
zip -g ~/rsstotwitter.zip twPostsConfig
