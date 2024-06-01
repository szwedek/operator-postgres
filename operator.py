import kopf
import os
import psycopg2
from kubernetes import client, config
from kubernetes.config import ConfigException

def create_database(database_name, username, password):
    db_host = os.environ.get('POSTGRES_HOST', 'localhost')
    admin_user = os.environ.get('POSTGRES_ADMIN_USER', 'postgres')
    admin_password = os.environ.get('POSTGRES_ADMIN_PASSWORD', 'postgres')
    admin_conn = psycopg2.connect(f"dbname='postgres' user='{admin_user}' host='{db_host}' password='{admin_password}'")
    admin_conn.autocommit = True
    cursor = admin_conn.cursor()

    try:
        cursor.execute(f"CREATE DATABASE {database_name}")
        cursor.execute(f"CREATE USER {username} WITH PASSWORD '{password}'")
        cursor.execute(f"GRANT ALL PRIVILEGES ON DATABASE {database_name} TO {username}")
        cursor.close()
        admin_conn.close()
        return True
    except Exception as e:
        print(f"Database creation failed: {e}")
        return False

def delete_database(database_name, username):
    db_host = os.environ.get('POSTGRES_HOST', 'localhost')
    admin_user = os.environ.get('POSTGRES_ADMIN_USER', 'postgres')
    admin_password = os.environ.get('POSTGRES_ADMIN_PASSWORD', 'postgres')
    admin_conn = psycopg2.connect(f"dbname='postgres' user='{admin_user}' host='{db_host}' password='{admin_password}'")
    admin_conn.autocommit = True
    cursor = admin_conn.cursor()

    try:
        cursor.execute(f"DROP DATABASE IF EXISTS {database_name}")
        cursor.execute(f"DROP USER IF EXISTS {username}")
        cursor.close()
        admin_conn.close()
        return True
    except Exception as e:
        print(f"Database deletion failed: {e}")
        return False

def test_database_connection(db_host, database_name, username, password):
    try:
        test_conn = psycopg2.connect(f"dbname='{database_name}' user='{username}' host='{db_host}' password='{password}'")
        test_conn.close()
        return 'Created'
    except psycopg2.OperationalError:
        return 'Failed'

@kopf.on.create('taka.edu.pl', 'v1', 'pgdatabases')
def create_fn(body, spec, patch, name, namespace, logger, **kwargs):
    database_name = spec.get('databaseName')
    username = spec.get('username')
    password = spec.get('password')
    service_name = spec.get('serviceName')
    db_host = os.environ.get('POSTGRES_HOST', 'localhost')

    kopf.event(body, type='Normal', reason='Creation', message='Creating database and initializing connection test.')
    patch.status['state'] = 'Pending'

    try:
        config.load_incluster_config()
    except ConfigException:
        config.load_kube_config()

    v1 = client.CoreV1Api()

    if create_database(database_name, username, password):
        service = client.V1Service(
            metadata=client.V1ObjectMeta(name=service_name),
            spec=client.V1ServiceSpec(
                type="ExternalName",
                external_name=f"{username}.db.example.com"
            )
        )
        v1.create_namespaced_service(namespace=namespace, body=service)

        final_status = test_database_connection(db_host, database_name, username, password)
        patch.status['state'] = final_status
    else:
        patch.status['state'] = 'Failed'

@kopf.on.delete('taka.edu.pl', 'v1', 'pgdatabases')
def delete_fn(spec, name, namespace, logger, **kwargs):
    database_name = spec.get('databaseName')
    username = spec.get('username')
    service_name = spec.get('serviceName')

    if delete_database(database_name, username):
        logger.info(f"Database {database_name} and user {username} successfully deleted.")
    else:
        logger.warning(f"Failed to delete database {database_name} and user {username}.")

    try:
        config.load_incluster_config()
    except config.ConfigException:
        config.load_kube_config()

    v1 = client.CoreV1Api()
    
    try:
        v1.delete_namespaced_service(name=service_name, namespace=namespace)
        logger.info(f"Service {service_name} successfully deleted.")
    except ApiException as e:
        logger.error(f"Failed to delete service {service_name}: {e.status}, {e.reason}")