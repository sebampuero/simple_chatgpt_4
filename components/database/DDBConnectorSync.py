import logging
import boto3
from boto3.dynamodb.conditions import Key, Attr
from components.elasticsearch.ElasticClient import ElasticClient

logger = logging.getLogger("ChatGPT")


# TODO: async needs to be pushed. Maybe use https://pypi.org/project/asgiref/ ? evaluate how does it work
class DDBConnectorSync:
    def __init__(self, chats_table: str, users_table: str):
        self.chats_table = chats_table
        self.users_table = users_table
        self.resource = boto3.resource("dynamodb")
        self.es = ElasticClient()

    async def get_chats_by_email(self, email: str) -> dict:
        table = self.resource.Table(self.chats_table)
        try:
            response = table.query(
                IndexName="user_email-index",
                KeyConditionExpression=Key("user_email").eq(email),
            )
        except Exception as e:
            logger.error(f"Error querying for {email} {e}")
            return []
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
            response = table.query(**query_params)
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

    async def get_chat_by_id(self, id: str, timestamp: int) -> dict:
        table = self.resource.Table(self.chats_table)
        try:
            response = table.get_item(Key={"chat_id": id, "timestamp": timestamp})
        except Exception as e:
            logger.error(f"Error querying chat with id {id} {e}")
            return None
        return response.get("Item")

    async def delete_chat_by_id(self, id: str, timestamp: int):
        table = self.resource.Table(self.chats_table)
        try:
            response = table.delete_item(Key={"chat_id": id, "timestamp": timestamp})
            self.es.delete_document(id)
            logger.debug(f"Deleting ID {id}. Response: {response}")
        except Exception as e:
            logger.error(f"Error deleting chat with id {id} {e}")

    async def get_user(self, email: str):
        table = self.resource.Table(self.users_table)
        try:
            response = table.get_item(Key={"email": email})
        except Exception as e:
            logger.error(f"Error querying user with email {email} {e}")
            return None
        return response.get("Item")

    async def store_chat(self, chat: dict):
        table = self.resource.Table(self.chats_table)
        try:
            response = table.put_item(Item=chat)
            self.es.create_document(
                chat["chat_id"], chat["timestamp"], chat["messages"], chat["user_email"]
            )
            logger.debug(f"Created chat {chat}. Response: {response}")
        except Exception as e:
            logger.error(f"Error saving chat {chat} {e}")
