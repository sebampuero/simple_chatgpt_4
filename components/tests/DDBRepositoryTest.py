import unittest
from components.repository.DDBRepository import DDBRepository
from decimal import Decimal

class TestDDBRepository(unittest.TestCase):

    def setUp(self):
        self.repository = DDBRepository('dummy', 'dummy')

    def test_convert_decimal_to_int(self):
        as_list = [{'messages': [{'type': 'user', 'content': 'some content'}, {'type': 'peer', 'content': 'some content from peer'}], 'user_email': 'test@example.com', 'chat_id': Decimal('2'), 'timestamp': Decimal('1234567789')}, {'messages': [{'type': 'user', 'content': 'some content'}, {'type': 'peer', 'content': 'some content from peer'}], 'user_email': 'test@example.com', 'chat_id': Decimal('1'), 'timestamp': Decimal('1234567789')}]
        result = self.repository.convert_decimal_to_int(as_list)
        expected = [{'messages': [{'type': 'user', 'content': 'some content'}, {'type': 'peer', 'content': 'some content from peer'}], 'user_email': 'test@example.com', 'chat_id': 2, 'timestamp': 1234567789}, {'messages': [{'type': 'user', 'content': 'some content'}, {'type': 'peer', 'content': 'some content from peer'}], 'user_email': 'test@example.com', 'chat_id': 1, 'timestamp': 1234567789}]
        self.assertEquals(result, expected)

        as_dict = {'messages': [{'type': 'user', 'content': 'some content'}, {'type': 'peer', 'content': 'some content from peer'}], 'user_email': 'test@example.com', 'chat_id': Decimal('1'), 'timestamp': Decimal('1234567789')}
        result = self.repository.convert_decimal_to_int(as_dict)
        expected = {'messages': [{'type': 'user', 'content': 'some content'}, {'type': 'peer', 'content': 'some content from peer'}], 'user_email': 'test@example.com', 'chat_id': 1, 'timestamp': 1234567789}
        self.assertDictEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
