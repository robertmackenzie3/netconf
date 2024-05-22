import os
from abc import ABC
from dataclasses import dataclass

import xmltodict
from jinja2 import Environment, FileSystemLoader
from ncclient import manager

from app.models import InterfaceConfig
from app.exceptions import CannotEdit

env = Environment(loader=FileSystemLoader("app/templates"))


@dataclass
class ManagerParams:
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
class DeviceObject(ABC):
    """A base class for an object that can be retrieved or editted on a device"""

    manager_params: ManagerParams

    def _get_config(self, conn, rendered_config):
        response = conn.get_config(source="running", filter=rendered_config)
        xml_data = response.data_xml
        return xmltodict.parse(xml_data)

    def _edit_config(self, conn, rendered_config):
        conn.edit_config(target="candidate", config=rendered_config)
        conn.commit()

    def get_one(self):
        raise NotImplementedError

    def get_all(self):
        raise NotImplementedError

    def add(self):
        raise NotImplementedError

    def remove(self):
        raise NotImplementedError


@dataclass
class Interface(DeviceObject):
    """An interface object on a device"""

    def _check_exists(self, interface_name):
        json_data = self.get_one(interface_name)
        return bool(json_data.get("data", {}).get("interface-configurations"))

    def get_one(self, interface_name: str) -> dict:
        with manager.connect(**self.manager_params.format()) as conn:
            template = env.get_template(
                f"{self.manager_params.device_type}_get_interface.xml.j2"
            )
            rendered_config = template.render(interface_name=interface_name)
            return self._get_config(conn, rendered_config)

    def get_all(self) -> dict:
        with manager.connect(**self.manager_params.format()) as conn:
            template = env.get_template(
                f"{self.manager_params.device_type}_get_interfaces.xml.j2"
            )
            rendered_config = template.render()
            return self._get_config(conn, rendered_config)

    def add(self, interface_config: InterfaceConfig) -> dict:
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
        if not self._check_exists(interface_name):
            raise CannotEdit(f"Interface {interface_name} does not exist")

        with manager.connect(**self.manager_params.format()) as conn:
            template = env.get_template(
                f"{self.manager_params.device_type}_delete_interface.xml.j2"
            )
            rendered_config = template.render(interface_name=interface_name)
            return self._edit_config(conn, rendered_config)
