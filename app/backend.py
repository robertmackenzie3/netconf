"""
Backend classes to action changes on a device via NETCONF

Create a device with how to connect, read, edit
create interfacemgt class and pass device in to manager interfaces

"""

import os
from dataclasses import dataclass

import xmltodict
from jinja2 import Environment, FileSystemLoader
from ncclient import manager

from app.exceptions import CannotEdit, InvalidCredential, InvalidData
from app.models import InterfaceConfig

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
    device_type: str
    credential: str

    def __post_init__(self):
        connection_manager = ConnectionManager()
        username, password = get_credentials(self.credential)
        self.manager_params = connection_manager.format_params(
            self.host, self.device_type, username, password
        )

    def validate_data(self, json_data: dict) -> None:
        """
        Validate the json data contains what we need based on device_type
        Raises:
            InvalidData when the data is not valid for the device tpye
        """
        if self.device_type == "iosxr":
            if (
                json_data.get("data", {}).get("interface-configurations")
                is None
            ):
                raise InvalidData(json_data)

        if self.device_type == "nexus":
            if (
                json_data.get("data", {})
                .get("interfaces", {})
                .get("interface")
                is None
            ):
                raise InvalidData(json_data)

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
        json_data = xmltodict.parse(xml_data)
        self.validate_data(json_data)
        return json_data

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

    def _check_exists(self, interface_name: str) -> bool:
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
            template = env.get_template(
                f"{self.device.device_type}_get_interface.xml.j2"
            )
            rendered_config = template.render(interface_name=interface_name)
            return self.device.get_config(ncclient_manager, rendered_config)

    def get_all(self) -> dict:
        """
        Get config of all interfaces
        Returns:
            dict
        """
        with manager.connect(**self.device.manager_params) as ncclient_manager:
            template = env.get_template(
                f"{self.device.device_type}_get_interfaces.xml.j2"
            )
            rendered_config = template.render()
            return self.device.get_config(ncclient_manager, rendered_config)

    def create(self, interface_config: InterfaceConfig) -> dict:
        """
        Create a single interface on the device
        Args:
            interface_config (InterfaceConfig): config of interface to add
        Returns:
            dict
        """
        if self._check_exists(interface_config.interface_name):
            raise CannotEdit(
                f"Interface {interface_config.interface_name} already exists"
            )

        with manager.connect(**self.device.manager_params) as ncclient_manager:
            template = env.get_template(
                f"{self.device.device_type}_create_interface.xml.j2"
            )
            rendered_config = template.render(**interface_config.__dict__)
            return self.device.edit_config(ncclient_manager, rendered_config)

    def delete(self, interface_name: str) -> dict:
        """
        Delete a single interface from the device config
        Args:
            interface_name (str): name of the interface to check
        Returns:
            dict
        """
        if not self._check_exists(interface_name):
            raise CannotEdit(f"Interface {interface_name} does not exist")

        with manager.connect(**self.device.manager_params) as ncclient_manager:
            template = env.get_template(
                f"{self.device.device_type}_delete_interface.xml.j2"
            )
            rendered_config = template.render(interface_name=interface_name)
            return self.device.edit_config(ncclient_manager, rendered_config)
