import unittest

from devops_agent import DevOpsAgent, Config, respond


SAMPLE = """
services:
  api:
    version: "1.0.0"
    instances: 2
    healthy: true
  worker:
    version: "0.1.0"
    instances: 1
    healthy: false
"""


def _agent():
    return DevOpsAgent(config=Config.from_string(SAMPLE))


class AgentTests(unittest.TestCase):
    def test_status(self):
        a = _agent()
        out = a.chat("status api")
        self.assertIn("1.0.0", out)

    def test_deploy_chain(self):
        a = _agent()
        out = a.chat("deploy api 1.1.0")
        self.assertIn("1.1.0", out)
        self.assertEqual(a.config.services["api"]["version"], "1.1.0")

    def test_rollback(self):
        a = _agent()
        a.chat("deploy api 1.1.0")
        out = a.chat("rollback api")
        self.assertIn("1.0.0", out)
        self.assertEqual(a.config.services["api"]["version"], "1.0.0")

    def test_logs(self):
        a = _agent()
        out = a.chat("logs api")
        self.assertIn("3", out)

    def test_scale(self):
        a = _agent()
        out = a.chat("scale worker 4")
        self.assertIn("1->4", out)
        self.assertEqual(a.config.services["worker"]["instances"], 4)

    def test_restart(self):
        a = _agent()
        a.chat("restart worker")
        self.assertTrue(a.config.services["worker"]["healthy"])

    def test_healthcheck_all(self):
        a = _agent()
        out = a.chat("healthcheck")
        self.assertIn("worker", out)

    def test_healthcheck_one(self):
        a = _agent()
        out = a.chat("healthcheck worker")
        self.assertIn("False", out)

    def test_unknown(self):
        a = _agent()
        out = a.chat("hello")
        self.assertIn("Try", out)

    def test_max_5_calls(self):
        config = Config.from_string(SAMPLE)
        out = respond("deploy api 2.0", config)
        self.assertLessEqual(len(out["tool_calls"]), 5)


if __name__ == "__main__":
    unittest.main()
