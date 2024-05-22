import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

from app.backend import ManagerParams, Interface
from app.models import InterfaceConfig
from app.exceptions import CannotEdit


load_dotenv()

log_level = getattr(
    logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.DEBUG
)
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)


app = FastAPI()


@app.get("/healthz")
def healthz():
    """
    Basic endpoint for use with health checks e.g. in k8s
    """
    return {"detail": "Netconf is running"}


@app.get("/interface")
def get_interface(host: str, device_type: str, interface_name: str):
    manager_params = ManagerParams(host, device_type)
    interface = Interface(manager_params)
    try:
        json_data = interface.get_one(interface_name)
    except Exception as e:
        logger.exception(e.__class__.__name__)
        raise HTTPException(
            status_code=500, detail=f"Exception {e.__class__.__name__}: {e}"
        )

    if json_data.get("data", {}).get("interface-configurations"):
        return json_data
    else:
        raise HTTPException(
            status_code=404, detail=f"{interface_name} not found on {host}"
        )


@app.get("/interfaces")
def get_interfaces(host: str, device_type: str):
    manager_params = ManagerParams(host, device_type)
    interface = Interface(manager_params)
    try:
        return interface.get_all()
    except Exception as e:
        logger.exception(e.__class__.__name__)
        raise HTTPException(
            status_code=500, detail=f"Exception {e.__class__.__name__}: {e}"
        )


@app.put("/interface")
def add_interface(
    host: str, device_type: str, interface_config: InterfaceConfig
):
    manager_params = ManagerParams(host, device_type)
    interface = Interface(manager_params)
    try:
        interface.add(interface_config)
        return {
            "detail": f"Successfully added {interface_config.interface_name}"
        }
    except CannotEdit as e:
        logger.info(str(e))
        raise HTTPException(status_code=400, detail=f"Cannot edit: {e}")
    except Exception as e:
        logger.exception(e.__class__.__name__)
        raise HTTPException(
            status_code=500, detail=f"Exception {e.__class__.__name__}: {e}"
        )


@app.delete("/interface")
def remove_interface(host: str, device_type: str, interface_name: str):
    manager_params = ManagerParams(host, device_type)
    interface = Interface(manager_params)
    try:
        interface.remove(interface_name)
        return {"detail": f"Successfully removed {interface_name}"}
    except CannotEdit as e:
        logger.info(str(e))
        raise HTTPException(status_code=400, detail=f"Cannot edit: {e}")
    except Exception as e:
        logger.exception(e.__class__.__name__)
        raise HTTPException(
            status_code=500, detail=f"Exception {e.__class__.__name__}: {e}"
        )
