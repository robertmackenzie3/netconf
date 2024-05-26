"""
Main fastapi app with endpoints
"""

import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

from app.backend import Device, InterfaceManager
from app.exceptions import CannotEdit, InvalidData
from app.models import InterfaceConfig, CredentialType

load_dotenv()

log_level = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper())
logging.basicConfig(level=log_level)

app = FastAPI()


@app.get("/healthz")
def healthz() -> dict:
    """
    Basic endpoint for use with health checks e.g. in k8s
    Returns:
        dict
    """
    return {"detail": "Netconf is running"}


@app.get("/interface")
def get_interface(
    host: str,
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
        dict
    """
    try:
        device = Device(host, credential.value)
        interface_manager = InterfaceManager(device)
        return interface_manager.get_one(interface_name)
    except InvalidData as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        logging.exception(e.__class__.__name__)
        raise HTTPException(
            status_code=500, detail=f"Exception {e.__class__.__name__}: {e}"
        ) from e


@app.get("/interfaces")
def get_interfaces(
    host: str,
    credential: CredentialType = CredentialType.DEFAULT,
) -> dict:
    """
    Get all interfaces on a device via netconf
    Args:
        host (str): hostname of the device to connect to
        device_type (str): ncclient device type
        credential (str): optional credential to use
    Returns:
        dict
    """
    try:
        device = Device(host, credential.value)
        interface_manager = InterfaceManager(device)
        return interface_manager.get_all()
    except Exception as e:
        logging.exception(e.__class__.__name__)
        raise HTTPException(
            status_code=500, detail=f"Exception {e.__class__.__name__}: {e}"
        ) from e


@app.post("/interface", status_code=200)
def create_interface(
    host: str,
    interface_config: InterfaceConfig,
    credential: CredentialType = CredentialType.DEFAULT,
    dry_run: bool = False,
) -> dict:
    """
    Create an interface on the device and commit
    Args:
        host (str): hostname of the device to connect to
        device_type (str): ncclient device type
        interface_config (InterfaceConfig): config of interface to create
        credential (str): optional credential to use
        dry_run (bool): if true returns what we would send to create
    Returns:
        dict
    """
    try:
        device = Device(host, credential.value)
        interface_manager = InterfaceManager(device)
        data = interface_manager.create(interface_config, dry_run)
        if dry_run:
            return {"dry_run": data}

        return {
            "detail": f"Successfully created {interface_config.interface_name}"
        }
    except CannotEdit as e:
        logging.info(str(e))
        raise HTTPException(status_code=409, detail=f"Cannot edit: {e}") from e
    except Exception as e:
        logging.exception(e.__class__.__name__)
        raise HTTPException(
            status_code=500, detail=f"Exception {e.__class__.__name__}: {e}"
        ) from e


@app.delete("/interface", status_code=200)
def delete_interface(
    host: str,
    interface_name: str,
    credential: CredentialType = CredentialType.DEFAULT,
    dry_run: bool = False,
) -> dict:
    """
    Delete an interface from the device config and commit
    Args:
        host (str): hostname of the device to connect to
        device_type (str): ncclient device type
        interface_name (str): name of the interface to delete
        credential (str): optional credential to use
        dry_run (bool): if true returns what we would send to create
    Returns:
        dict
    """
    try:
        device = Device(host, credential.value)
        interface_manager = InterfaceManager(device)
        data = interface_manager.delete(interface_name, dry_run)
        if dry_run:
            return {"dry_run": data}

        return {"detail": f"Successfully deleted {interface_name}"}
    except CannotEdit as e:
        logging.info(str(e))
        raise HTTPException(status_code=404, detail=f"Cannot edit: {e}") from e
    except Exception as e:
        logging.exception(e.__class__.__name__)
        raise HTTPException(
            status_code=500, detail=f"Exception {e.__class__.__name__}: {e}"
        ) from e
