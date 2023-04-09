# Basic ChatGPT using GPT-4 OpenAPI API

## Features
Simple chatGPT clone that uses the OpenAI GPT-4 model API. Works with access codes and maintains history for every opened Websocket connection. Access codes can be limited by number of prompts per day.

## Setup

First spin up the Postgres docker container
´docker compose up -d´

To get started, execute the following command to run the Flyway migration:
´docker run --rm -v /home/pi/gpt-4chat/sql:/flyway/sql -v /home/pi/gpt-4chat/conf:/flyway/conf flyway/flyway migrate´
Make sure the database name is correct

Connect to the database and insert a code
´docker exec -it pg psql -U pguser "INSERT INTO chat_codes(code,date,count,max_uses) VALUES('yourcode','YYYY-mm-dd',0,1000)"´

Activate the virtual environment
´source venv/bin/activate´
and install the dependencies
´pip install -r requirements.txt´

Create a .env file and store your OPENAPI_APIKEY there.
Start development with start_dev.sh or production with start_prd.sh
