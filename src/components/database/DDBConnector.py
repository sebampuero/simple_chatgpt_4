import logging
import boto3
import asyncio
from boto3.dynamodb.conditions import Key
from sanic import Sanic
from models.ChatModel import ChatModel
from models.UserModel import UserModel

logger = logging.getLogger("ChatGPT")

class DDBConnector:
    def __init__(self, chats_table: str, users_table: str):
        app = Sanic.get_app()
        self.chats_table = chats_table
        self.users_table = users_table
        self.resource = boto3.resource('dynamodb',
                          endpoint_url=app.config.AWS_DYNAMODB_ENDPOINT,
                          region_name=app.config.AWS_REGION,
                          aws_access_key_id=app.config.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=app.config.AWS_SECRET_ACCESS_KEY)

    async def get_chats_by_email(self, email: str) -> dict:
        table = self.resource.Table(self.chats_table)
        try:
            response = await asyncio.to_thread(
                lambda: table.query(
                    IndexName="user_email-index",
                    KeyConditionExpression=Key("user_email").eq(email),
                ),
            )
        except Exception as e:
            logger.error(f"Error querying for {email} {e}")
            return {}
        return response.get("Items", [])

    async def get_chats_by_email_paginated(
        self,
        email: str,
        *,
        last_evaluated_key: dict,
        limit: int,
        load_images: bool = False,
    ) -> dict:
        table = self.resource.Table(self.chats_table)
        try:
            query_params = {
                "IndexName": "user_email-index",
                "KeyConditionExpression": Key("user_email").eq(email),
                "ScanIndexForward": False,
            }
            if last_evaluated_key:
                query_params["ExclusiveStartKey"] = last_evaluated_key
            if limit:
                query_params["Limit"] = limit
            response = await asyncio.to_thread(
                lambda: table.query(**query_params),
            )
            if not load_images:
                items = response.get("Items", [])
                for item in items:
                    for message in item["messages"]:
                        message.pop("image", None)
        except Exception as e:
            logger.error(f"Error querying for {email} {e}")
            return {"items": [], "last_eval_key": ""}
        # To continue reading from where you left off, return the LastEvaluatedKey in the response
        return {
            "items": response.get("Items", []),
            "last_eval_key": response.get("LastEvaluatedKey"),
        }

    async def get_chat_by_id(self, id: str) -> dict | None:
        table = self.resource.Table(self.chats_table)
        try:
            response = await asyncio.to_thread(
                lambda: table.query(
                    KeyConditionExpression=Key('chat_id').eq(id),
                    Limit=1
                )
            )
            items = response.get('Items', [])
            return items[0] if items else None
        except Exception as e:
            logger.error(f"Error querying chat with id {id}: {e}")
            return None

    async def delete_chat_by_id(self, id: str, timestamp: int):
        table = self.resource.Table(self.chats_table)
        try:
            response = await asyncio.to_thread(
                lambda: table.delete_item(Key={"chat_id": id, "timestamp": timestamp})
            )
            logger.debug(f"Deleting ID {id}. Response: {response}")
        except Exception as e:
            logger.error(f"Error deleting chat with id {id} {e}")

    async def get_user(self, email: str) -> UserModel | None:
        table = self.resource.Table(self.users_table)
        try:
            response = await asyncio.to_thread(
                lambda: table.get_item(Key={"email": email})
            )
        except Exception as e:
            logger.error(f"Error querying user with email {email} {e}")
            return None
        return UserModel.model_validate(response.get("Item")) if response.get("Item") else None

    async def store_chat(self, chat: ChatModel):
        table = self.resource.Table(self.chats_table)
        try:
            response = await asyncio.to_thread(lambda: table.put_item(Item=chat.model_dump()))
            logger.debug(f"Created or updated chat {chat}. Response: {response}")
        except Exception as e:
            logger.error(f"Error saving chat {chat} {e}")
