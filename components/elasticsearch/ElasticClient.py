from elasticsearch import Elasticsearch
from elastic_transport import ObjectApiResponse
from typing import Any
import os
import logging

logger = logging.getLogger(__name__)

HOST = os.getenv("ES_HOST")
PORT = os.getenv("ES_PORT")

class ElasticClient:
    def __init__(self, index = None):
        self.es = Elasticsearch(hosts=f"http://{HOST}:{PORT}", basic_auth=("elastic","changemepls"))
        self.index = 'chat_index' if not index else index
        if not self.es.indices.exists(index=self.index):
            self._create_index()

    def _create_index(self):
        body = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 1
            },
            "mappings": {
                "properties": {
                    "user_email": {
                        "type": "keyword"
                    }
                }
            }
        }
        response = self.es.indices.create(index=self.index, body=body)
        return response

    def create_document(self, chat_id: str, timestamp: int, messages: list, email_address: str) -> ObjectApiResponse[Any]:
        doc_id = chat_id
        
        body = {
            'chat_id': chat_id,
            'timestamp': timestamp,
            'messages': messages,
            'user_email': email_address
        }
        
        response = self.es.index(index=self.index, id=doc_id, body=body)
        return response

    def delete_document(self, doc_id: str):
        response = self.es.delete(index=self.index, id=doc_id)
        return response
    
    def search_chats_by_keyword(self, keyword: str, email_address: str) -> list:
        matches = self.search_documents(keyword, email_address)
        results = []
        for result in matches:
            results.append({
                "chat_id": result['_source']['chat_id'],
                "timestamp": result['_source']['timestamp'],
                "messages": result['_source']['messages']
            })
        return results

    def search_documents(self, keyword: str, email_address: str) -> ObjectApiResponse[Any]:
        query = {
            'query': {
                'bool': {
                    'must': [
                        {'match': {'messages.content': keyword}},
                        {'match': {'user_email': email_address}}
                    ]
                }
            }
        }
        response = self.es.search(index=self.index, body=query)
        return response['hits']['hits']