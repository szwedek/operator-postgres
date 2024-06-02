from classes.database import Database
import psycopg2

class PostgresDatabase(Database):
    def __init__(self, db_host: str, admin_user: str, admin_password: str) -> None:
        super().__init__()

        self.__db_host = db_host
        self.__admin_conn = psycopg2.connect(f"dbname='postgres' user='{admin_user}' host='{db_host}' password='{admin_password}'")
        self.__admin_conn.autocommit = True
        self.__cursor = self.__admin_conn.cursor()
        self.__database_name = None
        self.__username = None
        self.__password = None

    def create_database(self, database_name: str, username: str, password: str) -> bool:
        self.__database_name = database_name
        self.__username = username
        self.__password = password

        try:
            self.__cursor.execute(f"CREATE DATABASE {database_name}")
            self.__cursor.execute(f"CREATE USER {username} WITH PASSWORD '{password}'")
            self.__cursor.execute(f"GRANT ALL PRIVILEGES ON DATABASE {database_name} TO {username}")
            return True
        except Exception as e:
            print(f"Database creation failed: {e}")
            return False

    def delete_database(self, database_name: str, username: str) -> bool:
        try:
            self.__cursor.execute(f"DROP DATABASE IF EXISTS {database_name}")
            self.__cursor.execute(f"DROP USER IF EXISTS {username}")
            return True
        except Exception as e:
            print(f"Database deletion failed: {e}")
            return False
        
    def test_database_connection(self) -> str:
        try:
            test_conn = psycopg2.connect(f"dbname='{self.__database_name}' user='{self.__username}' host='{self.__db_host}' password='{self.__password}'")
            test_conn.close()
            return 'Created'
        except psycopg2.OperationalError:
            return 'Failed'
        
    def __del__(self) -> None:
        self.__cursor.close()
        self.__admin_conn.close()