# Basic Chatbot that uses different public LLMs

## Features
Simple chatGPT clone that uses the OpenAI, Gemini and Mistral APIs. Sign in via Google. Chat history and authorized google emails are stored in DynamoDB.

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

## Screenshots
 <img src="https://sebampuerom.de/nc/apps/files_sharing/publicpreview/PTDF4ToDPL942aA?file=/&fileId=3850581&x=2560&y=1440&a=true&etag=5a6c5bc0092dccf9dc38cb611d11c2ce" alt="Example Screenshot" width="400"/>
 <img src="https://sebampuerom.de/nc/apps/files_sharing/publicpreview/TFrsnQkqjJNpnf5?file=/&fileId=3850576&x=2560&y=1440&a=true&etag=e3ea0efd2de0a9cc022ef7fb8c98f244" alt="Example Screenshot" width="400"/>

## TODO
More tests  
Improve UI    
Some sort of "quota" for individual users (email addresses)
Improve cookies security
