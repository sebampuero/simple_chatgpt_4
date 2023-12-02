# Basic ChatGPT using GPT-4 OpenAPI API

## Features
Simple chatGPT clone that uses the OpenAI GPT-4 model API. Sign in via Google. Chat history and authorized google emails are stored in DynamoDB.

## Setup

First install the aws-cli with ´sudo pip3 install awscli´
Then, run ´aws configure´ to set up your AWS credentials. Make sure you have the correct policies set in place (Creation of tables, put, query and scan privileges)
Then, run ´setup.sh´ to create the tables in DynamoDB. It will ask for the name of the chats table and authorized table. Place those in the start_prd.sh file, too.

Activate the virtual environment in python:
´source venv/bin/activate´
and install the dependencies
´pip install -r requirements.txt´

Configure a new Google project that uses the Google+ API. Generate a pair of Client ID and secret. https://console.cloud.google.com/apis/api/plus.googleapis.com
Create a .env file and store your OPENAPI_APIKEY, CLIENT_ID (Google Oauth), CLIENT_SECRET (Google Oauth) and JWT_SECRET there.
Start development with start_dev.sh or production with start_prd.sh
