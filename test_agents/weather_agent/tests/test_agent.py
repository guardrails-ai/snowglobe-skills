import unittest

from weather_agent import WeatherAgent, WeatherClient, MockWeatherBackend, respond


def _agent():
    return WeatherAgent(client=WeatherClient(backend=MockWeatherBackend()))


class AgentTests(unittest.TestCase):
    def test_current(self):
        a = _agent()
        out = a.chat("what's the weather in tokyo")
        self.assertIn("Tokyo", out)
        self.assertIn("68", out)

    def test_forecast(self):
        a = _agent()
        out = a.chat("forecast for london")
        self.assertIn("forecast", out)

    def test_alerts(self):
        a = _agent()
        out = a.chat("alerts in london")
        self.assertIn("wind advisory", out)

    def test_compare(self):
        a = _agent()
        out = a.chat("compare tokyo and london")
        self.assertIn("warmer", out.lower())

    def test_summary(self):
        a = _agent()
        out = a.chat("summary for tokyo")
        self.assertIn("avg", out)

    def test_unknown_city(self):
        a = _agent()
        out = a.chat("how about atlantis")
        self.assertIn("Tell me a city", out)

    def test_max_5_calls(self):
        out = respond("alerts and forecast and summary for london",
                      WeatherClient(backend=MockWeatherBackend()))
        self.assertLessEqual(len(out["tool_calls"]), 5)
        self.assertGreaterEqual(len(out["tool_calls"]), 1)


if __name__ == "__main__":
    unittest.main()
