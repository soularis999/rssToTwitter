import oauth2
import urllib
import logging

TWITTER_STATUS_POST_URL = "https://api.twitter.com/1.1/statuses/update.json?"

log = logging.getLogger(__name__)


class TwitterException(Exception):
    def __init__(self, response, body):
        self.response = response
        self.body = body

    def __str__(self):
        from os import linesep
        return "Response %s %s %s" % (self.response, linesep, self.body)


class TwitterPost(object):
    """
    The purpose of the class is to authenticate into the twitter system and be able to post the tweets
    In theory you can post with different users but through same application
    """

    def __init__(self, appKey, appSecret, dryRun=False):
        """
        The constructor is taking two params, the application key and secret
        :param appKey: string key value of the applications that will be posting the tweet
        :param appSecret: the secret of the application that will be posting the tweet
        :param dryRun: the flag can be set to just log the messages instead of publishing them to twitter
        """
        self._consumer = oauth2.Consumer(appKey, appSecret)
        self._paramsToSend = {"status": None}
        self._dryRun = dryRun

    def post(self, userKey, userSecret, tweet):
        """
        Given the user key, secret and tweet to post the method creates a token and posts the message
        :param userKey: user key for this application
        :param userSecret: user secret for ths application
        :param tweet: tweet to post
        :raise Will raise TwitterException if response status is not 200
        """
        # your application key and val
        tok = oauth2.Token(userKey, userSecret)
        client = oauth2.Client(self._consumer, tok)

        self._paramsToSend["status"] = tweet
        query = urllib.urlencode(self._paramsToSend)

        log.info("Posting: " + TWITTER_STATUS_POST_URL + query)
        if not self._dryRun:
            (resp, content) = client.request(TWITTER_STATUS_POST_URL + query, method="POST")
            if "200" != resp["status"]:
                raise TwitterException(resp, content)
            return content
        return None
