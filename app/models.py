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


class DeviceType(str, Enum):
    """
    Valid device types we have implemented
    """
    IOSXR = "iosxr"
    NEXUS = "nexus"
