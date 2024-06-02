import psycopg2
import os

db_host = os.environ.get('POSTGRES_HOST', 'localhost')
admin_user = os.environ.get('POSTGRES_ADMIN_USER', 'postgres')
admin_password = os.environ.get('POSTGRES_ADMIN_PASSWORD', 'postgres')
admin_conn = psycopg2.connect(f"dbname='postgres' user='{admin_user}' host='{db_host}' password='{admin_password}'")
admin_conn.autocommit = True