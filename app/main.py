"""
Main fastapi app with endpoints
"""

import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

from app.backend import Device, InterfaceManager
from app.exceptions import CannotEdit, InvalidData
from app.models import InterfaceConfig, DeviceType, CredentialType

load_dotenv()

log_level = getattr(
    logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.DEBUG
)
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)


app = FastAPI()


@app.get("/healthz")
def healthz() -> dict:
    """
    Basic endpoint for use with health checks e.g. in k8s
    """
    return {"detail": "Netconf is running"}


@app.get("/interface")
def get_interface(
    host: str,
    device_type: DeviceType,
    interface_name: str,
    credential: CredentialType = CredentialType.DEFAULT,
) -> dict:
    """
    Get an interface via netconf
    If the interface does not exist it returns 404
    Args:
        host (str): hostname of the device to connect to
        device_type (str): ncclient device type
        interface_name (str): name of the interface to get
        credential (str): optional credential to use
    Returns:
        json_data (dict)
    """
    try:
        device = Device(host, device_type.value, credential.value)
        interface_manager = InterfaceManager(device)
        return interface_manager.get_one(interface_name)
    except InvalidData as e:
        raise HTTPException(
            status_code=404, detail=f"{interface_name} not found on {host}"
        ) from e
    except Exception as e:
        logger.exception(e.__class__.__name__)
        raise HTTPException(
            status_code=500, detail=f"Exception {e.__class__.__name__}: {e}"
        ) from e


@app.get("/interfaces")
def get_interfaces(
    host: str,
    device_type: DeviceType,
    credential: CredentialType = CredentialType.DEFAULT,
) -> dict:
    """
    Get all interfaces on a device via netconf
    Args:
        host (str): hostname of the device to connect to
        device_type (str): ncclient device type
        credential (str): optional credential to use
    Returns:
        json_data (dict)
    """
    try:
        device = Device(host, device_type.value, credential.value)
        interface_manager = InterfaceManager(device)
        return interface_manager.get_all()
    except Exception as e:
        logger.exception(e.__class__.__name__)
        raise HTTPException(
            status_code=500, detail=f"Exception {e.__class__.__name__}: {e}"
        ) from e


@app.post("/interface", status_code=201)
def create_interface(
    host: str,
    device_type: DeviceType,
    interface_config: InterfaceConfig,
    credential: CredentialType = CredentialType.DEFAULT,
) -> dict:
    """
    Create an interface on the device and commit
    Args:
        host (str): hostname of the device to connect to
        device_type (str): ncclient device type
        interface_config (InterfaceConfig): config of interface to create
        credential (str): optional credential to use
    Returns:
        json_data (dict)
    """
    try:
        device = Device(host, device_type.value, credential.value)
        interface_manager = InterfaceManager(device)
        interface_manager.create(interface_config)
        return {
            "detail": f"Successfully created {interface_config.interface_name}"
        }
    except CannotEdit as e:
        logger.info(str(e))
        raise HTTPException(status_code=409, detail=f"Cannot edit: {e}") from e
    except Exception as e:
        logger.exception(e.__class__.__name__)
        raise HTTPException(
            status_code=500, detail=f"Exception {e.__class__.__name__}: {e}"
        ) from e


@app.delete("/interface", status_code=204)
def delete_interface(
    host: str,
    device_type: DeviceType,
    interface_name: str,
    credential: CredentialType = CredentialType.DEFAULT,
) -> None:
    """
    Delete an interface from the device config and commit
    Args:
        host (str): hostname of the device to connect to
        device_type (str): ncclient device type
        interface_name (str): name of the interface to delete
        credential (str): optional credential to use
    Returns:
        None (204 status code cannot return data)
    """
    try:
        device = Device(host, device_type.value, credential.value)
        interface_manager = InterfaceManager(device)
        interface_manager.delete(interface_name)
    except CannotEdit as e:
        logger.info(str(e))
        raise HTTPException(status_code=404, detail=f"Cannot edit: {e}") from e
    except Exception as e:
        logger.exception(e.__class__.__name__)
        raise HTTPException(
            status_code=500, detail=f"Exception {e.__class__.__name__}: {e}"
        ) from e
