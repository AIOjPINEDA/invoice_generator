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

def calculate_invoice_totals(service_price, quantity, apply_iva=True, apply_irpf=True):
    """Calculate invoice totals including taxes"""
    subtotal = service_price * quantity
    iva = subtotal * 0.21 if apply_iva else 0
    irpf = subtotal * 0.15 if apply_irpf else 0
    total = subtotal + iva - irpf

    return {
        'subtotal': subtotal,
        'iva': iva,
        'irpf': irpf,
        'total': total
    }


