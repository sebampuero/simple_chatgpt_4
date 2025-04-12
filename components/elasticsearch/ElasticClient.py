from elasticsearch import AsyncElasticsearch
from elastic_transport import ObjectApiResponse
from typing import Any
import logging
from sanic import Sanic
from constants.AppConstants import AppConstants
app = Sanic(AppConstants.APP_NAME)

logger = logging.getLogger("ChatGPT")

HOST = app.config.ELASTIC_SEARCH_HOST
PORT = app.config.ELASTIC_SEARCH_PORT


class ElasticClient:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, index=None):
        if not ElasticClient._initialized:
            self.es = AsyncElasticsearch(
                hosts=f"http://{HOST}:{PORT}", basic_auth=("elastic", "changemepls")
            )
            self.index = "chat_index" if not index else index
            ElasticClient._initialized = True

    @classmethod
    async def get_instance(cls, index=None):
        if cls._instance is None:
            cls._instance = ElasticClient(index)
        await cls._instance._check_index()
        
        return cls._instance

    async def _check_index(self):
        if not await self.es.indices.exists(index=self.index):
            await self._create_index()

    async def _create_index(self):
        body = {
            "settings": {"number_of_shards": 1, "number_of_replicas": 1},
            "mappings": {"properties": {"user_email": {"type": "keyword"}}},
        }
        response = await self.es.indices.create(index=self.index, body=body)
        return response

    async def create_document(
        self, chat_id: str, timestamp: int, messages: list, email_address: str
    ) -> ObjectApiResponse[Any]:
        doc_id = chat_id
        body = {
            "chat_id": chat_id,
            "timestamp": timestamp,
            "messages": messages,
            "user_email": email_address,
        }

        response = await self.es.index(index=self.index, id=doc_id, body=body)
        return response

    async def delete_document(self, doc_id: str):
        response = await self.es.delete(index=self.index, id=doc_id)
        return response

    async def search_chats_by_keyword(self, keyword: str, email_address: str) -> list:
        matches = await self.search_documents(keyword, email_address)
        results = []
        for result in matches:
            results.append(
                {
                    "chat_id": result["_source"]["chat_id"],
                    "timestamp": result["_source"]["timestamp"],
                    "messages": result["_source"]["messages"],
                }
            )
        return self.sort_by_timestamp(results, asc=True)

    def sort_by_timestamp(self, chats: list, *, asc: bool) -> list:
        return sorted(chats, key=lambda x: int(x["timestamp"]), reverse=asc)

    async def search_documents(
        self, keyword: str, email_address: str
    ) -> ObjectApiResponse[Any]:
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"match": {"messages.content": keyword}},
                        {"match": {"user_email": email_address}},
                    ]
                }
            }
        }
        response = await self.es.search(index=self.index, body=query)
        return response["hits"]["hits"]
