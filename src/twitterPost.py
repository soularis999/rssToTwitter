import oauth2
import urllib
import logging

TWITTER_STATUS_POST_URL = "https://api.twitter.com/1.1/statuses/update.json?"

log = logging.getLogger(__name__)


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
        self._posts = []

    def post(self, userKey, userSecret):
        """
        Given the user key, secret the method attempts to post all the currently stored items on Twitter.
        :param userKey: user key for this application
        :param userSecret: user secret for ths application
        :return Returns back a tuple of (id, and boolean if post was successful or not)
        """
        # your application key and val
        tok = oauth2.Token(userKey, userSecret)
        client = oauth2.Client(self._consumer, tok)

        results = {}
        for post in self._posts:
            self._paramsToSend["status"] = post[1]
            query = urllib.urlencode(self._paramsToSend)

            log.info("Posting: " + TWITTER_STATUS_POST_URL + query)
            result = True
            if not self._dryRun:
                (resp, content) = client.request(TWITTER_STATUS_POST_URL + query, method="POST")
                if "200" != resp["status"]:
                    log.error("Error posting url %s -> %s" % (query, content))
                    result = False

            results[post[0]] = result

        self._posts = []
        return results

    def _generatePost(self, data, url):
        text = data + ' ' + (url if url else '')
        if len(data) > 110:
            length = data[:110].rfind(' ')
            if not url:
                length += 25
            text = data[:length] + '... ' + (url if url else '')

        text = text.strip()
        if 0 == len(text):
            return None
        return text

    def prepare(self, post_id, text, url=None):
        """
        The method stores all the posts by their ids so it could process and handle errors at the same time
        during post action
        :param post_id:
        :param text:
        """
        text = self._generatePost(text, url)
        if not text:
            return False

        self._posts.append((post_id, text))
        return True
