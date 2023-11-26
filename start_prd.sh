#!/bin/bash
source /home/pi/gpt-4chat/venv/bin/activate
source /home/pi/gpt-4chat/.env
export ENV=PROD
export SUBDIRECTORY=gpt4
export DOMAIN=sebampuerom.de
export OPENAI_KEY=$OPENAPI_APIKEY
export DB=chatgpt
export DDB_CHATS_TABLE=chats
export DDB_USERS_TABLE=authorized_users
python3 /home/pi/gpt-4chat/server.py