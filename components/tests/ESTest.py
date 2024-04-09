import unittest
from components.elasticsearch.ElasticClient import ElasticClient

class TestElasticClient(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.timestammp = 123457890
        cls.client = ElasticClient(index="test")
        cls.ids = []
        i = 0
        id = 0
        loop = 0
        while True:
            cls.client.create_document(
                chat_id=str(id),
                timestamp=cls.timestammp,
                messages=[
                    {'role': 'user', 'content': f'Hello {i}!', 'image': 'base64image'},
                    {'role': 'assistant', 'content': f'Hi there {i}!', 'image': 'base64image'}
                ],
                email_address=f'user{i}@example.com'
            )
            cls.ids.append(str(i))
            i += 1
            id += 1
            if i == 10:
                i = 0
                loop += 1
            if loop == 2:
                break
        cls.client.es.indices.refresh(index="test")

    def test_search_document(self):
        search_results = self.client.search_documents('Hello', 'user5@example.com')
        self.assertTrue(len(search_results) > 0)
        for result in search_results:
            self.assertIn('Hello 5', result['_source']['messages'][0]['content'])

    def test_search_chat_content(self):
        search_results = self.client.search_chats_by_keyword('Hello', 'user5@example.com')
        self.assertListEqual([
            {'chat_id': '5', 'timestamp': 123457890, 'messages': [{'role': 'user', 'content': 'Hello 5!', 'image': 'base64image'}, {'role': 'assistant', 'content': 'Hi there 5!', 'image': 'base64image'}]}, 
            {'chat_id': '15', 'timestamp': 123457890, 'messages': [{'role': 'user', 'content': 'Hello 5!', 'image': 'base64image'}, {'role': 'assistant', 'content': 'Hi there 5!', 'image': 'base64image'}]}], search_results)

    def test_delete_document(self):
        delete_response = self.client.delete_document(self.ids[1])
        self.assertIsNotNone(delete_response)
        self.assertEqual(delete_response['result'], 'deleted')