import unittest
import feed_config
import os
import logging

logging.basicConfig(level=logging.DEBUG)


class TestConfig(unittest.TestCase):
    def setUp(self):
        os.environ[feed_config.APP_TWITTER_KEY_ENV] = "test1"
        os.environ[feed_config.APP_TWITTER_SECRET_ENV] = "test2"
        os.environ[feed_config.USER_TWITTER_KEY_ENV] = "test3"
        os.environ[feed_config.USER_TWITTER_SECRET_ENV] = "test4"

    def tearDown(self):
        if feed_config.APP_TWITTER_KEY_ENV in os.environ:
            del os.environ[feed_config.APP_TWITTER_KEY_ENV]
        if feed_config.APP_TWITTER_SECRET_ENV in os.environ:
            del os.environ[feed_config.APP_TWITTER_SECRET_ENV]
        if feed_config.USER_TWITTER_KEY_ENV in os.environ:
            del os.environ[feed_config.USER_TWITTER_KEY_ENV]
        if feed_config.USER_TWITTER_SECRET_ENV in os.environ:
            del os.environ[feed_config.USER_TWITTER_SECRET_ENV]

    def test_fileparse(self):
        config = feed_config.Config()

        # when
        config.open(os.path.expanduser('testConfig.cfg'))

        # then
        self.assertEqual(config['netflix'].url, 'https://medium.com/feed/netflix')
        self.assertEqual(config['netflix'].numPosts, 5)

        self.assertEqual(config['Netflix'].url, 'https://medium.com/feed/netflix')
        self.assertEqual(config[' NetfliX '].url, 'https://medium.com/feed/netflix')
        self.assertEqual(config[' NETFLIX '].url, 'https://medium.com/feed/netflix')

        self.assertEqual(['NETFLIX'], config.services())

    def test_multipleFiles(self):
        config = feed_config.Config()

        # when
        config.open(os.path.expanduser('testConfig.cfg'), os.path.expanduser('testConfig2.cfg'))

        # then
        self.assertEqual(config.mainService().numToProcessAtOneTime, 10)

        self.assertEqual(config.appService("TWITTER").appTwitterKey, 'test1')
        self.assertEqual(config.appService("TWITTER").appTwitterSecret, 'test2')
        self.assertEqual(config.appService("TWITTER").userTwitterKey, 'test3')
        self.assertEqual(config.appService("TWITTER").userTwitterSecret, 'test4')

        self.assertEqual(config['LINKEDIN'].serviceName, 'LINKEDIN')
        self.assertEqual(config['LINKEDIN'].url, 'https://engineering.linkedin.com/blog.rss')
        self.assertEqual(config['LINKEDIN'].numPosts, 1)
        self.assertEqual(config['NETFLIX'].serviceName, 'NETFLIX')
        self.assertEqual(config['NETFLIX'].url, 'https://netflix.com/feed/netflix-techblog')
        self.assertEqual(config['NETFLIX'].numPosts, 1)
        self.assertEqual(['LINKEDIN', 'NETFLIX'], sorted(config.services()))

        if __name__ == "__main__":
            unittest.main(TestConfig)

    def test_validation(self):
        # when
        with self.assertRaises(SystemError) as e:
            del os.environ[feed_config.APP_TWITTER_KEY_ENV]
            del os.environ[feed_config.APP_TWITTER_SECRET_ENV]
            del os.environ[feed_config.USER_TWITTER_KEY_ENV]
            del os.environ[feed_config.USER_TWITTER_SECRET_ENV]
            config = feed_config.Config()
            config.open('./testConfig.cfg', './testConfig2.cfg')

        self.assertEqual(e.exception.message,
                         "Twitter app was not configured (app key,app secret,user key,user secret). "
                         "Did you setup the env variables as defined in README?")


if __name__ == "__main__":
    unittest.main(TestConfig)
