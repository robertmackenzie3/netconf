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

## TODO

2. integration tests
3. add nginx front server with docker compose
4. add dry run
5. finish nexus add/remove
6. more advanced pipeline
7. gitlab pipeline?
