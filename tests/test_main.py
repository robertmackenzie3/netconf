"""
Test for the fastapi app frontend
"""

import os
from unittest import TestCase
from unittest.mock import patch
from fastapi.testclient import TestClient

from app.main import app


class TestMain(TestCase):
    """
    Test the endpoints in the fastapi app
    """

    @classmethod
    def setUpClass(cls):
        cls.env_patcher = patch.dict(
            os.environ,
            {"DEVICE_USERNAME": "test", "DEVICE_PASSWORD": "test"},
        )
        cls.env_patcher.start()
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        cls.env_patcher.stop()

    def setUp(self):
        pass

    def test_healthz(self):
        """Test we can check health of app"""
        response = self.client.get("/healthz")
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json(), {"detail": "Netconf is running"})
