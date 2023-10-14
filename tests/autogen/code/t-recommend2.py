# filename: t-recommend2.py

import sys
sys.path.append('./code')
from recommend2 import get_service_price, cheapest_option
import unittest

class TestRecommend2(unittest.TestCase):
    def setUp(self):
        self.path_of_service_options = '/home/sz/RePolyA/repolya/_workspace/_autogen/service_options'

    def test_get_service_price_case1(self):
        service = 'windows-basic-b3-payg'
        expected_output = ('windows-basic-b1-payg', 0.075)
        self.assertEqual(cheapest_option(self.path_of_service_options, service), expected_output)

    def test_get_service_price_case2(self):
        service = 'linux-standard-s3-payg'
        expected_output = ('linux-standard-s1-payg', 0.095)
        self.assertEqual(cheapest_option(self.path_of_service_options, service), expected_output)

    def test_get_service_price_case3(self):
        service = 'nonexistent-service'
        expected_output = (None, None)
        self.assertEqual(cheapest_option(self.path_of_service_options, service), expected_output)

if __name__ == '__main__':
    unittest.main()