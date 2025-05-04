import sqlite3
import os
import sys
import unittest

# Add the parent directory to sys.path to import the database module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import database as db

class DatabaseTestCase(unittest.TestCase):
    """Test case for database functionality and structure"""

    def setUp(self):
        """Setup test environment"""
        self.db_file = db.DB_FILE
        # Ensure database exists
        if not os.path.exists(self.db_file):
            db.init_db()

    def test_database_exists(self):
        """Test if database file exists"""
        self.assertTrue(os.path.exists(self.db_file), f"Database file {self.db_file} not found")

    def test_clients_table(self):
        """Test clients table structure and content"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Test table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='clients'")
        self.assertIsNotNone(cursor.fetchone(), "Table 'clients' not found")
        
        # Test schema
        cursor.execute("PRAGMA table_info(clients)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        expected_columns = ['id', 'name', 'tax_id', 'address', 'country', 'email']
        for column in expected_columns:
            self.assertIn(column, column_names, f"Column '{column}' missing from clients table")
        
        # Test data exists
        cursor.execute("SELECT COUNT(*) FROM clients")
        count = cursor.fetchone()[0]
        self.assertGreater(count, 0, "No client records found")
        
        conn.close()

    def test_services_table(self):
        """Test services table structure and content"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Test table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='services'")
        self.assertIsNotNone(cursor.fetchone(), "Table 'services' not found")
        
        # Test schema
        cursor.execute("PRAGMA table_info(services)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        expected_columns = ['id', 'description', 'unit_price', 'unit_type']
        for column in expected_columns:
            self.assertIn(column, column_names, f"Column '{column}' missing from services table")
        
        # Test data exists
        cursor.execute("SELECT COUNT(*) FROM services")
        count = cursor.fetchone()[0]
        self.assertGreater(count, 0, "No service records found")
        
        conn.close()

    def test_invoices_table(self):
        """Test invoices table structure"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Test table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='invoices'")
        self.assertIsNotNone(cursor.fetchone(), "Table 'invoices' not found")
        
        # Test schema
        cursor.execute("PRAGMA table_info(invoices)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        expected_columns = ['id', 'client_id', 'service_id', 'quantity', 'date', 'invoice_number', 'apply_iva', 'apply_irpf']
        for column in expected_columns:
            self.assertIn(column, column_names, f"Column '{column}' missing from invoices table")
        
        conn.close()

    def test_invoice_number_generation(self):
        """Test invoice number generation function"""
        # Use the first client for testing
        clients = db.get_clients()
        if clients:
            client_id = clients[0][0]
            invoice_number = db.generate_invoice_number(client_id)
            
            # Check format: YYYYMMDD-XXX-N
            parts = invoice_number.split('-')
            self.assertEqual(len(parts), 3, f"Invoice number format incorrect: {invoice_number}")
            self.assertEqual(len(parts[0]), 8, f"Date part incorrect length: {parts[0]}")
            self.assertTrue(parts[0].isdigit(), f"Date part not numeric: {parts[0]}")
            self.assertTrue(parts[2].isdigit(), f"Sequence part not numeric: {parts[2]}")


if __name__ == '__main__':
    unittest.main()
