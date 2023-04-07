#!/bin/bash
source /home/pi/gpt-4chat/venv/bin/activate
source /home/pi/gpt-4chat/.env
export ENV=PROD
export SUBDIRECTORY=gpt4
export DOMAIN=sebampuerom.de
export OPENAI_KEY=$OPENAPI_APIKEY
export DB=chatgpt4db
python3 /home/pi/gpt-4chat/server.py