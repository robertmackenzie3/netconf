import os
from dataclasses import dataclass

import xmltodict
from ncclient import manager
from jinja2 import Environment, FileSystemLoader


env = Environment(loader=FileSystemLoader("app/templates"))


def get_device_class(device_type):
    device_classes = {
        "iosxr": IOSXRDevice,
        "nxos": NXOSDevice,
    }
    return device_classes.get(device_type.lower())


def create_device(host, device_type):
    device_class = get_device_class(device_type)
    if device_class:
        return device_class(host=host)
    else:
        raise ValueError(f"Unsupported device type: {device_type}")


@dataclass
class ManagerParams:
    host: str
    port: int = 830
    timeout: int = 30
    hostkey_verify: bool = False
    look_for_keys: bool = False

    def __post_init__(self):
        self.username = os.environ["DEVICE_USERNAME"]
        self.password = os.environ["DEVICE_PASSWORD"]

    def set_device_params(self, device_type: str):
        self.device_params = {"name": device_type}


@dataclass
class IOSXRDevice:
    host: str

    def __post_init__(self):
        self.device_type = "iosxr"
        self.manager_params = ManagerParams(host=self.host)
        self.manager_params.set_device_params(self.device_type)

    def get_interface(self, interface_name: str) -> dict:
        with manager.connect(**self.manager_params.__dict__) as conn:
            template = env.get_template(
                f"{self.device_type}_get_interface.xml.j2"
            )
            rendered_config = template.render(interface_name=interface_name)
            response = conn.get_config(
                source="running", filter=rendered_config
            )
            xml_data = response.data_xml
            return xmltodict.parse(xml_data)

    # def get_interfaces():

    # def create_interface():

    # def delete_interface():


@dataclass
class NXOSDevice:
    host: str

    def __post_init__(self):
        manager_params = ManagerParams(host=self.host)
        manager_params.set_device_params("nxos")
