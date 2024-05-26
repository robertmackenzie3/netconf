"""
Holds custom models that we use in the fastapi frontend endpoints
"""

from enum import Enum

from pydantic import BaseModel


class InterfaceConfig(BaseModel):
    """
    Config for adding an interface to a device
    """

    interface_name: str
    address: str
    netmask: str
    active: str = "act"


class CredentialType(str, Enum):
    """
    Valid credential types you can use
    These should prepend env vars e.g.
    DEFAULT_USERNAME=""
    DEFAULT_PASSWORD=""
    """

    DEFAULT = "DEFAULT"
    NEXUS = "NEXUS"


class DeviceCapability(Enum):
    """
    Valid device capabilities with NETCONF
    """

    IOSXR = "http://cisco.com/ns/yang/Cisco-IOS-XR"
    # NEXUS = "http://cisco.com/ns/yang/cisco-nx-os-device"
    # IOSXE = "http://cisco.com/ns/yang/Cisco-IOS-XE"
    # JUNOS = "http://xml.juniper.net/junos/"
