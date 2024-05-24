"""
Integration tests for this fast api app

This file is designed to be run after the server is started in another shell
"""

import logging

import requests

logging.basicConfig(level="DEBUG")

HOST = "sandbox-iosxr-1.cisco.com"
DEVICE_TYPE = "iosxr"


def test_healthz():
    """Test the health check"""
    logging.info("Test health check /healthz")
    response = requests.get(
        "http://127.0.0.1:8000/healthz",
        timeout=30,
    )
    assert response.status_code == 200


def test_interfaces():
    """Test we can create and delete an interface"""
    interface_name = "Loopback432"
    logging.info("Testing interface with: %s", interface_name)

    logging.info("Get all interfaces /interfaces")
    response = requests.get(
        "http://127.0.0.1:8000/interfaces",
        params={"host": HOST, "device_type": DEVICE_TYPE},
        timeout=30,
    )
    assert response.status_code == 200

    logging.info("Confirm interface %s missing", interface_name)
    response = requests.get(
        "http://127.0.0.1:8000/interface",
        params={
            "host": HOST,
            "device_type": DEVICE_TYPE,
            "interface_name": interface_name,
        },
        timeout=30,
    )
    assert response.status_code == 404

    logging.info("Create interface %s", interface_name)
    response = requests.post(
        "http://127.0.0.1:8000/interface",
        params={
            "host": HOST,
            "device_type": DEVICE_TYPE,
        },
        json={
            "interface_name": interface_name,
            "address": "10.1.1.2",
            "netmask": "255.255.255.255",
        },
        timeout=30,
    )
    assert response.status_code == 200

    logging.info("Confirm interface %s created", interface_name)
    response = requests.get(
        "http://127.0.0.1:8000/interface",
        params={
            "host": HOST,
            "device_type": DEVICE_TYPE,
            "interface_name": interface_name,
        },
        timeout=30,
    )
    assert response.status_code == 200

    logging.info("Delete interface %s", interface_name)
    response = requests.delete(
        "http://127.0.0.1:8000/interface",
        params={
            "host": HOST,
            "device_type": DEVICE_TYPE,
            "interface_name": interface_name,
        },
        timeout=30,
    )
    assert response.status_code == 200

    logging.info("Confirm interface %s deleted", interface_name)
    response = requests.get(
        "http://127.0.0.1:8000/interface",
        params={
            "host": HOST,
            "device_type": DEVICE_TYPE,
            "interface_name": interface_name,
        },
        timeout=30,
    )
    assert response.status_code == 404


if __name__ == "__main__":
    test_healthz()
    test_interfaces()
    print("All assertions passed")
