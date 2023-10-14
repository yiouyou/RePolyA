# filename: test_recommend.py

import unittest
from recommend import get_service_price, cheapest_option

class TestRecommend(unittest.TestCase):

    def setUp(self):
        self.path_of_service_options = '/home/sz/RePolyA/repolya/_workspace/_autogen/service_options'

    def test_get_service_price(self):
        self.assertEqual(get_service_price(self.path_of_service_options, 'linux-standard-s2-payg'), 0.19)
        self.assertEqual(get_service_price(self.path_of_service_options, 'windows-basic-b2-payg'), 0.15)
        self.assertIsNone(get_service_price(self.path_of_service_options, 'nonexistent-service'))

    def test_cheapest_option(self):
        self.assertEqual(cheapest_option(self.path_of_service_options, 'linux-standard-s3-payg'), ('linux-standard-s1-payg', 0.095))
        self.assertEqual(cheapest_option(self.path_of_service_options, 'windows-basic-b3-payg'), ('windows-basic-b1-payg', 0.075))
        self.assertEqual(cheapest_option(self.path_of_service_options, 'windows-free-f1-payg'), (None, None))

if __name__ == '__main__':
    unittest.main()