# Basic Chatbot that uses different public LLMs

## Features
Simple chatGPT clone that uses the OpenAI, Gemini, Mistral and Anthropic APIs. Sign in via Google. Chat history and authorized google emails are stored in DynamoDB.

## Setup

First install the aws-cli with `sudo pip3 install awscli`  
Then, run `aws configure` to set up your AWS credentials. Make sure you have the correct policies set in place for your AWS user or role (Creation of tables, put, query and scan privileges)  
Example:  
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:CreateTable",
                "dynamodb:PutItem",
                "dynamodb:DeleteItem",
                "dynamodb:Query",
                "dynamodb:Scan",
                "dynamodb:DescribeTable"
            ],
            "Resource": [
                "arn:aws:dynamodb:*:*:table/YourChatsTableName",
                "arn:aws:dynamodb:*:*:table/YourAuthorizedTableName"
            ]
        }
    ]
}
```

Then, run `setup.sh` to create the tables in DynamoDB. It will ask for the name of the chats table and authorized table. Place those in the `start_prd.sh` file, too.  
Execute the bash script `add_authorized_email.sh` to add your Google email to the authorized users table. Add other emails if you want to share with other people.

Activate the virtual environment in python:  
`source venv/bin/activate`  
and install the dependencies  
`pip install -r requirements.txt`

Configure a new Google project that uses the Google+ API. Generate a pair of Client ID and secret. https://console.cloud.google.com/apis/api/plus.googleapis.com  
For this flow to work, a domain needs to be registered (free domain under https://www.getfreedomain.name/ for example). A certificate for TLS communication can be automatically managed by Certbot: https://letsencrypt.org/getting-started/  
Create a `.env` file and store your `OPENAPI_APIKEY`, `CLIENT_ID` (Google Oauth), `CLIENT_SECRET` (Google Oauth) , `JWT_SECRET` (for session authorization), `GEMINI_PROJECTID` and `MISTRAL_API_KEY`

Start development with `start_dev.sh` or production with `start_prd.sh`

The chat app includes a searching functionality that leverages elastic search. In order to start elastic search, the following docker-compose.yml file can be used:

```
version: '3'
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:latest
    container_name: elasticsearch
    restart: unless-stopped
    environment:
      - discovery.type=single-node
      - ES_JAVA_OPTS=-Xms512m -Xmx512m
      - xpack.security.enabled=true
      - ELASTIC_PASSWORD=yourpassowrd
      - "ELASTICSEARCH_USERNAME=elastic"
    ports:
      - "9200:9200"
      - "9300:9300"
    volumes:
      - ./esdata:/usr/share/elasticsearch/data
    networks:
      - esnet

volumes:
  esdata:
    driver: local

networks:
  esnet:
    driver: bridge
```

## Screenshots
 <table>
  <tr>
    <td>
      <img src="https://sebampuerom.de/nc/apps/files_sharing/publicpreview/DH3DjdaZfbi6gYB?file=/&fileId=4579556&x=2560&y=1440&a=true&etag=b1c37c703c4c393dd110660d3aad2ca4" alt="Example Screenshot" width="400"/>
    </td>
    <td>
      <img src="https://sebampuerom.de/nc/apps/files_sharing/publicpreview/PrKBg9Bk68e39EW?file=/&fileId=4579550&x=2560&y=1440&a=true&etag=0dbcf0d7204ed215b169bc876c533834" alt="Example Screenshot" width="400"/>
    </td>
    <td>
      <img src="https://sebampuerom.de/nc/apps/files_sharing/publicpreview/JjFqP5ECFF2KY9N?file=/&fileId=4579546&x=2560&y=1440&a=true&etag=03b526cc4bcc704a67924031233d054c" alt="Example Screenshot" width="400"/>
    </td>
  </tr>
</table>

## TODO
More tests      
Some sort of "quota" for individual users (email addresses)
