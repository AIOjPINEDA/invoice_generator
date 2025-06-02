"""
Utility functions for the Invoice Generator application.
"""
import os
import json
from datetime import datetime
from flask import flash, redirect, request

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

def validate_form_fields(required_fields, form_data):
    """
    Validate required form fields and return missing fields.

    Args:
        required_fields (list): List of required field names
        form_data (dict): Form data to validate

    Returns:
        list: List of missing field names
    """
    missing_fields = []
    for field in required_fields:
        if not form_data.get(field):
            missing_fields.append(field)
    return missing_fields

def validate_and_convert_quantity(quantity_str):
    """
    Validate and convert quantity string to integer.

    Args:
        quantity_str (str): Quantity as string

    Returns:
        tuple: (success: bool, value: int or None, error_message: str or None)
    """
    try:
        quantity = int(quantity_str)
        if quantity <= 0:
            return False, None, "Quantity must be greater than 0"
        return True, quantity, None
    except (ValueError, TypeError):
        return False, None, "Invalid quantity format"

def validate_and_convert_irpf_rate(irpf_rate_str):
    """
    Validate and convert IRPF rate string to float.

    Args:
        irpf_rate_str (str): IRPF rate as string

    Returns:
        tuple: (success: bool, value: float or None, error_message: str or None)
    """
    try:
        irpf_rate = float(irpf_rate_str) if irpf_rate_str else 0.0
        if irpf_rate < 0 or irpf_rate > 1:
            return False, None, "IRPF rate must be between 0 and 1"
        return True, irpf_rate, None
    except (ValueError, TypeError):
        return False, None, "Invalid IRPF rate format"

def handle_validation_error(error_message, referrer_url=None):
    """
    Handle validation errors with consistent flash message and redirect.

    Args:
        error_message (str): Error message to display
        referrer_url (str): URL to redirect to (defaults to request referrer or home)

    Returns:
        Flask redirect response
    """
    flash(error_message, 'error')
    return redirect(referrer_url or request.referrer or '/')

def format_date_for_display(date_str, input_format='%Y-%m-%d', output_format='%d/%m/%Y'):
    """
    Convert date string from one format to another.

    Args:
        date_str (str): Date string to convert
        input_format (str): Input date format
        output_format (str): Output date format

    Returns:
        str: Formatted date string or original string if conversion fails
    """
    try:
        date_obj = datetime.strptime(date_str, input_format)
        return date_obj.strftime(output_format)
    except (ValueError, TypeError):
        return date_str
