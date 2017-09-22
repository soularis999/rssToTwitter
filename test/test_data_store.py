import os
import unittest
import mock

from feed_config import MAIN, AWS_STORAGE
from data_store import FileBasedDataStore, S3BasedDataStore, STORE

TMP_STORE_FILE_PATH = "/tmp/twStore"


class TestDataStore(unittest.TestCase):
    def setUp(self):
        if os.path.exists(TMP_STORE_FILE_PATH):
            os.remove(TMP_STORE_FILE_PATH)

    def test_set_and_get(self):
        config = FileBasedDataStore(MAIN(15, TMP_STORE_FILE_PATH))

        with self.assertRaises(SystemError) as e:
            config["T2"] = None
            self.assertEqual(e.exception.message, "Store is empty for T2")

        with self.assertRaises(SystemError) as e:
            config[None] = None
            self.assertEqual(e.exception.message, "Section name is empty")

    def test_writing(self):
        config = FileBasedDataStore(MAIN(15, TMP_STORE_FILE_PATH))

        # then
        self.assertEqual(len(config), 0)

        # when
        config["T1"] = STORE(None, None, None)
        config["T2"] = STORE("T2", None, None)
        config["T3"] = STORE("T3", "id3", None)
        config["T4"] = STORE("T4", None, 5555545)
        config["T5"] = STORE("T5", "id5", 444555666)
        config["T6"] = STORE("T6", "id6", 555666777)
        config.write_store()

        # then
        self.assertTrue(os.path.exists(TMP_STORE_FILE_PATH))
        self.assertEqual(sorted(open(TMP_STORE_FILE_PATH).readlines()),
                         ["T1||\n", "T2||\n", "T3|id3|\n", "T4||5555545\n", "T5|id5|444555666\n", "T6|id6|555666777\n"])

        # when - try reading the file back
        self.assertEqual(len(config), 6)
        config["T4"] = STORE("T4", "id4New", 11111111)
        config["T5"] = STORE("T5", "id5New", 22222222)
        config._read_store()

        # then
        self.assertEqual(len(config), 6)
        self.assertIsNone(config['T1'])
        self.assertIsNone(config['T2'])
        self.assertIsNone(config['T3'])
        self.assertIsNone(config['T4'])

        self.assertEqual(config['T5'].serviceName, 'T5')
        self.assertEqual(config['T5'].lastProcessedId, 'id5')
        self.assertEqual(config['T5'].lastProcessedUpdateTimestamp, 444555666)

        self.assertEqual(config['T6'].serviceName, 'T6')
        self.assertEqual(config['T6'].lastProcessedId, 'id6')
        self.assertEqual(config['T6'].lastProcessedUpdateTimestamp, 555666777)

    def test_dry_run(self):
        config = FileBasedDataStore(MAIN(15, TMP_STORE_FILE_PATH), dry_run=True)
        config["T2"] = STORE("T2", "id2", None)
        config["T3"] = STORE("T3", None, 5555545)
        config["T4"] = STORE("T4", "id4", 444555666)
        config["T5"] = STORE("T5", "id5", 555666777)

        # when
        config.write_store()

        # then
        self.assertFalse(os.path.exists(TMP_STORE_FILE_PATH))

    @mock.patch("boto3.resource")
    def test_s3_store(self, mock_boto):
        #        self._connection = boto3.resource('s3', aws_access_key_id=aws_config.awsAccessKey,
        #                                   aws_secret_access_key=aws_config.awsAccessSecret)
        # self._connection.Bucket(aws_config.awsBucket).download_file(file_name, config.storeFileName)
        resource_mock = mock.MagicMock()
        bucket_mock = mock.MagicMock()
        mock_boto.return_value = resource_mock
        resource_mock.Bucket.return_value = bucket_mock

        config = S3BasedDataStore(MAIN(15, TMP_STORE_FILE_PATH), AWS_STORAGE("awskey", "awssecret", "awsbucket"))

        # then
        self.assertEqual(len(config), 0)

        # when
        config["T1"] = STORE(None, None, None)
        config["T2"] = STORE("T2", None, None)
        config["T3"] = STORE("T3", "id3", None)
        config["T4"] = STORE("T4", None, 5555545)
        config["T5"] = STORE("T5", "id5", 444555666)
        config["T6"] = STORE("T6", "id6", 555666777)
        config.write_store()

        # then
        self.assertEqual(mock_boto.call_args,
                         mock.call('s3', aws_access_key_id='awskey', aws_secret_access_key='awssecret'))
        self.assertEqual(resource_mock.Bucket.call_args, mock.call("awsbucket"))
        self.assertEqual(bucket_mock.download_file.call_args, mock.call("twStore", "/tmp/twStore"))
        self.assertEqual(bucket_mock.upload_file.call_args, mock.call("/tmp/twStore", "twStore"))

        self.assertTrue(os.path.exists(TMP_STORE_FILE_PATH))
        self.assertEqual(sorted(open(TMP_STORE_FILE_PATH).readlines()),
                         ["T1||\n", "T2||\n", "T3|id3|\n", "T4||5555545\n", "T5|id5|444555666\n", "T6|id6|555666777\n"])

        # when - try reading the file back
        self.assertEqual(len(config), 6)
        config["T4"] = STORE("T4", "id4New", 11111111)
        config["T5"] = STORE("T5", "id5New", 22222222)
        config._read_store()

        # then
        self.assertEqual(len(config), 6)
        self.assertIsNone(config['T1'])
        self.assertIsNone(config['T2'])
        self.assertIsNone(config['T3'])
        self.assertIsNone(config['T4'])

        self.assertEqual(config['T5'].serviceName, 'T5')
        self.assertEqual(config['T5'].lastProcessedId, 'id5')
        self.assertEqual(config['T5'].lastProcessedUpdateTimestamp, 444555666)

        self.assertEqual(config['T6'].serviceName, 'T6')
        self.assertEqual(config['T6'].lastProcessedId, 'id6')
        self.assertEqual(config['T6'].lastProcessedUpdateTimestamp, 555666777)


if __name__ == "__main__":
    unittest.main(TestDataStore)
