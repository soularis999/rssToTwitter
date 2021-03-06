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
        os.environ[feed_config.AWS_KEY_ENV] = "test5"
        os.environ[feed_config.AWS_SECRET_ENV] = "test6"
        os.environ[feed_config.AWS_S3_BUCKET_ENV] = "test7"
        os.environ[feed_config.TWEETS_AT_ONE_TIME_ENV] = "10"
        os.environ[feed_config.STORE_FILE_NAME_ENV] = "test9"

    def tearDown(self):
        if feed_config.APP_TWITTER_KEY_ENV in os.environ:
            del os.environ[feed_config.APP_TWITTER_KEY_ENV]
        if feed_config.APP_TWITTER_SECRET_ENV in os.environ:
            del os.environ[feed_config.APP_TWITTER_SECRET_ENV]
        if feed_config.USER_TWITTER_KEY_ENV in os.environ:
            del os.environ[feed_config.USER_TWITTER_KEY_ENV]
        if feed_config.USER_TWITTER_SECRET_ENV in os.environ:
            del os.environ[feed_config.USER_TWITTER_SECRET_ENV]
        if feed_config.AWS_KEY_ENV in os.environ:
            del os.environ[feed_config.AWS_KEY_ENV]
        if feed_config.AWS_SECRET_ENV in os.environ:
            del os.environ[feed_config.AWS_SECRET_ENV]
        if feed_config.AWS_S3_BUCKET_ENV in os.environ:
            del os.environ[feed_config.AWS_S3_BUCKET_ENV]
        if feed_config.TWEETS_AT_ONE_TIME_ENV in os.environ:
            del os.environ[feed_config.TWEETS_AT_ONE_TIME_ENV]
        if feed_config.STORE_FILE_NAME_ENV in os.environ:
            del os.environ[feed_config.STORE_FILE_NAME_ENV]

    def test_fileparse(self):
        file = '%s/testConfig.cfg' % os.path.dirname(os.path.realpath(__file__))
        config = feed_config.Config(file)

        # then
        self.assertEqual(config['netflix'].url, 'https://medium.com/feed/netflix')
        self.assertEqual(config['netflix'].numPosts, 5)

        self.assertEqual(config['Netflix'].url, 'https://medium.com/feed/netflix')
        self.assertEqual(config[' NetfliX '].url, 'https://medium.com/feed/netflix')
        self.assertEqual(config[' NETFLIX '].url, 'https://medium.com/feed/netflix')

        self.assertEqual(['NETFLIX'], config.services())

    def test_multipleFiles(self):
        # when
        file = '%s/testConfig.cfg' % os.path.dirname(os.path.realpath(__file__))
        file2 = '%s/testConfig2.cfg' % os.path.dirname(os.path.realpath(__file__))
        config = feed_config.Config(file, file2)

        # then
        self.assertEqual(config.globalConfig("MAIN").numToProcessAtOneTime, 10)
        self.assertEqual(config.globalConfig("MAIN").storeFileName, "test9")

        self.assertEqual(config.globalConfig("TWITTER").appTwitterKey, 'test1')
        self.assertEqual(config.globalConfig("TWITTER").appTwitterSecret, 'test2')
        self.assertEqual(config.globalConfig("TWITTER").userTwitterKey, 'test3')
        self.assertEqual(config.globalConfig("TWITTER").userTwitterSecret, 'test4')

        self.assertEqual(config.globalConfig("AWS").awsAccessKey, 'test5')
        self.assertEqual(config.globalConfig("AWS").awsAccessSecret, 'test6')
        self.assertEqual(config.globalConfig("AWS").awsBucket, 'test7')

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
            feed_config.Config('./testConfig.cfg', './testConfig2.cfg')

        self.assertEqual(e.exception.args[0],
                         "Twitter app was not configured (app key,app secret,user key,user secret). "
                         "Did you setup the env variables as defined in README?")


if __name__ == "__main__":
    unittest.main(TestConfig)
