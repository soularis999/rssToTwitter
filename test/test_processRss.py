import unittest
import mock

from processRss import process, DRY_RUN
from feedConfig import SERVICE
from collections import namedtuple


class TestProcess(unittest.TestCase):
    @mock.patch("processRss.parse")
    @mock.patch("processRss.TwitterPost")
    @mock.patch("processRss.Config")
    def test_process(self, mock_config, mock_post, mock_parser):
        # when
        mock_config.return_value.mainService.return_value.appTwitterKey = "test1AppKey"
        mock_config.return_value.mainService.return_value.appTwitterSecret = "test1AppSecret"
        mock_config.return_value.mainService.return_value.userTwitterKey = "test1UserKey"
        mock_config.return_value.mainService.return_value.userTwitterSecret = "test1UserSecret"
        mock_config.return_value.services.return_value = ["service1", "service2"]
        mock_config.return_value.__getitem__.side_effect = (
            SERVICE("test1url", 5, None, None), SERVICE("test2url", 1, None, None))

        timeTuple = namedtuple("TimeTuple", "tm_year tm_mon tm_mday tm_hour tm_min tm_sec")
        mock_parser.return_value = {
            "status": 200,
            "entries": [
                {
                    "id": "post2",
                    "title": "post 2 title",
                    "published_parsed": timeTuple(2017, 7, 20, 5, 10, 15),
                    "link": "httpd://test2.com"
                },
                {
                    "id": "post1",
                    "title": "post 1 title",
                    "published_parsed": timeTuple(2017, 5, 15, 20, 36, 55),
                    "link": "httpd://test1.com"
                }]
        }

        process("file1", "file2")

        # then
        # test config open is called
        mock_config.return_value.open.assert_called_once_with('file1', 'file2')
        # test creating twitter post
        mock_post.assert_called_once_with("test1AppKey", "test1AppSecret", DRY_RUN)

        # test get is called

        self.assertEquals(mock_config.return_value.__getitem__.call_args_list,
                          [mock.call("service1"), mock.call("service2")])
        # test parse is called to get feed
        self.assertEquals(mock_parser.call_args_list, [mock.call("test1url"), mock.call("test2url")])
        # test post is called
        self.assertEqual(mock_post.return_value.post.call_args_list,
                         [mock.call('test1UserKey', 'test1UserSecret', 'post 2 title httpd://test2.com'),
                          mock.call('test1UserKey', 'test1UserSecret', 'post 1 title httpd://test1.com'),
                          mock.call('test1UserKey', 'test1UserSecret', 'post 2 title httpd://test2.com')])
        # test store is called to save data
        self.assertEquals(mock_config.return_value.__setitem__.call_args_list,
                          [mock.call('service1', SERVICE("test1url", 5, "post2", 1500527415L)),
                           mock.call('service2', SERVICE("test2url", 1, "post2", 1500527415L))])
        # test write is called
        mock_config.return_value.writeStore.assert_called_once_with()


if __name__ == "__main__":
    unittest.main(TestProcess)
