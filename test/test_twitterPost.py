import logging

import mock
import unittest
import twitterPost

logging.basicConfig(level=logging.DEBUG)


class TestTwitterPost(unittest.TestCase):
    @mock.patch("twitterPost.oauth2")
    def test_request_successful(self, mock_oauth2):
        # given
        mock_oauth2.Client().request.return_value = ({"status": "200"}, {})

        # when
        post = twitterPost.TwitterPost("key", "secret")
        results = post.post("userKey", "userSecret", "tweet")

        # then
        mock_oauth2.Consumer.assert_called_once_with('key', 'secret')
        mock_oauth2.Token.assert_called_once_with("userKey", "userSecret")
        mock_oauth2.Client.return_value.request.assert_called_once_with(
            "https://api.twitter.com/1.1/statuses/update.json?status=tweet", method="POST")

        self.assertEqual(results, {})

    @mock.patch("twitterPost.oauth2")
    def test_request_successful_with_spaces(self, mock_oauth2):
        # given
        mock_oauth2.Client().request.return_value = ({"status": "200"}, {})

        # when
        post = twitterPost.TwitterPost("key", "secret")
        results = post.post("userKey", "userSecret", "tweet this please")

        # then
        mock_oauth2.Consumer.assert_called_once_with('key', 'secret')
        mock_oauth2.Token.assert_called_once_with("userKey", "userSecret")
        mock_oauth2.Client.return_value.request.assert_called_once_with(
            "https://api.twitter.com/1.1/statuses/update.json?status=tweet+this+please", method="POST")

        self.assertEqual(results, {})

    @mock.patch("twitterPost.oauth2")
    def test_request_error(self, mock_oauth2):
        # given
        mock_oauth2.Client().request.return_value = ({"status": "400"}, {})

        # when
        post = twitterPost.TwitterPost("key", "secret")

        with self.assertRaises(twitterPost.TwitterException) as e:
            post.post("userKey", "userSecret", "tweet this please")

        # then
        mock_oauth2.Consumer.assert_called_once_with('key', 'secret')
        mock_oauth2.Token.assert_called_once_with("userKey", "userSecret")
        mock_oauth2.Client.return_value.request.assert_called_once_with(
            "https://api.twitter.com/1.1/statuses/update.json?status=tweet+this+please", method="POST")

        self.assertEqual(e.exception.response, {"status": "400"})
        self.assertEqual(e.exception.body, {})

    @mock.patch("twitterPost.oauth2")
    def test_dry_run(self, mock_oauth2):
        # when
        post = twitterPost.TwitterPost("key", "secret", True)
        result = post.post("userKey", "userSecret", "tweet this please")

        # then
        mock_oauth2.Consumer.assert_called_once_with('key', 'secret')
        mock_oauth2.Token.assert_called_once_with("userKey", "userSecret")
        mock_oauth2.Client.request.assert_not_called()
        self.assertEqual(result, None)


if __name__ == "__main__":
    unittest.main(TestTwitterPost)
