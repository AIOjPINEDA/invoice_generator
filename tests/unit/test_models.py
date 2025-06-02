"""
Unit tests for database models in the Invoice Generator.
"""
import unittest
from tests.test_base import TestBase, DatabaseTestMixin
from src.models.clients import add_client, get_clients
from src.models.services import add_service, get_services


class ModelsTests(TestBase, DatabaseTestMixin):
    """Tests for database models."""
    
    def test_add_and_get_client(self):
        """Test adding and retrieving a client."""
        # Arrange
        client_data = {
            'name': 'Test Client',
            'tax_id': 'TC123',
            'address': '123 Test St',
            'country': 'Spain',
            'email': 'test@client.com',
            'currency_code': 'EUR',
            'currency_symbol': '€'
        }
        
        # Act
        client_id = add_client(**client_data)
        clients = get_clients()
        
        # Assert
        self.assertIsNotNone(client_id)
        self.assertGreater(len(clients), 0)
        
        # Find our client in the list
        added_client = None
        for client in clients:
            if client[0] == client_id:  # client[0] is the ID
                added_client = client
                break
        
        self.assertIsNotNone(added_client)
        self.assertEqual(added_client[1], client_data['name'])  # client[1] is name
        self.assertEqual(added_client[2], client_data['tax_id'])  # client[2] is tax_id
    
    def test_add_and_get_service(self):
        """Test adding and retrieving a service."""
        # Arrange
        service_data = {
            'description': 'Test Service',
            'unit_price': 100.0,
            'unit_type': 'hour'
        }
        
        # Act
        service_id = add_service(**service_data)
        services = get_services()
        
        # Assert
        self.assertIsNotNone(service_id)
        self.assertGreater(len(services), 0)
        
        # Find our service in the list
        added_service = None
        for service in services:
            if service[0] == service_id:  # service[0] is the ID
                added_service = service
                break
        
        self.assertIsNotNone(added_service)
        self.assertEqual(added_service[1], service_data['description'])  # service[1] is description
        self.assertEqual(added_service[2], service_data['unit_price'])  # service[2] is unit_price
    
    def test_database_tables_exist(self):
        """Test that all required database tables exist."""
        # Assert
        self.assertTableExists('clients')
        self.assertTableExists('services')
        self.assertTableExists('invoices')
        self.assertTableExists('estimates')
    
    def test_client_table_structure(self):
        """Test that client table has required columns."""
        # Assert
        self.assertColumnExists('clients', 'id')
        self.assertColumnExists('clients', 'name')
        self.assertColumnExists('clients', 'tax_id')
        self.assertColumnExists('clients', 'address')
        self.assertColumnExists('clients', 'country')
        self.assertColumnExists('clients', 'email')
        self.assertColumnExists('clients', 'currency_code')
        self.assertColumnExists('clients', 'currency_symbol')
    
    def test_service_table_structure(self):
        """Test that service table has required columns."""
        # Assert
        self.assertColumnExists('services', 'id')
        self.assertColumnExists('services', 'description')
        self.assertColumnExists('services', 'unit_price')
        self.assertColumnExists('services', 'unit_type')


if __name__ == '__main__':
    unittest.main()
