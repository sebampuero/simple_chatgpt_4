#!/bin/bash
source /home/pi/gpt-4chat/venv/bin/activate
source /home/pi/gpt-4chat/.env
export ENV=DEV
export SUBDIRECTORY=
export DOMAIN=localhost
export OPENAI_KEY=$OPENAPI_APIKEY
export CLIENT_ID=$CLIENT_ID
export CLIENT_SECRET=$CLIENT_SECRET
export JWT_SECRET=$JWT_SECRET
export DDB_CHATS_TABLE=chats_test
export DDB_USERS_TABLE=authorized_users
python3 /home/pi/gpt-4chat/server.py