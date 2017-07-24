import unittest
import feedConfig
import os
import logging

logging.basicConfig(level=logging.DEBUG)


class TestConfig(unittest.TestCase):
    def test_fileparse(self):
        config = feedConfig.Config()

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
        config = feedConfig.Config()

        # when
        config.open(os.path.expanduser('testConfig.cfg'), os.path.expanduser('testConfig2.cfg'))

        # then
        self.assertEqual(config.mainService().storePath, './twStore')
        self.assertEqual(config.mainService().numToProcessAtOneTime, 10)
        self.assertEqual(config.mainService().appTwitterKey, 'test1')
        self.assertEqual(config.mainService().appTwitterSecret, 'test2')
        self.assertEqual(config.mainService().userTwitterKey, 'test3')
        self.assertEqual(config.mainService().userTwitterSecret, 'test4')

        self.assertEqual(config['LINKEDIN'].url, 'https://engineering.linkedin.com/blog.rss')
        self.assertEqual(config['LINKEDIN'].numPosts, 1)
        self.assertEqual(config['NETFLIX'].url, 'https://netflix.com/feed/netflix-techblog')
        self.assertEqual(config['NETFLIX'].numPosts, 1)
        self.assertEqual(['LINKEDIN', 'NETFLIX'], sorted(config.services()))

        if __name__ == "__main__":
            unittest.main(TestConfig)

    def test_mergingStoreAndConfig(self):

        config = feedConfig.Config()

        # when
        config.open('./testConfig.cfg', './testConfig2.cfg')

        # then
        self.assertEqual(config['LINKEDIN'].url, 'https://engineering.linkedin.com/blog.rss')
        self.assertEqual(config['LINKEDIN'].numPosts, 1)
        self.assertEqual(config['LINKEDIN'].lastProcessedId, None)
        self.assertEqual(config['LINKEDIN'].lastProcessedUpdateTimestamp, None)

        self.assertEqual(config['NETFLIX'].url, 'https://netflix.com/feed/netflix-techblog')
        self.assertEqual(config['NETFLIX'].numPosts, 1)
        self.assertEqual(config['NETFLIX'].lastProcessedId, 'testid1')
        self.assertEqual(config['NETFLIX'].lastProcessedUpdateTimestamp, 2348233)

        self.assertEqual(['LINKEDIN', 'NETFLIX'], sorted(config.services()))

    def test_writing(self):
        config = feedConfig.Config()
        config["T1"] = feedConfig.SERVICE("url1", 1, None, None)
        config["T2"] = feedConfig.SERVICE("url2", 2, "id2", None)
        config["T3"] = feedConfig.SERVICE("url3", 3, None, 5555545)
        config["T4"] = feedConfig.SERVICE("url4", 4, "id4", 444555666)
        config["T5"] = feedConfig.SERVICE("url5", 5, "id5", 555666777)
        config._main = feedConfig.MAIN("/tmp/.twStore", 10, None, None, None, None)

        # when
        config.writeStore()

        # then
        self.assertTrue(os.path.exists("/tmp/.twStore"))
        self.assertEqual(file("/tmp/.twStore").readlines(), ["T4|id4|444555666\n", "T5|id5|555666777\n"])

        # when - try reading the file back
        config["T4"] = feedConfig.SERVICE("url4", 4, "id4New", 11111111)
        config["T5"] = feedConfig.SERVICE("url5", 5, "id5New", 22222222)
        config._readStore()

        # then
        self.assertEqual(config['T4'].lastProcessedId, 'id4')
        self.assertEqual(config['T4'].lastProcessedUpdateTimestamp, 444555666)

        self.assertEqual(config['T5'].lastProcessedId, 'id5')
        self.assertEqual(config['T5'].lastProcessedUpdateTimestamp, 555666777)


if __name__ == "__main__":
    unittest.main(TestConfig)
