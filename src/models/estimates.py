"""
Estimate-related database operations for the Invoice Generator application.
"""
import sqlite3 # Added import for sqlite3.Error
from datetime import datetime
from src.models.db import get_db_connection
from src.utils import calculate_financials, load_config # Import the new utility function

def generate_estimate_number(issue_date_obj):
    """Generate a sequential estimate number (e.g., YYYY-MM-PXXX)."""
    # issue_date_obj should be a datetime object
    year_month_prefix = issue_date_obj.strftime("%Y-%m") # Format YYYY-MM

    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Count estimates from this year and month
        query = f"SELECT COUNT(*) FROM estimates WHERE estimate_number LIKE '{year_month_prefix}-P%'"
        cursor.execute(query)
        count = cursor.fetchone()[0]
        # Create estimate number: YYYY-MM-PXXX (e.g., 2024-07-P001)
        return f"{year_month_prefix}-P{(count + 1):03d}"

# TODO: Adapt to handle multiple services per estimate.
# This would require a separate estimate_items table.
def save_estimate(client_id, service_id, quantity, issue_date_str, valid_until_date_str, irpf_rate_decimal, notes, terms, estimate_number_override=None):
    """Save a new estimate to the database, performing calculations."""
    
    estimate_number = estimate_number_override if estimate_number_override else generate_estimate_number(datetime.strptime(issue_date_str, "%Y-%m-%d"))

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # 1. Fetch client currency
            cursor.execute("SELECT currency_code, currency_symbol FROM clients WHERE id = ?", (client_id,))
            client_currency_row = cursor.fetchone()
            if not client_currency_row:
                raise ValueError(f"Client with ID {client_id} not found.")
            client_currency_code, _ = client_currency_row  # currency_symbol not used here

            # 2. Fetch service unit price
            cursor.execute("SELECT unit_price FROM services WHERE id = ?", (service_id,)) # Assuming 'unit_price' from schema
            service_row = cursor.fetchone()
            if not service_row:
                raise ValueError(f"Service with ID {service_id} not found.")
            unit_price = service_row[0]

            # 3. Calculate subtotal
            subtotal = float(quantity) * float(unit_price)
            
            # 4. Use calculate_financials for tax and total calculation
            # Get IVA rate from configuration for consistency
            config = load_config()
            default_iva = config.get('tax_rates', {}).get('default_iva', 0.21)
            financials = calculate_financials(subtotal, default_iva, float(irpf_rate_decimal))
            
            # 5. Insert into estimates table
            sql = '''INSERT INTO estimates (
                    estimate_number, client_id, service_id, quantity, issue_date, 
                    valid_until_date, subtotal, iva_amount, irpf_rate, irpf_amount, total, 
                    currency, status, notes, terms
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            cursor.execute(sql, (
                estimate_number, client_id, service_id, quantity, issue_date_str,
                valid_until_date_str, financials['subtotal'], financials['iva_amount'], 
                float(irpf_rate_decimal), financials['irpf_amount'], financials['total'],
                client_currency_code, 
                'Draft', 
                notes, terms
            ))
            conn.commit()
            return estimate_number # Return the generated estimate number
    except sqlite3.Error as e:
        print(f"Database error in save_estimate: {e}")
        # Potentially re-raise or handle more gracefully
        raise
    except ValueError as e:
        print(f"Value error in save_estimate: {e}")
        # Potentially re-raise or handle
        raise
    except Exception as e:
        print(f"An unexpected error occurred in save_estimate: {e}")
        raise

def get_estimate_by_number(estimate_number):
    """Get estimate details by its number, including client and service info."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Joined with clients and services to get comprehensive details
        # Ensure column names match the actual schema in src/models.py
        # The estimates table in src/models.py has:
        # estimate_number, client_id, service_id, quantity, issue_date, valid_until_date,
        # subtotal, iva_amount, irpf_rate, irpf_amount, total, currency, status, notes, terms
        # The services table has 'description' not 'name', and 'price', 'unit_type'
        # The clients table has 'name', 'tax_id', 'address', 'country', 'email', 'currency_code', 'currency_symbol'
        
        # Corrected JOIN: services.description, services.price, services.unit_type
        # Corrected SELECT for estimate fields
        cursor.execute('''
            SELECT 
                e.id, e.estimate_number, e.issue_date, e.valid_until_date,
                e.subtotal, e.iva_amount, e.irpf_rate, e.irpf_amount, e.total,
                e.currency, e.status, e.notes, e.terms,
                c.id as client_id, c.name as client_name, c.tax_id as client_tax_id,
                c.address as client_address, c.country as client_country, c.email as client_email,
                c.currency_code as client_currency_code, c.currency_symbol as client_currency_symbol,
                s.id as service_id, s.description as service_description, -- Changed from s.name
                s.unit_price as service_unit_price, -- Changed from s.price
                s.unit_type as service_unit_type, -- Changed from s.unit
                e.quantity
            FROM estimates e
            JOIN clients c ON e.client_id = c.id
            JOIN services s ON e.service_id = s.id 
            WHERE e.estimate_number = ?
        ''', (estimate_number,))
        
        row = cursor.fetchone()
        
        if row:
            # Convert row to dict for easier access
            columns = [desc[0] for desc in cursor.description]
            estimate_data = dict(zip(columns, row))
            return estimate_data
        return None

def get_recent_estimates(limit=5):
    """Get recent estimates with client and service information."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Corrected JOIN: services.description, services.price, services.unit_type
        # Corrected SELECT for estimate fields
        cursor.execute('''
            SELECT 
                e.estimate_number, e.issue_date, e.total, e.currency, e.status,
                c.name as client_name,
                s.description as service_description -- Changed from s.name
            FROM estimates e
            JOIN clients c ON e.client_id = c.id
            JOIN services s ON e.service_id = s.id 
            ORDER BY e.issue_date DESC, e.id DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        estimates_list = []
        if rows:
            columns = [desc[0] for desc in cursor.description]
            for row_data in rows:
                estimates_list.append(dict(zip(columns, row_data)))
        return estimates_list

def delete_estimate(estimate_number):
    """Delete an estimate from the database by its number."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM estimates WHERE estimate_number = ?", (estimate_number,))
            conn.commit()
            return cursor.rowcount > 0 # Returns True if a row was deleted
    except sqlite3.Error as e:
        print(f"Database error in delete_estimate: {e}")
        return False
