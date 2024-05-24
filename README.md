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

## Unit tests

1. Run `./run_tests.sh`

## Integration tests

1. Run `fastapi dev` in one shell
2. Run `./run_integration_tests.sh` in another

```bash
❯ ./run_integration_tests.sh
INFO:root:Testing interface with: Loopback432
INFO:root:Get all interfaces
DEBUG:urllib3.connectionpool:Starting new HTTP connection (1): 127.0.0.1:8000
DEBUG:urllib3.connectionpool:http://127.0.0.1:8000 "GET /interfaces?host=sandbox-iosxr-1.cisco.com&device_type=iosxr HTTP/1.1" 200 4865
INFO:root:Confirm interface Loopback432 missing
DEBUG:urllib3.connectionpool:Starting new HTTP connection (1): 127.0.0.1:8000
DEBUG:urllib3.connectionpool:http://127.0.0.1:8000 "GET /interface?host=sandbox-iosxr-1.cisco.com&device_type=iosxr&interface_name=Loopback432 HTTP/1.1" 404 63
INFO:root:Create interface Loopback432
DEBUG:urllib3.connectionpool:Starting new HTTP connection (1): 127.0.0.1:8000
DEBUG:urllib3.connectionpool:http://127.0.0.1:8000 "POST /interface?host=sandbox-iosxr-1.cisco.com&device_type=iosxr HTTP/1.1" 200 45
INFO:root:Confirm interface Loopback432 created
DEBUG:urllib3.connectionpool:Starting new HTTP connection (1): 127.0.0.1:8000
DEBUG:urllib3.connectionpool:http://127.0.0.1:8000 "GET /interface?host=sandbox-iosxr-1.cisco.com&device_type=iosxr&interface_name=Loopback432 HTTP/1.1" 200 455
INFO:root:Delete interface Loopback432
DEBUG:urllib3.connectionpool:Starting new HTTP connection (1): 127.0.0.1:8000
DEBUG:urllib3.connectionpool:http://127.0.0.1:8000 "DELETE /interface?host=sandbox-iosxr-1.cisco.com&device_type=iosxr&interface_name=Loopback432 HTTP/1.1" 200 45
INFO:root:Confirm interface Loopback432 deleted
DEBUG:urllib3.connectionpool:Starting new HTTP connection (1): 127.0.0.1:8000
DEBUG:urllib3.connectionpool:http://127.0.0.1:8000 "GET /interface?host=sandbox-iosxr-1.cisco.com&device_type=iosxr&interface_name=Loopback432 HTTP/1.1" 404 63
```

## NGINX

This command will start fastapi app and nginx in front of it on port 80: `docker compose up --build`

This will disable access directly to fastapi but you can get to it via nginx e.g. <http://localhost/docs>

## TODO

1. integration tests
2. finish nexus add/remove
3. add fingerprinting to work out device_type automatically
