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
        post.prepare("1", "tweet")
        results = post.post("userKey", "userSecret")

        # then
        mock_oauth2.Consumer.assert_called_once_with('key', 'secret')
        mock_oauth2.Token.assert_called_once_with("userKey", "userSecret")
        mock_oauth2.Client.return_value.request.assert_called_once_with(
            "https://api.twitter.com/1.1/statuses/update.json?status=tweet", method="POST")

        self.assertEqual(results, {"1": True})

    @mock.patch("twitterPost.oauth2")
    def test_long_text(self, mock_oauth2):
        # given
        mock_oauth2.Client().request.return_value = ({"status": "200"}, {})

        # when
        post = twitterPost.TwitterPost("key", "secret", False)
        post.prepare("1", "tweet this please very very very long string of 150 characters and longer and longer and longer and longer and longer and longer and longer and logner", "test123")
        results = post.post("userKey", "userSecret")

        # then
        query = "tweet this please very very very long string of 150 characters and longer and longer and longer and longer... test123".replace(' ','+')
        mock_oauth2.Consumer.assert_called_once_with('key', 'secret')
        mock_oauth2.Token.assert_called_once_with("userKey", "userSecret")
        mock_oauth2.Client.return_value.request.assert_called_once_with(
            "https://api.twitter.com/1.1/statuses/update.json?status=" + query, method="POST")

        self.assertEqual(results, {"1": True})

    @mock.patch("twitterPost.oauth2")
    def test_cache_does_not_persist_between_posts(self, mock_oauth2):
        # given
        mock_oauth2.Client().request.return_value = ({"status": "200"}, {})

        # when
        post = twitterPost.TwitterPost("key", "secret")
        post.prepare("1", "tweet 1")
        results1 = post.post("userKey", "userSecret")
        post.prepare("2", "tweet 2")
        results2 = post.post("userKey", "userSecret")

        # then
        mock_oauth2.Consumer.assert_called_once_with('key', 'secret')
        self.assertEqual(mock_oauth2.Token.call_args_list, [
            mock.call("userKey", "userSecret"), mock.call("userKey", "userSecret")])
        self.assertEqual(mock_oauth2.Client.return_value.request.call_args_list, [
            mock.call("https://api.twitter.com/1.1/statuses/update.json?status=tweet+1", method="POST"),
            mock.call("https://api.twitter.com/1.1/statuses/update.json?status=tweet+2", method="POST")])

        self.assertEqual(results1, {"1": True})
        self.assertEqual(results2, {"2": True})

    @mock.patch("twitterPost.oauth2")
    def test_request_successful_with_spaces(self, mock_oauth2):
        # given
        mock_oauth2.Client().request.return_value = ({"status": "200"}, {})

        # when
        post = twitterPost.TwitterPost("key", "secret")
        post.prepare("1", "tweet this please")
        results = post.post("userKey", "userSecret")

        # then
        mock_oauth2.Consumer.assert_called_once_with('key', 'secret')
        mock_oauth2.Token.assert_called_once_with("userKey", "userSecret")
        mock_oauth2.Client.return_value.request.assert_called_once_with(
            "https://api.twitter.com/1.1/statuses/update.json?status=tweet+this+please", method="POST")

        self.assertEqual(results, {"1": True})

    @mock.patch("twitterPost.oauth2")
    def test_multiple_successfull_posts(self, mock_oauth2):
        # given
        mock_oauth2.Client().request.return_value = ({"status": "200"}, {})

        # when
        post = twitterPost.TwitterPost("key", "secret")
        post.prepare("1", "tweet this please")
        post.prepare("2", "tweet that please")
        post.prepare("3", "tweet one more please")
        results = post.post("userKey", "userSecret")

        # then
        mock_oauth2.Consumer.assert_called_once_with('key', 'secret')
        mock_oauth2.Token.assert_called_once_with("userKey", "userSecret")
        mock_oauth2.Client.return_value.request.assert_called_once_with(
            "https://api.twitter.com/1.1/statuses/update.json?status=tweet+this+please", method="POST")

        self.assertEqual(results, {"1": True, "2": True, "3": True})

    @mock.patch("twitterPost.oauth2")
    def test_multiple_successfull_posts(self, mock_oauth2):
        # given
        mock_oauth2.Client().request.return_value = ({"status": "200"}, {})

        # when
        post = twitterPost.TwitterPost("key", "secret")
        post.prepare("1", "tweet this please")
        post.prepare("2", "tweet that please")
        post.prepare("3", "tweet one more please")
        results = post.post("userKey", "userSecret")

        # then
        mock_oauth2.Consumer.assert_called_once_with('key', 'secret')
        mock_oauth2.Token.assert_called_once_with("userKey", "userSecret")
        self.assertEqual(mock_oauth2.Client.return_value.request.call_args_list, [
            mock.call("https://api.twitter.com/1.1/statuses/update.json?status=tweet+this+please", method="POST"),
            mock.call("https://api.twitter.com/1.1/statuses/update.json?status=tweet+that+please", method="POST"),
            mock.call("https://api.twitter.com/1.1/statuses/update.json?status=tweet+one+more+please", method="POST")])

        self.assertEqual(results, {"1": True, "2": True, "3": True})

    @mock.patch("twitterPost.oauth2")
    def test_multiple_error_posts(self, mock_oauth2):
        # given
        def effect(*args, **kwargs):
            if args[0] == "https://api.twitter.com/1.1/statuses/update.json?status=tweet+that+please":
                return {"status": "400"}, {}
            return {"status": "200"}, {}

        mock_oauth2.Client().request.side_effect = effect

        # when
        post = twitterPost.TwitterPost("key", "secret")
        post.prepare("1", "tweet this please")
        post.prepare("2", "tweet that please")
        post.prepare("3", "tweet one more please")
        results = post.post("userKey", "userSecret")

        # then
        mock_oauth2.Consumer.assert_called_once_with('key', 'secret')
        mock_oauth2.Token.assert_called_once_with("userKey", "userSecret")
        self.assertEqual(mock_oauth2.Client.return_value.request.call_args_list, [
            mock.call("https://api.twitter.com/1.1/statuses/update.json?status=tweet+this+please", method="POST"),
            mock.call("https://api.twitter.com/1.1/statuses/update.json?status=tweet+that+please", method="POST"),
            mock.call("https://api.twitter.com/1.1/statuses/update.json?status=tweet+one+more+please", method="POST")])

        self.assertEqual(results, {"1": True, "2": False, "3": True})

    @mock.patch("twitterPost.oauth2")
    def test_dry_run(self, mock_oauth2):
        # when
        post = twitterPost.TwitterPost("key", "secret", True)
        post.prepare("1", "tweet this please")
        result = post.post("userKey", "userSecret")

        # then
        mock_oauth2.Consumer.assert_called_once_with('key', 'secret')
        mock_oauth2.Token.assert_called_once_with("userKey", "userSecret")
        mock_oauth2.Client.request.assert_not_called()
        self.assertEqual(result, {"1": True})




if __name__ == "__main__":
    unittest.main(TestTwitterPost)

