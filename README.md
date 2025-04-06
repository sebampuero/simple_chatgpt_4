# Basic Chatbot that uses different public LLMs

## Features
- Simple chatGPT clone that uses the OpenAI, DeepSeek, Mistral and Anthropic APIs. 

- Sign in via Google. Chat history and authorized google emails are stored in DynamoDB.

- Chat search capabitilies with the help of ElasticSearch

## Setup

Populate a `.env`file by using the provided `.env.dist`.

Get up and running by starting the docker containers from the `docker-compose.yml` file:
```bash
docker compose up -d
```

Install the aws-cli with `sudo pip3 install awscli`.
Then, run `setup.sh` to create the tables in DynamoDB. It will ask for the name of the chats table and authorized table. Execute the bash script `add_authorized_email.sh` to add your Google email to the authorized users table. Add other emails if you want to share with other people.

### Using real AWS DynamoDB

Make sure you have the correct policies set in place for your AWS user or role (Creation of tables, put, query and scan privileges). The AWS Secret ID and Key need to be inside the `.env` file.
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
