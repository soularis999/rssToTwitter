import unittest
import feedConfig
import os
import logging

logging.basicConfig(level=logging.DEBUG)

TMP_STORE_FILE_PATH = "/tmp/twStore"


class TestConfig(unittest.TestCase):
    def setUp(self):
        if (os.path.exists(TMP_STORE_FILE_PATH)):
            os.remove(TMP_STORE_FILE_PATH)

    def test_fileparse(self):
        config = feedConfig.Config(store_path=TMP_STORE_FILE_PATH)

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
        config = feedConfig.Config(store_path=TMP_STORE_FILE_PATH)

        # when
        config.open(os.path.expanduser('testConfig.cfg'), os.path.expanduser('testConfig2.cfg'))

        # then
        self.assertEqual(config.mainService().numToProcessAtOneTime, 10)
        self.assertEqual(config.mainService().appTwitterKey, 'test1')
        self.assertEqual(config.mainService().appTwitterSecret, 'test2')
        self.assertEqual(config.mainService().userTwitterKey, 'test3')
        self.assertEqual(config.mainService().userTwitterSecret, 'test4')

        self.assertEqual(config['LINKEDIN'].serviceName, 'LINKEDIN')
        self.assertEqual(config['LINKEDIN'].url, 'https://engineering.linkedin.com/blog.rss')
        self.assertEqual(config['LINKEDIN'].numPosts, 1)
        self.assertEqual(config['NETFLIX'].serviceName, 'NETFLIX')
        self.assertEqual(config['NETFLIX'].url, 'https://netflix.com/feed/netflix-techblog')
        self.assertEqual(config['NETFLIX'].numPosts, 1)
        self.assertEqual(['LINKEDIN', 'NETFLIX'], sorted(config.services()))

        if __name__ == "__main__":
            unittest.main(TestConfig)

    def test_mergingStoreAndConfig(self):
        config = feedConfig.Config(store_path=TMP_STORE_FILE_PATH)
        with file(TMP_STORE_FILE_PATH, 'w') as f:
            f.writelines(['NETFLIX|testid1|2348233\n', 'YAHOO|testid22223423|2394230\n'])

        # when
        config.open('./testConfig.cfg', './testConfig2.cfg')

        # then
        self.assertEqual(config['LINKEDIN'].serviceName, 'LINKEDIN')
        self.assertEqual(config['LINKEDIN'].url, 'https://engineering.linkedin.com/blog.rss')
        self.assertEqual(config['LINKEDIN'].numPosts, 1)
        self.assertIsNone(config['LINKEDIN'].store)

        self.assertEqual(config['NETFLIX'].serviceName, 'NETFLIX')
        self.assertEqual(config['NETFLIX'].url, 'https://netflix.com/feed/netflix-techblog')
        self.assertEqual(config['NETFLIX'].numPosts, 1)
        self.assertEqual(config['NETFLIX'].store, feedConfig.STORE('NETFLIX', 'testid1', 2348233l))

        self.assertEqual(['LINKEDIN', 'NETFLIX'], sorted(config.services()))

        config.writeStore()
        self.assertEqual(file(TMP_STORE_FILE_PATH).readlines(),
                         ['NETFLIX|testid1|2348233\n', 'YAHOO|testid22223423|2394230\n'])


    def test_writing(self):
        config = feedConfig.Config(store_path=TMP_STORE_FILE_PATH)
        config["T1"] = feedConfig.SERVICE("T1", "url1", 1, None)
        config["T2"] = feedConfig.SERVICE("T2", "url2", 2, feedConfig.STORE("T2", "id2", None))
        config["T3"] = feedConfig.SERVICE("T3", "url3", 3, feedConfig.STORE("T3", None, 5555545))
        config["T4"] = feedConfig.SERVICE("T4", "url4", 4, feedConfig.STORE("T4", "id4", 444555666))
        config["T5"] = feedConfig.SERVICE("T5", "url5", 5, feedConfig.STORE("T5", "id5", 555666777))
        config._main = feedConfig.MAIN(10, None, None, None, None)

        # when
        config.writeStore()

        # then
        self.assertTrue(os.path.exists(TMP_STORE_FILE_PATH))
        self.assertEqual(file(TMP_STORE_FILE_PATH).readlines(),
                         ["T4|id4|444555666\n", "T5|id5|555666777\n", "T2|id2|\n", "T3||5555545\n"])

        # when - try reading the file back
        config["T4"] = feedConfig.SERVICE("T4", "url4", 4, feedConfig.STORE("T4", "id4New", 11111111))
        config["T5"] = feedConfig.SERVICE("T5", "url5", 5, feedConfig.STORE("T5", "id5New", 22222222))
        store_data = config._readStore()

        # then
        self.assertIsNone(store_data['T2'])
        self.assertIsNone(store_data['T3'])

        self.assertEqual(store_data['T4'].serviceName, 'T4')
        self.assertEqual(store_data['T4'].lastProcessedId, 'id4')
        self.assertEqual(store_data['T4'].lastProcessedUpdateTimestamp, 444555666)

        self.assertEqual(store_data['T5'].serviceName, 'T5')
        self.assertEqual(store_data['T5'].lastProcessedId, 'id5')
        self.assertEqual(store_data['T5'].lastProcessedUpdateTimestamp, 555666777)

    def test_dry_run(self):
        config = feedConfig.Config(True, store_path=TMP_STORE_FILE_PATH)
        config["T1"] = feedConfig.SERVICE("T1", "url1", 1, None)
        config["T2"] = feedConfig.SERVICE("T2", "url2", 2, feedConfig.STORE("T2", "id2", None))
        config["T3"] = feedConfig.SERVICE("T3", "url3", 3, feedConfig.STORE("T3", None, 5555545))
        config["T4"] = feedConfig.SERVICE("T4", "url4", 4, feedConfig.STORE("T4", "id4", 444555666))
        config["T5"] = feedConfig.SERVICE("T5", "url5", 5, feedConfig.STORE("T5", "id5", 555666777))

        # when
        config.writeStore()

        # then
        self.assertFalse(os.path.exists(TMP_STORE_FILE_PATH))


if __name__ == "__main__":
    unittest.main(TestConfig)
