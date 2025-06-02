"""
Unit tests for financial calculation functions in the Invoice Generator.
"""
import unittest
from tests.test_base import TestBase
from src import utils


class CalculationTests(TestBase):
    """Tests for financial calculation functions."""
    
    def test_calculate_financials_basic(self):
        """Test basic calculate_financials functionality."""
        # Arrange
        subtotal = 100.0
        iva_rate = 0.21
        irpf_rate = 0.15
        
        # Act
        result = utils.calculate_financials(subtotal, iva_rate, irpf_rate)
        
        # Assert
        self.assertEqual(result['subtotal'], 100.0)
        self.assertEqual(result['iva_amount'], 21.0)
        self.assertEqual(result['irpf_amount'], 15.0)
        self.assertEqual(result['total'], 106.0)
    
    def test_calculate_invoice_totals_with_taxes(self):
        """Test calculate_invoice_totals with both taxes enabled."""
        # Arrange
        service_price = 100.0
        quantity = 1
        apply_iva = True
        apply_irpf = True
        
        # Act
        result = utils.calculate_invoice_totals(service_price, quantity, apply_iva, apply_irpf)
        
        # Assert
        self.assertEqual(result['subtotal'], 100.0)
        self.assertEqual(result['iva_amount'], 21.0)
        self.assertEqual(result['irpf_amount'], 15.0)
        self.assertEqual(result['total'], 106.0)
    
    def test_calculate_invoice_totals_without_taxes(self):
        """Test calculate_invoice_totals with both taxes disabled."""
        # Arrange
        service_price = 100.0
        quantity = 1
        apply_iva = False
        apply_irpf = False
        
        # Act
        result = utils.calculate_invoice_totals(service_price, quantity, apply_iva, apply_irpf)
        
        # Assert
        self.assertEqual(result['subtotal'], 100.0)
        self.assertEqual(result['iva_amount'], 0.0)
        self.assertEqual(result['irpf_amount'], 0.0)
        self.assertEqual(result['total'], 100.0)
    
    def test_calculate_invoice_totals_only_iva(self):
        """Test calculate_invoice_totals with only IVA enabled."""
        # Arrange
        service_price = 100.0
        quantity = 1
        apply_iva = True
        apply_irpf = False
        
        # Act
        result = utils.calculate_invoice_totals(service_price, quantity, apply_iva, apply_irpf)
        
        # Assert
        self.assertEqual(result['subtotal'], 100.0)
        self.assertEqual(result['iva_amount'], 21.0)
        self.assertEqual(result['irpf_amount'], 0.0)
        self.assertEqual(result['total'], 121.0)
    
    def test_calculate_invoice_totals_only_irpf(self):
        """Test calculate_invoice_totals with only IRPF enabled."""
        # Arrange
        service_price = 100.0
        quantity = 1
        apply_iva = False
        apply_irpf = True
        
        # Act
        result = utils.calculate_invoice_totals(service_price, quantity, apply_iva, apply_irpf)
        
        # Assert
        self.assertEqual(result['subtotal'], 100.0)
        self.assertEqual(result['iva_amount'], 0.0)
        self.assertEqual(result['irpf_amount'], 15.0)
        self.assertEqual(result['total'], 85.0)


if __name__ == '__main__':
    unittest.main()
