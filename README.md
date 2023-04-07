# Basic ChatGPT using GPT-4 OpenAPI API

## Setup

To get started, execute the following command to run the Flyway migration:
´docker run --rm -v /home/pi/gpt-4chat/sql:/flyway/sql -v /home/pi/gpt-4chat/conf:/flyway/conf flyway/flyway migrate´
Make sure the database name is correct

Activate the virtual environment
´source venv/bin/activate´
and install the dependencies
´pip install -r requirements.txt´

Create a .env file and store your OPENAPI_APIKEY there.
Start development with start_dev.sh or production with start_prd.sh