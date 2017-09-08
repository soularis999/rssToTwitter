#! /bin/sh

rm ~/rsstotwitter.zip
source ~/python_virtual_envs/rssTwitter/bin/activate

cd $VIRTUAL_ENV/lib/python2.7/site-packages/
zip -r9 ~/rsstotwitter.zip *

cd ~/projects/rssToTwitter/src/
zip -rg ~/rsstotwitter.zip *

cd ~/projects/random/config/
zip -g ~/rsstotwitter.zip twPostsConfig
