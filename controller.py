import psycopg2
from config import admin_conn

def create_database(database_name: str, username: str, password: str) -> bool:
    cursor = admin_conn.cursor()

    try:
        cursor.execute(f"CREATE DATABASE {database_name}")
        cursor.execute(f"CREATE USER {username} WITH PASSWORD '{password}'")
        cursor.execute(f"GRANT ALL PRIVILEGES ON DATABASE {database_name} TO {username}")
        cursor.close()
        return True
    except Exception as e:
        print(f"Database creation failed: {e}")
        return False

def delete_database(database_name: str, username: str) -> bool:
    cursor = admin_conn.cursor()

    try:
        cursor.execute(f"DROP DATABASE IF EXISTS {database_name}")
        cursor.execute(f"DROP USER IF EXISTS {username}")
        cursor.close()
        return True
    except Exception as e:
        print(f"Database deletion failed: {e}")
        return False
    
def test_database_connection(db_host: str, database_name: str, username: str, password: str) -> str:
    try:
        test_conn = psycopg2.connect(f"dbname='{database_name}' user='{username}' host='{db_host}' password='{password}'")
        test_conn.close()
        return 'Created'
    except psycopg2.OperationalError:
        return 'Failed'