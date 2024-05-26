"""
Test for the fastapi app frontend
"""

import os
from unittest import TestCase
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from app.main import app

from tests.fixtures import (
    IOSXR_CAPABILITIES,
    IOSXR_CREATE_INTERFACE,
    IOSXR_DELETE_INTERFACE,
    IOSXR_GET_INTERFACE,
    IOSXR_GET_INTERFACE_MISSING,
    IOSXR_GET_INTERFACES,
)


class TestMain(TestCase):
    """
    Test the generic endpoints in the fastapi app
    """

    @classmethod
    def setUpClass(cls):
        cls.env_patcher = patch.dict(
            os.environ,
            {"DEFAULT_USERNAME": "test", "DEFAULT_PASSWORD": "test"},
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


class TestInterface(TestCase):
    """
    Test the interface endpoints in the fastapi app
    """

    @classmethod
    def setUpClass(cls):
        cls.env_patcher = patch.dict(
            os.environ,
            {"DEFAULT_USERNAME": "test", "DEFAULT_PASSWORD": "test"},
        )
        cls.env_patcher.start()
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        cls.env_patcher.stop()

    def setUp(self):
        pass

    @patch("app.backend.Device.get_device_type")
    @patch("app.backend.manager.connect")
    def test_get_interface(self, mock_manager, mock_device_type):
        """Test we can get an interface"""
        mock_config = MagicMock()
        mock_config.data_xml = IOSXR_GET_INTERFACE
        mock_manager_obj = MagicMock()
        mock_manager_obj.get_config.return_value = mock_config
        mock_manager.return_value.__enter__.return_value = mock_manager_obj
        mock_device_type.return_value = "iosxr"

        response = self.client.get(
            "/interface",
            params={
                "host": "test",
                "interface_name": "vlan1",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(
            response.json(),
            {
                "data": {
                    "@xmlns": "urn:ietf:params:xml:ns:netconf:base:1.0",
                    "@xmlns:nc": "urn:ietf:params:xml:ns:netconf:base:1.0",
                    "interface-configurations": {
                        "@xmlns": "http://cisco.com/ns/yang/Cisco-IOS-XR-ifmgr-cfg",
                        "interface-configuration": {
                            "active": "act",
                            "interface-name": "Loopback0",
                            "interface-virtual": None,
                            "ipv4-network": {
                                "@xmlns": "http://cisco.com/ns/yang/Cisco-IOS-XR-ipv4-io-cfg",
                                "addresses": {
                                    "primary": {
                                        "address": "10.0.0.1",
                                        "netmask": "255.255.255.255",
                                    }
                                },
                            },
                        },
                    },
                }
            },
        )

    @patch("app.backend.Device.save_device_type")
    @patch("app.backend.manager.connect")
    def test_get_device_type(self, mock_manager, _):
        """Test we can get an interface"""
        mock_config = MagicMock()
        mock_config.data_xml = IOSXR_GET_INTERFACE
        mock_manager_obj = MagicMock()
        mock_manager_obj.get_config.return_value = mock_config
        mock_manager_obj.server_capabilities = IOSXR_CAPABILITIES
        mock_manager.return_value.__enter__.return_value = mock_manager_obj

        response = self.client.get(
            "/interface",
            params={
                "host": "test",
                "interface_name": "vlan1",
            },
        )
        self.assertEqual(response.status_code, 200)

    @patch("app.backend.Device.save_device_type")
    @patch("app.backend.manager.connect")
    def test_get_device_type_fail(self, mock_manager, _):
        """Test we can get an interface"""
        mock_config = MagicMock()
        mock_config.data_xml = IOSXR_GET_INTERFACE
        mock_manager_obj = MagicMock()
        mock_manager_obj.get_config.return_value = mock_config
        mock_manager_obj.server_capabilities = []
        mock_manager.return_value.__enter__.return_value = mock_manager_obj

        response = self.client.get(
            "/interface",
            params={
                "host": "test",
                "interface_name": "vlan1",
            },
        )
        self.assertDictEqual(
            response.json(),
            {
                "detail": (
                    "Exception InvalidDeviceType: "
                    "Could not determine a device type for host"
                )
            },
        )

    def test_get_interface_invalid_credential(self):
        """Test we fail on an invalid device type"""
        response = self.client.get(
            "/interface",
            params={
                "host": "test",
                "interface_name": "vlan1",
                "credential": "bad",
            },
        )
        self.assertEqual(response.status_code, 422)
        self.assertListEqual(
            response.json()["detail"][0]["loc"], ["query", "credential"]
        )

    @patch("app.backend.Device.get_device_type")
    @patch("app.backend.manager.connect")
    def test_get_interface_missing(self, mock_manager, mock_device_type):
        """Test we get a 404 when interface is missing"""
        mock_config = MagicMock()
        mock_config.data_xml = IOSXR_GET_INTERFACE_MISSING
        mock_manager_obj = MagicMock()
        mock_manager_obj.get_config.return_value = mock_config
        mock_manager.return_value.__enter__.return_value = mock_manager_obj
        mock_device_type.return_value = "iosxr"

        response = self.client.get(
            "/interface",
            params={
                "host": "test",
                "interface_name": "vlan1",
            },
        )
        self.assertEqual(response.status_code, 404)

    def test_get_interface_missing_param(self):
        """Test we get a 422 when param is missing"""
        response = self.client.get(
            "/interface",
            params={"host": "test"},
        )
        self.assertEqual(response.status_code, 422)
        self.assertDictEqual(
            response.json(),
            {
                "detail": [
                    {
                        "input": None,
                        "loc": ["query", "interface_name"],
                        "msg": "Field required",
                        "type": "missing",
                    }
                ]
            },
        )

    @patch("app.backend.Device.get_device_type")
    @patch("app.backend.manager.connect")
    def test_get_interfaces(self, mock_manager, mock_device_type):
        """Test we can get interfaces"""
        mock_config = MagicMock()
        mock_config.data_xml = IOSXR_GET_INTERFACES
        mock_manager_obj = MagicMock()
        mock_manager_obj.get_config.return_value = mock_config
        mock_manager.return_value.__enter__.return_value = mock_manager_obj
        mock_device_type.return_value = "iosxr"

        response = self.client.get(
            "/interfaces",
            params={"host": "test"},
        )
        response_dict = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(
                response_dict["data"]["interface-configurations"][
                    "interface-configuration"
                ]
            ),
            12,
        )

    @patch("app.backend.Device.get_device_type")
    @patch("app.backend.manager.connect")
    def test_create_interface(self, mock_manager, mock_device_type):
        """Test we can create an interface"""
        mock_config = MagicMock()
        mock_config.data_xml = IOSXR_GET_INTERFACE_MISSING
        mock_manager_obj = MagicMock()
        mock_manager_obj.get_config.return_value = mock_config
        mock_manager.return_value.__enter__.return_value = mock_manager_obj
        mock_device_type.return_value = "iosxr"

        response = self.client.post(
            "/interface",
            params={"host": "test"},
            json={
                "interface_name": "vlan1",
                "address": "10.0.0.1",
                "netmask": "255.255.255.255",
            },
        )
        self.assertEqual(response.status_code, 200)
        mock_manager_obj.edit_config.assert_called_once_with(
            target="candidate",
            config=IOSXR_CREATE_INTERFACE,
        )

    @patch("app.backend.Device.get_device_type")
    @patch("app.backend.manager.connect")
    def test_create_interface_exists(self, mock_manager, mock_device_type):
        """Test we cant create an interface if it exists"""
        mock_config = MagicMock()
        mock_config.data_xml = IOSXR_GET_INTERFACE
        mock_manager_obj = MagicMock()
        mock_manager_obj.get_config.return_value = mock_config
        mock_manager.return_value.__enter__.return_value = mock_manager_obj
        mock_device_type.return_value = "iosxr"

        response = self.client.post(
            "/interface",
            params={"host": "test"},
            json={
                "interface_name": "vlan1",
                "address": "10.0.0.1",
                "netmask": "255.255.255.255",
            },
        )
        self.assertEqual(response.status_code, 409)
        mock_manager_obj.edit_config.assert_not_called()

    @patch("app.backend.Device.get_device_type")
    @patch("app.backend.manager.connect")
    def test_create_interface_dry_run(self, mock_manager, mock_device_type):
        """Test we dont create an interface when dry run"""
        mock_config = MagicMock()
        mock_config.data_xml = IOSXR_GET_INTERFACE_MISSING
        mock_manager_obj = MagicMock()
        mock_manager_obj.get_config.return_value = mock_config
        mock_manager.return_value.__enter__.return_value = mock_manager_obj
        mock_device_type.return_value = "iosxr"

        response = self.client.post(
            "/interface",
            params={"host": "test", "dry_run": True},
            json={
                "interface_name": "vlan1",
                "address": "10.0.0.1",
                "netmask": "255.255.255.255",
            },
        )
        self.assertEqual(response.status_code, 200)
        mock_manager_obj.edit_config.assert_not_called()

    @patch("app.backend.Device.get_device_type")
    @patch("app.backend.manager.connect")
    def test_delete_interface(self, mock_manager, mock_device_type):
        """Test we can delete an interface"""
        mock_config = MagicMock()
        mock_config.data_xml = IOSXR_GET_INTERFACE
        mock_manager_obj = MagicMock()
        mock_manager_obj.get_config.return_value = mock_config
        mock_manager.return_value.__enter__.return_value = mock_manager_obj
        mock_device_type.return_value = "iosxr"

        response = self.client.delete(
            "/interface",
            params={
                "host": "test",
                "interface_name": "vlan1",
            },
        )
        self.assertEqual(response.status_code, 200)
        mock_manager_obj.edit_config.assert_called_once_with(
            target="candidate",
            config=IOSXR_DELETE_INTERFACE,
        )

    @patch("app.backend.Device.get_device_type")
    @patch("app.backend.manager.connect")
    def test_delete_interface_missing(self, mock_manager, mock_device_type):
        """Test we cant delete an interface if its missing"""
        mock_config = MagicMock()
        mock_config.data_xml = IOSXR_GET_INTERFACE_MISSING
        mock_manager_obj = MagicMock()
        mock_manager_obj.get_config.return_value = mock_config
        mock_manager.return_value.__enter__.return_value = mock_manager_obj
        mock_device_type.return_value = "iosxr"

        response = self.client.delete(
            "/interface",
            params={
                "host": "test",
                "interface_name": "vlan1",
            },
        )
        self.assertEqual(response.status_code, 404)
        mock_manager_obj.edit_config.assert_not_called()

    @patch("app.backend.Device.get_device_type")
    @patch("app.backend.manager.connect")
    def test_delete_interface_dry_run(self, mock_manager, mock_device_type):
        """Test we dont delete an interface when dry_run"""
        mock_config = MagicMock()
        mock_config.data_xml = IOSXR_GET_INTERFACE
        mock_manager_obj = MagicMock()
        mock_manager_obj.get_config.return_value = mock_config
        mock_manager.return_value.__enter__.return_value = mock_manager_obj
        mock_device_type.return_value = "iosxr"

        response = self.client.delete(
            "/interface",
            params={
                "host": "test",
                "interface_name": "vlan1",
                "dry_run": True,
            },
        )
        self.assertEqual(response.status_code, 200)
        mock_manager_obj.edit_config.assert_not_called()
