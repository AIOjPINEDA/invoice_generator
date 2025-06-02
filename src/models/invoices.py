"""
Invoice-related database operations for the Invoice Generator application.

Recent updates:
- Fixed save_invoice to calculate and store all financial fields
- Updated get_recent_invoices to return all necessary fields for templates
- Added proper currency handling and tax calculations
"""
from datetime import datetime
from src.models.db import get_db_connection

def generate_invoice_number(client_id):
    """Generate a sequential invoice number based on previous month, client and count"""
    now = datetime.now()
    # Calculate previous month (for work done in the previous month)
    if now.month == 1:  # If January, previous month is December of previous year
        prev_month = 12
        prev_year = now.year - 1
    else:
        prev_month = now.month - 1
        prev_year = now.year

    # Format: YYMM (previous month)
    date_code = f"{prev_year % 100:02d}{prev_month:02d}"

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Get client name
        cursor.execute('SELECT name FROM clients WHERE id = ?', (client_id,))
        client_name = cursor.fetchone()[0]

        # Get first letter of each word (up to 3) and convert to uppercase
        words = client_name.split()
        prefix = ''.join([word[0] for word in words[:3]]).upper()

        # Count invoices from this date for this client
        cursor.execute(
            'SELECT COUNT(*) FROM invoices WHERE invoice_number LIKE ? AND client_id = ?',
            (f'{date_code}-{prefix}-%', client_id)
        )
        count = cursor.fetchone()[0]

        # Create invoice number: YYMM-PRE-COUNT (e.g., 2504-AIO-1)
        return f"{date_code}-{prefix}-{(count + 1):01d}"

def save_invoice(client_id, service_id, quantity, date, invoice_number, apply_iva=True, apply_irpf=True):
    """Save an invoice to the database with tax application preferences"""
    from src import utils

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Get service price to calculate totals
        cursor.execute('SELECT unit_price FROM services WHERE id = ?', (service_id,))
        service_price = cursor.fetchone()[0]

        # Get client currency info
        cursor.execute('SELECT currency_code, currency_symbol FROM clients WHERE id = ?', (client_id,))
        client_currency = cursor.fetchone()
        currency_code = client_currency[0] if client_currency and client_currency[0] else 'EUR'
        currency_symbol = client_currency[1] if client_currency and client_currency[1] else '€'

        # Calculate totals using the utils function
        totals = utils.calculate_invoice_totals(service_price, quantity, apply_iva, apply_irpf)

        cursor.execute('''
        INSERT INTO invoices (client_id, service_id, quantity, date, invoice_number, apply_iva, apply_irpf,
                             subtotal, iva_amount, irpf_amount, total_amount, currency_code, currency_symbol)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (client_id, service_id, quantity, date, invoice_number, apply_iva, apply_irpf,
              totals['subtotal'], totals['iva_amount'], totals['irpf_amount'], totals['total'],
              currency_code, currency_symbol))

        invoice_id = cursor.lastrowid
        conn.commit()

        return invoice_id

def get_recent_invoices(limit=5):
    """Get the most recent invoices with basic info"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Common invoice query fields - updated to include all necessary fields
        invoice_query = '''
        SELECT i.id, i.invoice_number, i.date, c.name, s.description, i.quantity,
               COALESCE(i.subtotal, s.unit_price * i.quantity) AS subtotal,
               i.apply_iva, i.apply_irpf, i.client_id,
               COALESCE(c.currency_symbol, '€') AS currency_symbol,
               COALESCE(i.iva_amount, 0) AS iva_amount,
               COALESCE(i.irpf_amount, 0) AS irpf_amount,
               COALESCE(i.total_amount, s.unit_price * i.quantity) AS total_amount,
               COALESCE(i.currency_code, 'EUR') AS currency_code
        FROM invoices i
        JOIN clients c ON i.client_id = c.id
        JOIN services s ON i.service_id = s.id
        '''

        # Common order by clause
        order_by = '''
        ORDER BY
            substr(i.date, 7, 4) DESC,  -- Year
            substr(i.date, 4, 2) DESC,  -- Month
            substr(i.date, 1, 2) DESC   -- Day
        '''

        # First, get invoices from AIO (limited to 2)
        cursor.execute(
            invoice_query +
            "WHERE c.name LIKE '%Artificial%' " +
            order_by +
            "LIMIT 2"
        )
        aio_invoices = cursor.fetchall()

        # Then, get other recent invoices
        cursor.execute(
            invoice_query +
            "WHERE c.name NOT LIKE '%Artificial%' " +
            order_by +
            "LIMIT ?",
            (limit - len(aio_invoices),)
        )
        other_invoices = cursor.fetchall()

        # Combine and sort all invoices by date
        all_invoices = aio_invoices + other_invoices

        # Sort by date (DD/MM/YYYY format)
        all_invoices.sort(key=lambda x: (
            int(x[2].split('/')[2]),  # Year
            int(x[2].split('/')[1]),  # Month
            int(x[2].split('/')[0])   # Day
        ), reverse=True)

        # Limit to the specified number of invoices
        return all_invoices[:limit]

def get_invoice_by_number(invoice_number):
    """Get a specific invoice by its number"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # First get the invoice data
        cursor.execute('''
        SELECT * FROM invoices WHERE invoice_number = ? LIMIT 1
        ''', (invoice_number,))

        invoice_data = cursor.fetchone()

        if not invoice_data:
            return None

        # Get client data separately
        cursor.execute('SELECT * FROM clients WHERE id = ?', (invoice_data[1],))
        client_data = cursor.fetchone()

        # Get service data separately
        cursor.execute('SELECT * FROM services WHERE id = ?', (invoice_data[2],))
        service_data = cursor.fetchone()

        # Format the data into a structured dictionary
        invoice = {
            'id': invoice_data[0],
            'client_id': invoice_data[1],
            'service_id': invoice_data[2],
            'quantity': invoice_data[3],
            'date': invoice_data[4],
            'invoice_number': invoice_data[5],
            'apply_iva': invoice_data[6],
            'apply_irpf': invoice_data[7],
            'client': client_data,  # Complete client data
            'service': service_data  # Complete service data
        }

        return invoice

def delete_invoice(invoice_number):
    """Delete an invoice from the database by its number"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # First check if the invoice exists
            cursor.execute('SELECT id FROM invoices WHERE invoice_number = ?', (invoice_number,))
            invoice = cursor.fetchone()

            if not invoice:
                return False

            # Delete the invoice
            cursor.execute('DELETE FROM invoices WHERE invoice_number = ?', (invoice_number,))
            conn.commit()
            return True
    except Exception as e:
        print(f"Error deleting invoice: {e}")
        return False

def get_invoices_by_year(year):
    """Get all invoices for a specific year"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Extract year from date field (format: DD/MM/YYYY)
        cursor.execute('''
        SELECT i.id, i.invoice_number, i.date, c.name, s.description, i.quantity,
               COALESCE(i.subtotal, s.unit_price * i.quantity) AS subtotal,
               i.apply_iva, i.apply_irpf, i.client_id,
               COALESCE(c.currency_symbol, '€') AS currency_symbol,
               COALESCE(i.iva_amount, 0) AS iva_amount,
               COALESCE(i.irpf_amount, 0) AS irpf_amount,
               COALESCE(i.total_amount, s.unit_price * i.quantity) AS total_amount,
               COALESCE(i.currency_code, 'EUR') AS currency_code
        FROM invoices i
        JOIN clients c ON i.client_id = c.id
        JOIN services s ON i.service_id = s.id
        WHERE substr(i.date, 7, 4) = ?
        ORDER BY i.date DESC
        ''', (str(year),))

        invoices = cursor.fetchall()
        return invoices

def get_available_invoice_years():
    """Get list of years for which invoices exist"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Extract unique years from date field
        cursor.execute('''
        SELECT DISTINCT substr(date, 7, 4) as year
        FROM invoices
        WHERE date IS NOT NULL AND length(date) >= 10
        ORDER BY year DESC
        ''')

        years = [int(row[0]) for row in cursor.fetchall()]
        return years
