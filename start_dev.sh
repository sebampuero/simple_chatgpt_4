#!/bin/bash
source /home/pi/gpt-4chat/venv/bin/activate
source /home/pi/gpt-4chat/.env
export ENV=DEV
export SUBDIRECTORY=
export DOMAIN=localhost
export OPENAI_KEY=$OPENAPI_APIKEY
export DB=test
python3 /home/pi/gpt-4chat/server.py