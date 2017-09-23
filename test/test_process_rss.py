import unittest
import mock
import os
import feed_config

from process_rss import process, cleanup_feeds
from feed_config import SERVICE, TWITTER, AWS_STORAGE, MAIN
from data_store import STORE
from collections import namedtuple

TMP_STORE_FILE_PATH = "/tmp/twStore"


class TestProcess(unittest.TestCase):
    def setUp(self):
        os.environ[feed_config.STORE_FILE_NAME_ENV] = TMP_STORE_FILE_PATH

        if os.path.exists(TMP_STORE_FILE_PATH):
            os.remove(TMP_STORE_FILE_PATH)

    @mock.patch("process_rss.parse")
    @mock.patch("process_rss.TwitterPost")
    @mock.patch("process_rss.Config")
    @mock.patch("process_rss.FileBasedDataStore")
    def test_process(self, data_store, mock_config, mock_post, mock_parser):
        service1 = SERVICE("service1", "test1url", 5)
        service2 = SERVICE("service2", "test2url", 1)

        main = MAIN(10, TMP_STORE_FILE_PATH)
        aws = AWS_STORAGE("awsKey", "awsSecret", "awsBucket")
        twitter = TWITTER("test1AppKey", "test1AppSecret", "test1UserKey", "test1UserSecret")

        # when
        mock_config.return_value.globalConfig.side_effect = [main, twitter, aws]
        mock_config.return_value.mainService.return_value.max_posts = 5
        mock_config.return_value.services.return_value = ["service1", "service2"]
        mock_config.return_value.__getitem__.side_effect = (service1, service2)
        mock_config.return_value.globalConfig.return_value = twitter

        timeTuple = namedtuple("TimeTuple", "tm_year tm_mon tm_mday tm_hour tm_min tm_sec")
        mock_parser.return_value = {
            "status": 200,
            "entries": [
                {
                    "id": "postA",
                    "title": "post 2 title",
                    "published_parsed": timeTuple(2017, 7, 20, 5, 10, 15),
                    "link": "httpd://test2.com"
                },
                {
                    "id": "postB",
                    "title": "post 1 title",
                    "published_parsed": timeTuple(2017, 5, 15, 20, 36, 55),
                    "link": "httpd://test1.com"
                }]
        }

        mock_post.return_value.post.return_value = {
            (service1, "postA", 1500527415): True,
            (service1, "postB", 1494880615): True,
            (service2, "postA", 1500527415): False
        }

        process(False, 0, "file1", "file2")

        # then
        # test config open is called
        mock_config.assert_called_once_with('file1', 'file2')
        # test creating twitter post
        mock_post.assert_called_once_with(twitter, False)

        # test get is called

        self.assertEquals(mock_config.return_value.__getitem__.call_args_list,
                          [mock.call("service1"), mock.call("service2")])
        # test parse is called to get feed
        self.assertEquals(mock_parser.call_args_list, [mock.call("test1url"), mock.call("test2url")])
        # test post is called
        self.assertEqual(mock_post.return_value.prepare.call_args_list,
                         [
                             mock.call((service1, "postB", 1494880615.0), 'post 1 title', 'httpd://test1.com'),
                             mock.call((service1, "postA", 1500527415.0), 'post 2 title', 'httpd://test2.com'),
                             mock.call((service2, "postA", 1500527415.0), 'post 2 title', 'httpd://test2.com')])
        mock_post.return_value.post.assert_called_once_with()
        # test store is called to save data
        self.assertEquals(data_store.return_value.__setitem__.call_args_list,
                          [mock.call('service1', STORE('service1', 'postA', 1500527415)),
                           mock.call('service2', STORE('service2', 'postA', 1500527415))])
        # test write is called
        data_store.return_value.write_store.assert_called_once_with([])

    def test_cleanup_feeds(self):
        # given test case
        test_case = namedtuple('TestCase', 'store numItems data result')
        test_cases = [
            test_case(None, 5, None, []),
            test_case(STORE("t1", None, None), 5, None, []),
            test_case(STORE("t1", "test1", None), 5, None, []),
            test_case(STORE("t1", None, 1309458234), 5, None, []),
            test_case(STORE("t1", "test1", 1309458234), 5, None, []),

            test_case(None, 5, data=[{"id": "test1"}], result=[{"id": "test1"}]),
            test_case(STORE("t1", None, None), 5, data=[{"id": "test1"}], result=[{"id": "test1"}]),
            test_case(STORE("t1", "test1", None), 5, data=[{"id": "test1"}], result=[]),
            test_case(STORE("t1", None, 1309458234), 5, data=[{"id": "test1"}], result=[{"id": "test1"}]),
            test_case(STORE("t1", "test1", 1309458234), 5, data=[{"id": "test1"}], result=[]),
            test_case(STORE("t1", "test2", None), 5, data=[{"id": "test1"}], result=[{"id": "test1"}]),
            test_case(STORE("t1", "bla", None), 5, data=[{"id": "test1"}], result=[{"id": "test1"}]),

            test_case(None, 5, data=[{"id": "test1"}, {"id": "test2"}], result=[{"id": "test2"}, {"id": "test1"}]),
            test_case(STORE("t1", None, None), 5, data=[{"id": "test1"}, {"id": "test2"}],
                      result=[{"id": "test2"}, {"id": "test1"}]),
            test_case(STORE("t1", "test1", None), 5, data=[{"id": "test1"}, {"id": "test2"}], result=[]),
            test_case(STORE("t1", None, 1309458234), 5, data=[{"id": "test1"}, {"id": "test2"}],
                      result=[{"id": "test2"}, {"id": "test1"}]),
            test_case(STORE("t1", "test1", 1309458234), 5, data=[{"id": "test1"}, {"id": "test2"}], result=[]),
            test_case(STORE("t1", "test2", None), 5, data=[{"id": "test1"}, {"id": "test2"}], result=[{"id": "test1"}]),
            test_case(STORE("t1", "bla", None), 5, data=[{"id": "test1"}, {"id": "test2"}],
                      result=[{"id": "test2"}, {"id": "test1"}])
        ]

        for index, case in enumerate(test_cases):
            print(index, ' ', case)

            # when - test with None store
            result = cleanup_feeds(case.store, case.numItems, case.data)
            # then
            self.assertEqual(list(result), case.result)


if __name__ == "__main__":
    unittest.main(TestProcess)
