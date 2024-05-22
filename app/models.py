"""
Holds custom models that we use in the fastapi frontend endpoints
"""

from pydantic import BaseModel


class InterfaceConfig(BaseModel):
    """
    Config for adding an interface to a device
    """

    interface_name: str
    address: str
    netmask: str
    active: str = "act"
