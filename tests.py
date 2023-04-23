import unittest
import requests
#
from get_values import get_value
from config import EUR, USD


class TestsGetValutes(unittest.TestCase):
    expected_date_str = '21.04.2023'

    def test_get_value(self):
        get_value_result = get_value([EUR, USD], date=self.expected_date_str)
        expected_result = {'date': self.expected_date_str, 'EUR': ('89.4638', 1), 'USD': ('81.6188', 1)}
        self.assertEqual(expected_result, get_value_result)

    def test_root_status_code(self):
        response = requests.get('http://127.0.0.1:5000')
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main(exit=True)
