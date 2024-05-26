"""
Backend classes to action changes on a device via NETCONF
"""

import logging
import os
import sqlite3
from dataclasses import dataclass

import xmltodict
from jinja2 import Environment, FileSystemLoader
from ncclient import manager

from app.exceptions import (
    CannotEdit,
    InvalidCredential,
    InvalidData,
    InvalidDeviceType,
)
from app.models import DeviceCapability, InterfaceConfig

log_level = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper())
logging.basicConfig(level=log_level)

env = Environment(loader=FileSystemLoader("app/templates"))


def get_credentials(credential: str) -> tuple:
    """
    Get credentials from environment base on a type
    Args:
        credential (str): type of credential to retreive
    Returns:
        tuple (username, password)
    """
    try:
        return (
            os.environ[f"{credential.upper()}_USERNAME"],
            os.environ[f"{credential.upper()}_PASSWORD"],
        )
    except KeyError as e:
        raise InvalidCredential(credential) from e


@dataclass
class ConnectionManager:
    """
    Class to manage how to connect to the device via ncclient
    """

    timeout: int = 30
    hostkey_verify: bool = False
    look_for_keys: bool = False

    def format_params(
        self, host: str, device_type: str, username: str, password: str
    ) -> dict:
        """Format the manager params dict for ncclient manager.connect"""
        return {
            "host": host,
            "username": username,
            "password": password,
            "timeout": self.timeout,
            "hostkey_verify": self.hostkey_verify,
            "look_for_keys": self.look_for_keys,
            "device_params": {"name": device_type},
        }


@dataclass
class Device:
    """
    A class to manage parameters to connect to a device and
    how to get/edit the config
    """

    host: str
    credential: str

    def __post_init__(self):
        connection_manager = ConnectionManager()
        username, password = get_credentials(self.credential)
        self.device_type = self.get_device_type(
            connection_manager, username, password
        )
        logging.info(
            "Detected %s as device type: %s", self.host, self.device_type
        )
        self.manager_params = connection_manager.format_params(
            self.host, self.device_type, username, password
        )

    def save_device_type(self, device_type: str) -> None:
        """
        Store the device type so we dont need determine it again
        Args:
            device_type (str): device type to store with self.host
        """
        conn = sqlite3.connect("netconf.db")
        cursor = conn.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS device_info ( "
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "host TEXT NOT NULL, "
            "device_type TEXT NOT NULL)"
        )
        cursor.execute(
            "INSERT INTO device_info (host, device_type) VALUES (?, ?)",
            (self.host, device_type),
        )
        conn.commit()
        conn.close()

    def fetch_device_type(self) -> str:
        """
        Fetch device type from db if its there
        Returns:
            device type (str)
        """
        conn = sqlite3.connect("netconf.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT device_type FROM device_info WHERE host = ?", (self.host,)
        )
        row = cursor.fetchone()
        conn.close()
        return row[0]

    def get_device_type(
        self,
        connection_manager: ConnectionManager,
        username: str,
        password: str,
    ) -> str:
        """
        Determine the ncclient device type from the NETCONF capabilities
        Args:
            connection_manager (ConnectionManager): used for manager params
            username (str): to connect to device
            password (str): to connect to device
        Returns:
            device_type (str): ncclient device type
        Raises:
            InvalidDeviceType if we can't get a device type
        """
        try:
            return self.fetch_device_type()
        except (TypeError, sqlite3.OperationalError):
            pass

        default_manager_params = connection_manager.format_params(
            self.host, "default", username, password
        )
        with manager.connect(**default_manager_params) as mgr:
            for capability in DeviceCapability:
                if any(
                    capability.value in server_capability
                    for server_capability in mgr.server_capabilities
                ):
                    self.save_device_type(capability.name.lower())
                    return capability.name.lower()

        raise InvalidDeviceType("Could not determine a device type for host")

    def get_config(
        self, ncclient_manager: manager.Manager, rendered_config: str
    ) -> dict:
        """
        Get the running config with a filter
        returns a dict from the xml data
        """
        response = ncclient_manager.get_config(
            source="running", filter=rendered_config
        )
        xml_data = response.data_xml
        return xmltodict.parse(xml_data)

    def edit_config(
        self, ncclient_manager: manager.Manager, rendered_config: str
    ) -> None:
        """Edit the candidate config and commit the change"""
        ncclient_manager.edit_config(
            target="candidate", config=rendered_config
        )
        ncclient_manager.commit()


@dataclass
class InterfaceManager:
    """An interface object on a device"""

    device: Device

    def validate_data(self, json_data: dict) -> None:
        """
        Validate the json data contains what we need based on what
        template we used
        Raises:
            InvalidData when the data is not valid for the device tpye
        """
        if self.device.device_type == "iosxr":
            if (
                json_data.get("data", {}).get("interface-configurations")
                is None
            ):
                raise InvalidData(json_data)
        else:
            raise InvalidDeviceType(
                "Cannot validate data for device type "
                f"{self.device.device_type}"
            )

    def check_exists(self, interface_name: str) -> bool:
        """
        Check if the interface exists
        Args:
            interface_name (str): name of the interface to check
        Returns:
            boolean
        """
        try:
            self.get_one(interface_name)
        except InvalidData:
            return False

        return True

    def get_one(self, interface_name: str) -> dict:
        """
        Get config of a single interface
        Args:
            interface_name (str): name of the interface to check
        Returns:
            dict
        """
        with manager.connect(**self.device.manager_params) as ncclient_manager:
            template_name = f"{self.device.device_type}_get_interface.xml.j2"
            template = env.get_template(template_name)
            rendered_config = template.render(interface_name=interface_name)
            json_data = self.device.get_config(
                ncclient_manager, rendered_config
            )
            self.validate_data(json_data)
            return json_data

    def get_all(self) -> dict:
        """
        Get config of all interfaces
        Returns:
            dict
        """
        with manager.connect(**self.device.manager_params) as ncclient_manager:
            template_name = f"{self.device.device_type}_get_interfaces.xml.j2"
            template = env.get_template(template_name)
            rendered_config = template.render()
            json_data = self.device.get_config(
                ncclient_manager, rendered_config
            )
            self.validate_data(json_data)
            return json_data

    def create(
        self, interface_config: InterfaceConfig, dry_run: bool = False
    ) -> dict:
        """
        Create a single interface on the device
        Args:
            interface_config (InterfaceConfig): config of interface to add
        Returns:
            dict
        """
        if self.check_exists(interface_config.interface_name):
            raise CannotEdit(
                f"Interface {interface_config.interface_name} already exists"
            )

        with manager.connect(**self.device.manager_params) as ncclient_manager:
            template_name = (
                f"{self.device.device_type}_create_interface.xml.j2"
            )
            template = env.get_template(template_name)
            rendered_config = template.render(**interface_config.__dict__)
            if dry_run:
                return rendered_config

            return self.device.edit_config(ncclient_manager, rendered_config)

    def delete(self, interface_name: str, dry_run: bool = False) -> dict:
        """
        Delete a single interface from the device config
        Args:
            interface_name (str): name of the interface to check
        Returns:
            dict
        """
        if not self.check_exists(interface_name):
            raise CannotEdit(f"Interface {interface_name} does not exist")

        with manager.connect(**self.device.manager_params) as ncclient_manager:
            template_name = (
                f"{self.device.device_type}_delete_interface.xml.j2"
            )
            template = env.get_template(template_name)
            rendered_config = template.render(interface_name=interface_name)
            if dry_run:
                return rendered_config

            return self.device.edit_config(ncclient_manager, rendered_config)
