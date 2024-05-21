# Netconf

Uses netconf to make changes on network devices

## Setup

1. Create a vm here: <https://devnetsandbox.cisco.com>
2. Create an `.env` file with:

    ```bash
    DEVICE_USERNAME=""
    DEVICE_PASSWORD=""
    ```

3. Create venv with python:  
`python -m venv venv`
    - Tested on python 3.11.
    - If using pyenv the .python-version file should set it.
4. Install requirements:  
`pip install -r requirements.txt`
5. Run the dev server:  
`fastapi dev`
6. Check docs: <http://127.0.0.1:5000/docs>

## Example Calls

```bash
curl -s 'http://127.0.0.1:8000/interfaces?host=sandbox-iosxr-1.cisco.com&device_type=iosxr' | jq

curl -s -X PUT -H "Content-Type: application/json" -d '{"interface_name": "Loopback0", "address": "10.0.0.1", "netmask": "255.255.255.255"}' 'http://127.0.0.1:8000/interface?host=sandbox-iosxr-1.cisco.com&device_type=iosxr' | jq

curl -s 'http://127.0.0.1:8000/interface?host=sandbox-iosxr-1.cisco.com&device_type=iosxr&interface_name=Loopback0' | jq

curl -s -X DELETE 'http://127.0.0.1:8000/interface?host=sandbox-iosxr-1.cisco.com&device_type=iosxr&interface_name=Loopback0' | jq

curl -si 'http://127.0.0.1:8000/interface?host=sandbox-iosxr-1.cisco.com&device_type=iosxr&interface_name=Loopback0'
```
