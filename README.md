# rssToTwitter
The purpose of the project is to be able to read the rss details of particular feed and post the newest to the twitter
The application stores the data into a file that can reside on the local disk or in AWS S3 bucket

Setup:

The service requires 4 env variables to be defined before the code can run:
APP_TWITTER_KEY - application key to connect to twitter
APP_TWITTER_SECRET - application secret for twitter app
USER_TWITTER_KEY - user key to connect to twitter
USER_TWITTER_SECRET - user secret
AWS_KEY - [OPTIONAL] - AWS key to connect to S3
AWS_SECRET - [OPTIONAL] - AWS secret to connect to S3
AWS_S3_BUCKET - [OPTIONAL] - the bucket to put and read the store file from
TWEETS_AT_ONE_TIME [OPTIONAL, Default: 15] - Number of posts to post at one time
STORE_FILE_NAME [OPTIONAL, Default: ~/.twStore] - where to store the posted data to so application would not
    post the same tweets again after restart

The app and user keys can be setup online @ https://apps.twitter.com. Please make sure the secrets are secure and
only visible by you. If compromised - reset the keys @ https://apps.twitter.com

Besides the evn variables you also need to setup the config. Example of config is provided - twConfig.cfg

Example to run the app
python -m process_rss -d -s ~/.twStore <config files>

possible params
<config files>:list of comma seperated path to config files. The files are read in sequence so can override each other
-a, --aws [Optional]: The optional flag that indicates that the storage will be saved to AWS S3 disk
-h, --help Help
-d, --dryRun [optional]: if you want to just see the items read but not published to twitter
-v, --verbose: verbose output


<config files> - the list of config files to use
