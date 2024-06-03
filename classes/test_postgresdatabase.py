import unittest
from unittest.mock import MagicMock, patch
from classes.postgresdatabase import PostgresDatabase
import psycopg2

class TestPostgresDatabase(unittest.TestCase):
    @patch('psycopg2.connect')
    def setUp(self, mock_connect):
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()
        
        mock_connect.return_value = self.mock_conn
        
        self.mock_conn.cursor.return_value = self.mock_cursor

        self.db = PostgresDatabase('localhost', 'postgres', 'postgres')

    def test_create_database_success(self):
        self.mock_cursor.execute.return_value = None

        result = self.db.create_database('testdb', 'testuser', 'testpass')

        self.assertTrue(result)
        self.mock_cursor.execute.assert_has_calls([
            unittest.mock.call(f"CREATE DATABASE testdb"),
            unittest.mock.call(f"CREATE USER testuser WITH PASSWORD 'testpass'"),
            unittest.mock.call(f"GRANT ALL PRIVILEGES ON DATABASE testdb TO testuser")
        ])

    def test_create_database_failure(self):
        self.mock_cursor.execute.side_effect = Exception("Creation failed")

        result = self.db.create_database('testdb', 'testuser', 'testpass')

        self.assertFalse(result)

    def test_delete_database_success(self):
        self.mock_cursor.execute.return_value = None

        result = self.db.delete_database('testdb', 'testuser')

        self.assertTrue(result)
        self.mock_cursor.execute.assert_has_calls([
            unittest.mock.call("DROP DATABASE IF EXISTS testdb"),
            unittest.mock.call("DROP USER IF EXISTS testuser")
        ])

    def test_delete_database_failure(self):
        self.mock_cursor.execute.side_effect = Exception("Deletion failed")

        result = self.db.delete_database('testdb', 'testuser')

        self.assertFalse(result)

    def test_test_database_connection(self):
        with patch('psycopg2.connect') as mock_test_connect:
            mock_test_connect.return_value = MagicMock()
            result = self.db.test_database_connection()
            self.assertEqual(result, 'Created')

        with patch('psycopg2.connect', side_effect=psycopg2.OperationalError):
            result = self.db.test_database_connection()
            self.assertEqual(result, 'Failed')

if __name__ == '__main__':
    unittest.main()
