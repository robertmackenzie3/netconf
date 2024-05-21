import logging
import os
from app.backend import create_device

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

load_dotenv()

log_level = getattr(
    logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.DEBUG
)
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)


app = FastAPI()


class InterfaceConfig(BaseModel):
    interface_name: str
    address: str
    netmask: str
    active: str = "act"


# @app.put("/interface")
# def create_interface(
#     host: str, device_type: str, interface_config: InterfaceConfig
# ):
#     manager_params = ManagerParams(host=host)
#     manager_params.set_device_params(device_type)
#     template = env.get_template("iosxr_create_interface.xml.j2")
#     rendered_config = template.render(**interface_config.__dict__)
#     try:
#         with manager.connect(**manager_params.__dict__) as conn:
#             conn.edit_config(
#                 target="candidate",
#                 config=rendered_config
#             )
#             conn.commit()
#             return {
#                 "detail": (
#                     f"Created {interface_config.interface_name} on {host}"
#                 )
#             }
#     except Exception as e:
#         logger.exception(e.__class__.__name__)
#         raise HTTPException(
#             status_code=500, detail=f"Exception {e.__class__.__name__}: {e}"
#         )


# @app.delete("/interface")
# def delete_interface(host: str, device_type: str, interface_name: str):
#     manager_params = ManagerParams(host=host)
#     manager_params.set_device_params(device_type)
#     template = env.get_template("iosxr_delete_interface.xml.j2")
#     rendered_config = template.render(interface_name=interface_name)
#     try:
#         with manager.connect(**manager_params.__dict__) as conn:
#             conn.edit_config(
#                 target="candidate", config=rendered_config
#             )
#             conn.validate()
#             conn.commit()
#             return {"detail": f"Deleted {interface_name} on {host}"}
#     except Exception as e:
#         logger.exception(e.__class__.__name__)
#         raise HTTPException(
#             status_code=500, detail=f"Exception {e.__class__.__name__}: {e}"
#         )


@app.get("/interface")
def get_interface(host: str, device_type: str, interface_name: str):
    device = create_device(host, device_type)
    try:
        json_data = device.get_interface(interface_name)
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


# @app.get("/interfaces")
# def get_interfaces(host: str, device_type: str):
#     manager_params = ManagerParams(host=host)
#     manager_params.set_device_params(device_type)
#     try:
#         with manager.connect(**manager_params.__dict__) as conn:
#             filter = """
#             <filter>
#                 <interface-configurations xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ifmgr-cfg"/>
#             </filter>
#             """
#             response = conn.get_config(source="running", filter=filter)
#             xml_data = response.data_xml
#             json_data = xmltodict.parse(xml_data)
#             return json_data
#     except Exception as e:
#         logger.exception(e.__class__.__name__)
#         raise HTTPException(
#             status_code=500, detail=f"Exception {e.__class__.__name__}: {e}"
#         )
