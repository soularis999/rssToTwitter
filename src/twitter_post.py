import oauth2
import urllib.parse
import logging

TWITTER_STATUS_POST_URL = "https://api.twitter.com/1.1/statuses/update.json?"

log = logging.getLogger(__name__)


class TwitterPost(object):
    """
    The purpose of the class is to authenticate into the twitter system and be able to post the tweets
    In theory you can post with different users but through same application
    """

    def __init__(self, twitter_config, dry_run=False):
        """
        The constructor is taking two params, the application key and secret
        :param twitter_config: as described  by namedtuple in feedConfig.TWITTER
        :param dryRun: the flag can be set to just log the messages instead of publishing them to twitter
        """
        self._consumer = oauth2.Consumer(twitter_config.appTwitterKey, twitter_config.appTwitterSecret)
        self._twitter_config = twitter_config
        self._params = {"status": None}
        self._dry_run = dry_run
        self._posts = []

    def post(self):
        """
        method attempts to post all the currently stored items on Twitter using the authentication credentials provided
                in constructor param - twitter_config.
        :return Returns back a tuple of (id, and boolean if post was successful or not)
        """
        # your application key and val
        tok = oauth2.Token(self._twitter_config.userTwitterKey, self._twitter_config.userTwitterSecret)
        client = oauth2.Client(self._consumer, tok)

        results = {}
        for post in self._posts:
            self._params["status"] = post[1]
            query = urllib.parse.urlencode(self._params)

            log.info("Posting: %s%s" % (TWITTER_STATUS_POST_URL, query))
            result = True
            if not self._dry_run:
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
