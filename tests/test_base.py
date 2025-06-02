"""
Base test class with common utilities and setup for Invoice Generator tests.
"""
import unittest
import os
import sys
import tempfile
import shutil
from unittest.mock import patch

# Add the parent directory to sys.path to import application modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.db import init_db, get_db_connection
from src import utils


class TestBase(unittest.TestCase):
    """Base test class with common setup and utilities."""
    
    @classmethod
    def setUpClass(cls):
        """Set up class-level test fixtures."""
        # Create a temporary directory for test databases
        cls.test_dir = tempfile.mkdtemp()
        cls.original_db_file = None
        
    @classmethod
    def tearDownClass(cls):
        """Clean up class-level test fixtures."""
        # Remove temporary directory
        if hasattr(cls, 'test_dir') and os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a unique test database for each test
        self.test_db_file = os.path.join(self.test_dir, f'test_{self._testMethodName}.db')
        
        # Patch the database file path
        self.db_patcher = patch('src.models.db.DB_FILE', self.test_db_file)
        self.db_patcher.start()
        
        # Initialize test database
        init_db()
        
        # Store original config for restoration
        self.original_config = utils.load_config()
    
    def tearDown(self):
        """Clean up after each test method."""
        # Stop database patching
        self.db_patcher.stop()
        
        # Remove test database file
        if os.path.exists(self.test_db_file):
            os.remove(self.test_db_file)
        
        # Restore original config
        utils.save_config(self.original_config)
    
    def get_test_client_data(self):
        """Get test client data for testing."""
        return {
            'name': 'Test Client LLC',
            'tax_id': 'TEST123456',
            'address': '123 Test Street',
            'country': 'Test Country',
            'email': 'test@testclient.com',
            'currency_code': 'EUR',
            'currency_symbol': '€'
        }
    
    def get_test_service_data(self):
        """Get test service data for testing."""
        return {
            'description': 'Test Service',
            'unit_price': 100.0,
            'unit_type': 'hour'
        }
    
    def create_test_client(self):
        """Create a test client in the database and return its ID."""
        from src.models.clients import add_client
        client_data = self.get_test_client_data()
        return add_client(**client_data)
    
    def create_test_service(self):
        """Create a test service in the database and return its ID."""
        from src.models.services import add_service
        service_data = self.get_test_service_data()
        return add_service(**service_data)
    
    def assertFloatEqual(self, first, second, places=2, msg=None):
        """Assert that two floats are equal within specified decimal places."""
        self.assertAlmostEqual(first, second, places=places, msg=msg)
    
    def assertDictContainsSubset(self, subset, dictionary, msg=None):
        """Assert that dictionary contains all key-value pairs from subset."""
        for key, value in subset.items():
            self.assertIn(key, dictionary, msg=f"Key '{key}' not found in dictionary")
            self.assertEqual(dictionary[key], value, 
                           msg=f"Value for key '{key}' does not match. Expected: {value}, Got: {dictionary[key]}")


class DatabaseTestMixin:
    """Mixin class providing database testing utilities."""
    
    def assertTableExists(self, table_name):
        """Assert that a table exists in the database."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?", 
                (table_name,)
            )
            result = cursor.fetchone()
            self.assertIsNotNone(result, f"Table '{table_name}' does not exist")
    
    def assertColumnExists(self, table_name, column_name):
        """Assert that a column exists in a table."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            self.assertIn(column_name, column_names, 
                         f"Column '{column_name}' not found in table '{table_name}'")
    
    def assertRecordCount(self, table_name, expected_count):
        """Assert that a table has the expected number of records."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            actual_count = cursor.fetchone()[0]
            self.assertEqual(actual_count, expected_count,
                           f"Expected {expected_count} records in '{table_name}', got {actual_count}")
    
    def get_record_by_id(self, table_name, record_id):
        """Get a record from a table by its ID."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table_name} WHERE id = ?", (record_id,))
            return cursor.fetchone()


class FlaskTestMixin:
    """Mixin class providing Flask testing utilities."""
    
    def setUp(self):
        """Set up Flask test client."""
        super().setUp()
        from src import create_app
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """Clean up Flask test client."""
        self.app_context.pop()
        super().tearDown()
    
    def assertResponseOK(self, response, msg=None):
        """Assert that response status code is 200."""
        self.assertEqual(response.status_code, 200, 
                        msg or f"Expected status 200, got {response.status_code}")
    
    def assertResponseRedirect(self, response, msg=None):
        """Assert that response is a redirect (3xx status code)."""
        self.assertTrue(300 <= response.status_code < 400,
                       msg or f"Expected redirect status, got {response.status_code}")
    
    def assertResponseError(self, response, expected_status=None, msg=None):
        """Assert that response is an error (4xx or 5xx status code)."""
        if expected_status:
            self.assertEqual(response.status_code, expected_status,
                           msg or f"Expected status {expected_status}, got {response.status_code}")
        else:
            self.assertTrue(response.status_code >= 400,
                           msg or f"Expected error status, got {response.status_code}")
