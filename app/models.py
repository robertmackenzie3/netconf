from pydantic import BaseModel


class InterfaceConfig(BaseModel):
    interface_name: str
    address: str
    netmask: str
    active: str = "act"
