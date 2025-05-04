import os
import sys
import unittest
from flask import Flask

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app
import database as db

class RoutesTestCase(unittest.TestCase):
    """Test case for application routes"""

    def setUp(self):
        """Set up test client"""
        self.app = app.app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        # Initialize database
        db.init_db()

    def test_index_route(self):
        """Test the index route returns successful response"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200, "Index route failed")
        self.assertIn(b'html', response.data, "Response does not contain HTML")

    def test_get_client_route(self):
        """Test the get_client API endpoint"""
        # Get all clients
        clients = db.get_clients()
        if clients:
            client_id = clients[0][0]
            response = self.client.get(f'/get_client/{client_id}')
            self.assertEqual(response.status_code, 200, "Get client route failed")
            self.assertIn(b'name', response.data, "Response does not contain client name")
        else:
            self.skipTest("No clients in database to test")

    def test_get_service_route(self):
        """Test the get_service API endpoint"""
        # Get all services
        services = db.get_services()
        if services:
            service_id = services[0][0]
            response = self.client.get(f'/get_service/{service_id}')
            self.assertEqual(response.status_code, 200, "Get service route failed")
            self.assertIn(b'description', response.data, "Response does not contain service description")
        else:
            self.skipTest("No services in database to test")


if __name__ == '__main__':
    unittest.main()
