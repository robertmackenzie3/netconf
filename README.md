# Netconf

Uses netconf to make changes on network devices

## Setup

1. Create an IOSXR vm here: <https://devnetsandbox.cisco.com>
2. Create an `.env` file with:

    ```bash
    DEFAULT_USERNAME=""
    DEFAULT_PASSWORD=""
    ```

3. Create venv with python:  
`python -m venv venv`
    - Tested on python 3.11.
    - If using pyenv the .python-version file should set it.
4. Install requirements:  
`pip install -r requirements.txt`
5. Run the dev server:  
`fastapi dev`

Serving at: <http://127.0.0.1:8000>  
API docs: <http://127.0.0.1:8000/docs>

## Example Calls

```bash
curl -s 'http://127.0.0.1:8000/interfaces?host=sandbox-iosxr-1.cisco.com&device_type=iosxr' | jq

curl -s -X PUT -H "Content-Type: application/json" -d '{"interface_name": "Loopback0", "address": "10.0.0.1", "netmask": "255.255.255.255"}' 'http://127.0.0.1:8000/interface?host=sandbox-iosxr-1.cisco.com&device_type=iosxr' | jq

curl -s 'http://127.0.0.1:8000/interface?host=sandbox-iosxr-1.cisco.com&device_type=iosxr&interface_name=Loopback0' | jq

curl -s -X DELETE 'http://127.0.0.1:8000/interface?host=sandbox-iosxr-1.cisco.com&device_type=iosxr&interface_name=Loopback0' | jq

curl -si 'http://127.0.0.1:8000/interface?host=sandbox-iosxr-1.cisco.com&device_type=iosxr&interface_name=Loopback0'
```

```bash
❯ curl -s 'http://127.0.0.1:8000/interface?host=sandbox-iosxr-1.cisco.com&device_type=iosxr&interface_name=Loopback2' | jq

{
  "data": {
    "@xmlns": "urn:ietf:params:xml:ns:netconf:base:1.0",
    "@xmlns:nc": "urn:ietf:params:xml:ns:netconf:base:1.0",
    "interface-configurations": {
      "@xmlns": "http://cisco.com/ns/yang/Cisco-IOS-XR-ifmgr-cfg",
      "interface-configuration": {
        "active": "act",
        "interface-name": "Loopback2",
        "interface-virtual": null,
        "description": "test2"
      }
    }
  }
}
```

```bash
❯ curl -s -X DELETE 'http://127.0.0.1:8000/interface?host=sandbox-iosxr-1.cisco.com&device_type=iosxr&interface_name=Loopback0' | jq

{
  "detail": "Cannot edit: Interface Loopback0 does not exist"
}
```

## device types

```text
Alcatel Lucent: device_params={'name':'alu'}
Ciena: device_params={'name':'ciena'}
Cisco:
    CSR: device_params={'name':'csr'}
    Nexus: device_params={'name':'nexus'}
    IOS XR: device_params={'name':'iosxr'}
    IOS XE: device_params={'name':'iosxe'}
H3C: device_params={'name':'h3c'}
HP Comware: device_params={'name':'hpcomware'}
Huawei:
    device_params={'name':'huawei'}
    device_params={'name':'huaweiyang'}
Juniper: device_params={'name':'junos'}
Server or anything not in above: device_params={'name':'default'}
```
