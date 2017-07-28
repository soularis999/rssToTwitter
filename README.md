# rssToTwitter
The purpose of the project is to be able to read the rss details of particular feed and post the newest to the twitter

Setup:

The service requires 4 env variables to be defined before the code can run:
APP_TWITTER_KEY - application key to connect to twitter
APP_TWITTER_SECRET - application secret for twitter app
USER_TWITTER_KEY - user key to connect to twitter
USER_TWITTER_SECRET - user secret

The app and user keys can be setup online @ https://apps.twitter.com. Please make sure the secrets are secure and
only visible by you. If compromised - reset the keys @ https://apps.twitter.com

Besides the evn variables you also need to setup the config. Example of config is provided - twConfig.cfg

Example to run the app
python processRss -d -s ~/.twStore <config files>

possible params
<config files>:list of comma seperated path to config files. The files are read in sequence so can override each other
-d, --dryRun [optional]: if you want to just see the items read but not published to twitter
-s, --store  [optional: default ~/.twStore]: describe where to store the processed items. The script can be reran and the
        last published post will be recored in store to prevent the republishing
-v, --verbose: verbose output
-h, --help Help



             <config files> - the list of config files to use
