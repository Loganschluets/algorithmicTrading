import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from main import is_valid_date, get_last_n_trading_days, configure_call, make_api_call

class TestMain(unittest.TestCase):

    def test_is_valid_date(self):
        self.assertTrue(is_valid_date("01-02-2024"))   #correct case for a valid day 
        self.assertFalse(is_valid_date("2024-01-01"))  #testing an invalid formatting for the date
        self.assertFalse(is_valid_date("13-01-2024"))  #testing an invalid month
        self.assertFalse(is_valid_date("12-99-2024"))  #testing an invalid day

    def test_get_last_n_trading_days(self):
        holidays = [
            '2024-01-01',
            '2024-01-15',
            '2024-02-19',
        ]
        with patch('main.HOLIDAYS', holidays):
            trading_days = get_last_n_trading_days(5)
            #checks to make sure that 5 days are returned when 5 days are asked for
            self.assertEqual(len(trading_days), 5)
            for day in trading_days:
                self.assertNotIn(day.strftime('%Y-%m-%d'), holidays)  #checks if any of the days are a holiday
                self.assertNotEqual(day.weekday(), 5)  #checks if any of the days returned are Saturday (5 is code for Saturday)
                self.assertNotEqual(day.weekday(), 6)  #checks if any of the days returned are Sunday (6 is code for Sunday)

    def test_configure_call(self):
        ticker = 'AAPL'
        date = datetime(2024, 1, 1)
        multiplier = '15'
        interval = 'minute'
        url = configure_call(ticker, date, multiplier, interval)
        expected_url = (
            f'https://api.polygon.io/v2/aggs/ticker/{ticker}/range/{multiplier}/{interval}/2024-01-01/2024-01-01?apiKey=RpgkwjK4c_F4MwwPkD8LPoxJEsSTrnFs'
        )
        self.assertEqual(url, expected_url)

    @patch('main.requests.get')
    def test_make_api_call(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': [
                {'t': 123456789, 'v': 100, 'vw': 150.5, 'o': 150, 'c': 151, 'h': 152, 'l': 149, 'n': 10},
            ]
        }
        mock_get.return_value = mock_response

        result = make_api_call('AAPL', datetime(2024, 1, 1), '1', 'minute')
        self.assertTrue(result)
        mock_get.assert_called_once()

if __name__ == '__main__':
    unittest.main()
