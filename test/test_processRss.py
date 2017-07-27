import unittest
import mock
import os

from processRss import process, cleanup_feeds
from feedConfig import SERVICE, STORE
from test_feedConfig import TMP_STORE_FILE_PATH
from collections import namedtuple


class TestProcess(unittest.TestCase):
    def setUp(self):
        if os.path.exists(TMP_STORE_FILE_PATH):
            os.remove(TMP_STORE_FILE_PATH)

    @mock.patch("processRss.parse")
    @mock.patch("processRss.TwitterPost")
    @mock.patch("processRss.Config")
    def test_process(self, mock_config, mock_post, mock_parser):
        service1 = SERVICE("service1", "test1url", 5, None)
        service2 = SERVICE("service2", "test2url", 1, None)

        # when
        mock_config.return_value.mainService.return_value.max_posts = 5
        mock_config.return_value.mainService.return_value.appTwitterKey = "test1AppKey"
        mock_config.return_value.mainService.return_value.appTwitterSecret = "test1AppSecret"
        mock_config.return_value.mainService.return_value.userTwitterKey = "test1UserKey"
        mock_config.return_value.mainService.return_value.userTwitterSecret = "test1UserSecret"
        mock_config.return_value.services.return_value = ["service1", "service2"]
        mock_config.return_value.__getitem__.side_effect = (service1, service2)

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

        process(False, TMP_STORE_FILE_PATH, "file1", "file2")

        # then
        # test config open is called
        mock_config.return_value.open.assert_called_once_with('file1', 'file2')
        # test creating twitter post
        mock_post.assert_called_once_with("test1AppKey", "test1AppSecret", False)

        # test get is called

        self.assertEquals(mock_config.return_value.__getitem__.call_args_list,
                          [mock.call("service1"), mock.call("service2")])
        # test parse is called to get feed
        self.assertEquals(mock_parser.call_args_list, [mock.call("test1url"), mock.call("test2url")])
        # test post is called
        self.assertEqual(mock_post.return_value.prepare.call_args_list,
                         [
                             mock.call((service1, "postB", 1494880615), 'post 1 title', 'httpd://test1.com'),
                             mock.call((service1, "postA", 1500527415), 'post 2 title', 'httpd://test2.com'),
                             mock.call((service2, "postA", 1500527415), 'post 2 title', 'httpd://test2.com')])
        mock_post.return_value.post.assert_called_once_with('test1UserKey', 'test1UserSecret')
        # test store is called to save data
        self.assertEquals(mock_config.return_value.__setitem__.call_args_list,
                          [mock.call('service1',
                                     SERVICE('service1', 'test1url', 5, STORE('service1', 'postA', 1500527415))),
                           mock.call('service2',
                                     SERVICE('service2', 'test2url', 1, STORE('service2', 'postA', 1500527415)))
                           ])
        # test write is called
        mock_config.return_value.writeStore.assert_called_once_with()

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
            print index, ' ', case

            # when - test with None store
            result = cleanup_feeds(case.store, case.numItems, case.data)
            # then
            self.assertEqual(list(result), case.result)


if __name__ == "__main__":
    unittest.main(TestProcess)
