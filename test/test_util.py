import unittest
import util

class TestUtil(unittest.TestCase):

    def test_encode(self):
        self.assertEqual(None, util.encode(None))
        self.assertEqual(None, util.encode(""))
        self.assertEqual(None, util.encode(" "))
        self.assertEqual("TEST", util.encode("TEST"))
        self.assertEqual("TEST", util.encode("test"))
        self.assertEqual("TEST", util.encode("Test"))
        self.assertEqual("TEST", util.encode(" Test "))
        self.assertEqual("TEST TEST", util.encode(" Test test "))

if __name__ == "__main__":
    unittest.main(TestUtil)