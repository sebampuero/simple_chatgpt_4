import unittest
from unittest.mock import MagicMock
from components.database.Database import Database

class TestDatabase(unittest.TestCase):

    def setUp(self):
        # Set up a mock connection for testing
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_conn.cursor.return_value = self.mock_cursor
        self.db = Database('test', 'pguser', 'pgpassword', host='localhost', port=5432)
        self.db.conn = self.mock_conn

        # Insert some test data into the codes table
        self.mock_cursor.fetchone.return_value = (1,)
        self.db.execute("INSERT INTO codes (code, date, count, max_uses) VALUES (%s, %s, %s, %s)", ("ABC123", "2023-04-03", 5, 10))
        self.db.execute("INSERT INTO codes (code, date, count, max_uses) VALUES (%s, %s, %s, %s)", ("DEF456", "2023-04-04", 10, 20))
        self.mock_conn.commit.assert_called()

    def test_execute(self):
        # Mock the execute method to return a result
        self.mock_cursor.rowcount = 1
        result = self.db.execute('INSERT INTO codes (code, date, count, max_uses) VALUES (%s, %s, %s, %s)', ('ABC123', '2023-04-03', 5, 10))
        self.assertEqual(result.rowcount, 1)

    def test_fetch_one(self):
        # Mock the fetchone method to return a result
        self.mock_cursor.fetchone.return_value = (1, 'ABC123', '2023-04-03', 5, 10)
        result = self.db.fetch_one('SELECT * FROM codes WHERE code = %s', ('ABC123',))
        self.assertEqual(result, (1, 'ABC123', '2023-04-03', 5, 10))

    def test_fetch_all(self):
        # Mock the fetchall method to return some results
        self.mock_cursor.fetchall.return_value = [(1, 'ABC123', '2023-04-03', 5, 10), (2, 'DEF456', '2023-04-04', 10, 20)]
        result = self.db.fetch_all('SELECT * FROM codes')
        self.assertEqual(result, [(1, 'ABC123', '2023-04-03', 5, 10), (2, 'DEF456', '2023-04-04', 10, 20)])

    def tearDown(self):
        self.db.conn.close()

if __name__ == '__main__':
    unittest.main()
