import unittest
import datetime
from components.database.Database import Database

class TestDatabase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dbname = 'test'
        cls.user = 'pguser'
        cls.password = 'pgpassword'
        cls.host = 'localhost'
        cls.port = 5432
        cls.db = Database(cls.dbname, cls.user, cls.password, cls.host, cls.port)
        cls.table_name = 'chat_codes'
        cls.code = 'ABC123'
        cls.date = '2023-04-04'
        cls.count = 0
        cls.max_uses = 10

    @classmethod
    def tearDownClass(cls):
        # Delete the row that was inserted during the test
        cls.db.execute(f"DELETE FROM {cls.table_name} WHERE code = %s", cls.code)

    def test_insert_and_delete_row(self):
        # Insert a row into the table
        self.db.execute(f"INSERT INTO {self.table_name} (code, date, count, max_uses) VALUES (%s, %s, %s, %s)",
                         self.code, self.date, self.count, self.max_uses)

        # Verify that the row was inserted
        row = self.db.fetch_one(f"SELECT * FROM {self.table_name} WHERE code = %s", self.code)
        self.assertIsNotNone(row)
        row = self.db.fetch_one(f"SELECT code,date,count,max_uses FROM {self.table_name} WHERE code = %s", self.code)
        self.assertEqual(('ABC123', datetime.date(2023, 4, 4), 0, 10), row)

        # Delete the row
        self.db.execute(f"DELETE FROM {self.table_name} WHERE code = %s", self.code)

        # Verify that the row was deleted
        row = self.db.fetch_one(f"SELECT * FROM {self.table_name} WHERE code = %s", self.code)
        self.assertIsNone(row)

if __name__ == '__main__':
    unittest.main()
