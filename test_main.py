import unittest
from unittest import mock
from kubernetes.config.config_exception import ConfigException
from main import create_fn, delete_fn

class OperatorTest(unittest.TestCase):

    @mock.patch('main.kopf.event')
    @mock.patch('main.config')
    @mock.patch('main.client.CoreV1Api')
    def test_create_fn(self, mock_core_v1_api, mock_config, mock_kopf_event):
        mock_body = {}
        mock_spec = {
            'databaseName': 'test_db',
            'username': 'test_user',
            'password': 'test_password',
            'serviceName': 'test_service'
        }
        mock_patch = mock.MagicMock()
        mock_patch.status = {'state': ''}
        mock_namespace = 'test_namespace'
    
        mock_db_instance = mock.MagicMock()
        mock_db_instance.create_database.return_value = True
        mock_db_instance.test_database_connection.return_value = 'Connected'
    
        with mock.patch('main.db_instance', mock_db_instance):
            mock_config.load_incluster_config.side_effect = ConfigException
            mock_config.load_kube_config.return_value = None
    
            mock_v1 = mock_core_v1_api.return_value
            mock_v1.create_namespaced_service.return_value = None
    
            create_fn(mock_body, mock_spec, mock_patch, mock_namespace)
    
            mock_v1.create_namespaced_service.assert_called_once()
            self.assertEqual(mock_patch.status['state'], 'Connected')
            mock_kopf_event.assert_called_with(mock_body, type='Normal', reason='Creation', message='Creating database and initializing connection test.')


    @mock.patch('main.kopf.event')
    @mock.patch('main.config')
    @mock.patch('main.client.CoreV1Api')
    def test_create_fn_failure(self, mock_core_v1_api, mock_config, mock_kopf_event):
        mock_body = {}
        mock_spec = {
            'databaseName': 'test_db',
            'username': 'test_user',
            'password': 'test_password',
            'serviceName': 'test_service'
        }
        mock_patch = mock.MagicMock()
        mock_patch.status = {'state': ''}
        mock_namespace = 'test_namespace'
    
        mock_db_instance = mock.MagicMock()
        mock_db_instance.create_database.return_value = False
    
        with mock.patch('main.db_instance', mock_db_instance):
            mock_config.load_incluster_config.side_effect = ConfigException
            mock_config.load_kube_config.return_value = None
    
            create_fn(mock_body, mock_spec, mock_patch, mock_namespace)
    
            mock_v1 = mock_core_v1_api.return_value
            mock_v1.create_namespaced_service.assert_not_called()
            self.assertEqual(mock_patch.status['state'], 'Failed')
            mock_kopf_event.assert_called_with(mock_body, type='Warning', reason='Failed', message='Failed to create database.')


    @mock.patch('main.config')
    @mock.patch('main.client.CoreV1Api')
    def test_delete_fn(self, mock_core_v1_api, mock_config):
        mock_spec = {
            'databaseName': 'test_db',
            'username': 'test_user',
            'serviceName': 'test_service'
        }
        mock_namespace = 'test_namespace'
        mock_logger = mock.MagicMock()

        mock_db_instance = mock.MagicMock()
        mock_db_instance.delete_database.return_value = True

        with mock.patch('main.db_instance', mock_db_instance):
            mock_config.load_incluster_config.side_effect = ConfigException
            mock_config.load_kube_config.return_value = None

            mock_v1 = mock_core_v1_api.return_value
            mock_v1.delete_namespaced_service.return_value = None

            delete_fn(mock_spec, mock_namespace, mock_logger)

            mock_v1.delete_namespaced_service.assert_called_once_with(name='test_service', namespace='test_namespace')
            mock_logger.info.assert_called_with('Service test_service successfully deleted.')

if __name__ == '__main__':
    unittest.main()
