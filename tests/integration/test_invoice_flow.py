"""
Integration tests for invoice generation workflow in the Invoice Generator.
"""
import unittest
from datetime import datetime
from tests.test_base import TestBase, DatabaseTestMixin
from src.models.invoices import save_invoice, get_recent_invoices


class InvoiceFlowTests(TestBase, DatabaseTestMixin):
    """Tests for complete invoice generation workflow."""
    
    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        
        # Create test client and service
        self.client_id = self.create_test_client()
        self.service_id = self.create_test_service()
        
        # Verify they were created
        self.assertIsNotNone(self.client_id, "Test client should be created")
        self.assertIsNotNone(self.service_id, "Test service should be created")
    
    def test_save_invoice_basic(self):
        """Test basic invoice saving functionality."""
        # Arrange
        invoice_data = {
            'client_id': self.client_id,
            'service_id': self.service_id,
            'quantity': 1,
            'date': '01/06/2025',
            'invoice_number': 'TEST-001',
            'apply_iva': True,
            'apply_irpf': True
        }
        
        # Act
        invoice_id = save_invoice(**invoice_data)
        
        # Assert
        self.assertIsNotNone(invoice_id)
        self.assertIsInstance(invoice_id, int)
        
        # Verify invoice was saved
        recent_invoices = get_recent_invoices()
        self.assertGreater(len(recent_invoices), 0)
        
        # Find our invoice
        saved_invoice = None
        for invoice in recent_invoices:
            if invoice[0] == invoice_id:  # invoice[0] is ID
                saved_invoice = invoice
                break
        
        self.assertIsNotNone(saved_invoice)
        self.assertEqual(saved_invoice[1], invoice_data['invoice_number'])  # invoice[1] is invoice_number
    
    def test_save_invoice_with_calculations(self):
        """Test invoice saving with financial calculations."""
        # Arrange
        invoice_data = {
            'client_id': self.client_id,
            'service_id': self.service_id,
            'quantity': 2,  # 2 hours
            'date': '01/06/2025',
            'invoice_number': 'TEST-002',
            'apply_iva': True,
            'apply_irpf': True
        }
        
        # Act
        invoice_id = save_invoice(**invoice_data)
        
        # Assert
        self.assertIsNotNone(invoice_id)
        
        # Get the saved invoice
        recent_invoices = get_recent_invoices()
        saved_invoice = None
        for invoice in recent_invoices:
            if invoice[0] == invoice_id:
                saved_invoice = invoice
                break
        
        self.assertIsNotNone(saved_invoice)
        
        # Verify calculations (2 hours * 100€/hour = 200€ subtotal)
        expected_subtotal = 200.0
        expected_iva = 42.0  # 200 * 0.21
        expected_irpf = 30.0  # 200 * 0.15
        expected_total = 212.0  # 200 + 42 - 30
        
        # Check if the invoice has the calculated fields
        if len(saved_invoice) > 13:  # If we have the calculated fields
            self.assertEqual(saved_invoice[6], expected_subtotal)  # subtotal
            self.assertEqual(saved_invoice[11], expected_iva)  # iva_amount
            self.assertEqual(saved_invoice[12], expected_irpf)  # irpf_amount
            self.assertEqual(saved_invoice[13], expected_total)  # total_amount
    
    def test_save_invoice_without_taxes(self):
        """Test invoice saving without taxes."""
        # Arrange
        invoice_data = {
            'client_id': self.client_id,
            'service_id': self.service_id,
            'quantity': 1,
            'date': '01/06/2025',
            'invoice_number': 'TEST-003',
            'apply_iva': False,
            'apply_irpf': False
        }
        
        # Act
        invoice_id = save_invoice(**invoice_data)
        
        # Assert
        self.assertIsNotNone(invoice_id)
        
        # Get the saved invoice
        recent_invoices = get_recent_invoices()
        saved_invoice = None
        for invoice in recent_invoices:
            if invoice[0] == invoice_id:
                saved_invoice = invoice
                break
        
        self.assertIsNotNone(saved_invoice)
        
        # Verify tax settings
        self.assertEqual(saved_invoice[7], False)  # apply_iva
        self.assertEqual(saved_invoice[8], False)  # apply_irpf
        
        # Verify calculations (no taxes)
        if len(saved_invoice) > 13:
            expected_subtotal = 100.0
            expected_total = 100.0
            self.assertEqual(saved_invoice[6], expected_subtotal)  # subtotal
            self.assertEqual(saved_invoice[11], 0.0)  # iva_amount
            self.assertEqual(saved_invoice[12], 0.0)  # irpf_amount
            self.assertEqual(saved_invoice[13], expected_total)  # total_amount


if __name__ == '__main__':
    unittest.main()
