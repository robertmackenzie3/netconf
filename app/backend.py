"""
Backend classes to action changes on a device via NETCONF
"""

import os
from dataclasses import dataclass

import xmltodict
from jinja2 import Environment, FileSystemLoader
from ncclient import manager

from app.exceptions import CannotEdit
from app.models import InterfaceConfig

env = Environment(loader=FileSystemLoader("app/templates"))


@dataclass
class ManagerParams:
    """
    Class to manage how to connect to the device via ncclient
    """

    host: str
    device_type: str
    port: int = 830
    timeout: int = 30
    hostkey_verify: bool = False
    look_for_keys: bool = False

    def __post_init__(self):
        self.username = os.environ["DEVICE_USERNAME"]
        self.password = os.environ["DEVICE_PASSWORD"]

    def format(self):
        """Format the manager params dict for ncclient manager.connect"""
        return {
            "host": self.host,
            "port": self.port,
            "username": self.username,
            "password": self.password,
            "timeout": self.timeout,
            "hostkey_verify": self.hostkey_verify,
            "look_for_keys": self.look_for_keys,
            "device_params": {"name": self.device_type},
        }


@dataclass
class BaseObject:
    """
    A base class for an object that can be retrieved or editted on a device
    """

    manager_params: ManagerParams

    def _get_config(self, conn, rendered_config):
        response = conn.get_config(source="running", filter=rendered_config)
        xml_data = response.data_xml
        return xmltodict.parse(xml_data)

    def _edit_config(self, conn, rendered_config):
        conn.edit_config(target="candidate", config=rendered_config)
        conn.commit()


@dataclass
class Interface(BaseObject):
    """An interface object on a device"""

    def _check_exists(self, interface_name: str) -> bool:
        """
        Check if the interface exists
        Args:
            interface_name (str): name of the interface to check
        Returns:
            boolean
        """
        json_data = self.get_one(interface_name)
        return bool(json_data.get("data", {}).get("interface-configurations"))

    def get_one(self, interface_name: str) -> dict:
        """
        Get config of a single interface
        Args:
            interface_name (str): name of the interface to check
        Returns:
            dict
        """
        with manager.connect(**self.manager_params.format()) as conn:
            template = env.get_template(
                f"{self.manager_params.device_type}_get_interface.xml.j2"
            )
            rendered_config = template.render(interface_name=interface_name)
            return self._get_config(conn, rendered_config)

    def get_all(self) -> dict:
        """
        Get config of all interfaces
        Returns:
            dict
        """
        with manager.connect(**self.manager_params.format()) as conn:
            template = env.get_template(
                f"{self.manager_params.device_type}_get_interfaces.xml.j2"
            )
            rendered_config = template.render()
            return self._get_config(conn, rendered_config)

    def add(self, interface_config: InterfaceConfig) -> dict:
        """
        Add a single interface to the device config
        Args:
            interface_config (InterfaceConfig): config of interface to add
        Returns:
            dict
        """
        if self._check_exists(interface_config.interface_name):
            raise CannotEdit(
                f"Interface {interface_config.interface_name} already exists"
            )

        with manager.connect(**self.manager_params.format()) as conn:
            template = env.get_template(
                f"{self.manager_params.device_type}_create_interface.xml.j2"
            )
            rendered_config = template.render(**interface_config.__dict__)
            return self._edit_config(conn, rendered_config)

    def remove(self, interface_name: str) -> dict:
        """
        Remove a single interface from the device config
        Args:
            interface_name (str): name of the interface to check
        Returns:
            dict
        """
        if not self._check_exists(interface_name):
            raise CannotEdit(f"Interface {interface_name} does not exist")

        with manager.connect(**self.manager_params.format()) as conn:
            template = env.get_template(
                f"{self.manager_params.device_type}_delete_interface.xml.j2"
            )
            rendered_config = template.render(interface_name=interface_name)
            return self._edit_config(conn, rendered_config)
