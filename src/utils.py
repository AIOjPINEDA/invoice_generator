"""
Utility functions for the Invoice Generator application.
"""
import os
import json

# Configuration file
CONFIG_FILE = 'config.json'

def load_config():
    """Load configuration from config.json file"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")

    # Default configuration if file doesn't exist or has errors
    return {
        "currency": {
            "code": "EUR",
            "symbol": "€"
        },
        "issuer": {
            "name": "JAIME A. PINEDA MORENO",
            "tax_id": "60155423G",
            "address": "Calle arte conceptual 10 Portal 2, 5ºA",
            "city": "28051 Madrid",
            "country": "Spain",
            "phone": "+34 602 612 640",
            "email": "jaime.pineda@aiorchestrator.ai",
            "bank_iban": "ES29 0182 4919 7502 0158 2010",
            "bank_name": "BBVA"
        },
        "preferences": {
            "last_client_id": None,
            "last_service_id": None
        },
        # Added default tax rates here for central management
        "tax_rates": {
            "default_iva": 0.21,
            "default_irpf": 0.15 
        }
    }

def save_config(config):
    """Save configuration to config.json file"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

def calculate_financials(subtotal, iva_rate, irpf_rate):
    """
    Calculates IVA amount, IRPF amount, and total based on subtotal and tax rates.

    Args:
        subtotal (float): The base amount before taxes.
        iva_rate (float): The IVA rate (e.g., 0.21 for 21%).
        irpf_rate (float): The IRPF rate (e.g., 0.15 for 15%).

    Returns:
        dict: A dictionary containing 'subtotal', 'iva_amount', 
              'irpf_amount', and 'total'.
    """
    iva_amount = subtotal * iva_rate
    irpf_amount = subtotal * irpf_rate
    total = subtotal + iva_amount - irpf_amount
    return {
        'subtotal': round(subtotal, 2),
        'iva_amount': round(iva_amount, 2),
        'irpf_amount': round(irpf_amount, 2),
        'total': round(total, 2)
    }

def calculate_invoice_totals(service_price, quantity, apply_iva=True, apply_irpf=True):
    """Calculate invoice totals including taxes.
    This function might be refactored or deprecated if invoice creation
    logic is updated to use calculate_financials more directly with rates from config.
    """
    config = load_config()
    default_iva = config.get('tax_rates', {}).get('default_iva', 0.21)
    default_irpf = config.get('tax_rates', {}).get('default_irpf', 0.15)

    subtotal = service_price * quantity
    
    current_iva_rate = default_iva if apply_iva else 0
    current_irpf_rate = default_irpf if apply_irpf else 0
    
    return calculate_financials(subtotal, current_iva_rate, current_irpf_rate)


