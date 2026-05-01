import unittest

from weather_agent import WeatherClient, MockWeatherBackend


class ClientTests(unittest.TestCase):
    def setUp(self):
        self.client = WeatherClient(backend=MockWeatherBackend())

    def test_current_known(self):
        out = self.client.current("tokyo")
        self.assertEqual(out["temp_f"], 68)

    def test_current_unknown(self):
        self.assertIn("error", self.client.current("atlantis"))

    def test_forecast_length(self):
        self.assertEqual(len(self.client.forecast("london")["days"]), 5)

    def test_alerts_london(self):
        out = self.client.alerts("london")
        self.assertEqual(len(out["alerts"]), 1)

    def test_alerts_clean(self):
        self.assertEqual(self.client.alerts("tokyo")["alerts"], [])


if __name__ == "__main__":
    unittest.main()
