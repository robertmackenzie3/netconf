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
4. Install requirements in your venv:  
`source venv/bin/activate`
`pip install -r requirements.txt`
5. Run the dev server:  
`fastapi dev`

Serving at: <http://127.0.0.1:8000>  
API docs: <http://127.0.0.1:8000/docs>

## Unit tests

1. Run `./run_tests.sh`

## Integration tests

1. Run `./run_dev.sh` in one shell
2. Run `./run_integration_tests.sh` in another

## NGINX

This command will start fastapi app and nginx in front of it on port 80:  
`docker-compose up --build`

This will disable access directly to fastapi but you can get to it via nginx e.g. <http://localhost/docs>

## TODO

- add more ncclient compatible device types: NEXUS, IOSXE, JUNOS etc.
- manage interfaces using openconfig so we can handle multiple devices types with the same template xml
