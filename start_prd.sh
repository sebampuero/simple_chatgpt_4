#!/bin/bash
source /home/pi/gpt-4chat/venv/bin/activate
source /home/pi/gpt-4chat/.env
export ENV=PROD
export SUBDIRECTORY=gpt4
export DOMAIN=sebampuerom.de
export OPENAI_KEY=$OPENAPI_APIKEY
export CLIENT_ID=$CLIENT_ID
export CLIENT_SECRET=$CLIENT_SECRET
export JWT_SECRET=$JWT_SECRET
export PROJECT_ID=$PROJECT_ID
export MISTRAL_API_KEY=$MISTRAL_API_KEY
export DDB_CHATS_TABLE=chats
export DDB_USERS_TABLE=authorized_users
export GPT_MODEL=gpt-4-vision-preview
export GEMINI_MODEL=gemini-1.0-pro
export MISTRAL_MODEL=mistral-large-latest
python3 /home/pi/gpt-4chat/server.py