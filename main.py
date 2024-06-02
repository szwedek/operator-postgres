import kopf
import os
from kubernetes import client, config
from kubernetes.config import ConfigException
from classes.postgresdatabase import PostgresDatabase

db_host = os.environ.get('DB_HOST', 'localhost')
db_user = os.environ.get('DB_USER', 'postgres')
db_password = os.environ.get('DB_PASSWORD', 'postgres')

db_instance = PostgresDatabase(db_host=db_host, admin_user=db_user, admin_password=db_password)

@kopf.on.create('taka.edu.pl', 'v1', 'pgdatabases')
def create_fn(body, spec, patch, namespace, **kwargs) -> None:
    database_name = spec.get('databaseName')
    username = spec.get('username')
    password = spec.get('password')
    service_name = spec.get('serviceName')

    kopf.event(body, type='Normal', reason='Creation', message='Creating database and initializing connection test.')
    patch.status['state'] = 'Pending'

    try:
        config.load_incluster_config()
    except ConfigException:
        config.load_kube_config()

    v1 = client.CoreV1Api()

    if db_instance.create_database(database_name, username, password):
        service = client.V1Service(
            metadata=client.V1ObjectMeta(name=service_name),
            spec=client.V1ServiceSpec(
                type="ExternalName",
                external_name=f"{username}.db.example.com"
            )
        )
        v1.create_namespaced_service(namespace=namespace, body=service)

        final_status = db_instance.test_database_connection()
        patch.status['state'] = final_status
    else:
        patch.status['state'] = 'Failed'

@kopf.on.delete('taka.edu.pl', 'v1', 'pgdatabases')
def delete_fn(spec, namespace, logger, **kwargs) -> None:
    database_name = spec.get('databaseName')
    username = spec.get('username')
    service_name = spec.get('serviceName')

    if db_instance.delete_database(database_name, username):
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
    except client.ApiException as e:
        logger.error(f"Failed to delete service {service_name}: {e.status}, {e.reason}")