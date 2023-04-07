import unittest
from unittest.mock import MagicMock
from datetime import date
from components.chat_code_repository.ChatCode import ChatCode
from components.chat_code_repository.CodeRepository import CodeRepository
from components.database.Database import Database

class TestCodeRepository(unittest.TestCase):
    def setUp(self):
        # Set up a mock database connection for testing
        self.mock_db = MagicMock(spec=Database)
        self.repository = CodeRepository(self.mock_db)

    def test_get_code_returns_correct_code(self):
        # Set up mock data for the database to return
        mock_result = (1, 'ABC123', date(2023, 4, 3), 5, 10)
        self.mock_db.fetch_one.return_value = mock_result

        # Call the get_code method with a mock code
        code = 'ABC123'
        result = self.repository.get_code(code)
        # Check that the ChatCode object returned by the method has the expected values
        expected_result = ChatCode(1, 'ABC123', '2023-04-03', 5, 10)
        self.assertEqual(result, expected_result)

        # Check that the fetch_one method was called with the correct SQL statement and code
        expected_sql = "SELECT * FROM chat_codes WHERE code = %s"
        self.mock_db.fetch_one.assert_called_once_with(expected_sql, code)

    def test_incr_code_uses_by_one(self):
        # Check that the execute method was called with the correct SQL statement and code
        code = ChatCode(1, 'ABC', '2023-04-05', 0, 10)
        expected_sql = "UPDATE chat_codes SET count = %s WHERE code = %s"
        self.repository.incr_code_uses(code)
        self.mock_db.execute.assert_called_once_with(expected_sql, code.count + 1, code.code)

    def test_update_code(self):
        # Check that the execute method was called with the correct SQL statement and code
        code = ChatCode(1, 'ABC', '2023-04-05', 0, 10)
        expected_sql = "UPDATE chat_codes SET date = %s, count = %s WHERE code = %s"
        self.repository.update_code(code)
        self.mock_db.execute.assert_called_once_with(expected_sql, code.date, code.count, code.code)

if __name__ == '__main__':
    unittest.main()
