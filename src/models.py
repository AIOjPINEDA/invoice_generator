"""
Database models and operations for the Invoice Generator application.
"""
import sqlite3
import os
from datetime import datetime
from contextlib import contextmanager

# Database file
DB_FILE = 'db/invoices.db'

@contextmanager
def get_db_connection():
    """Context manager for database connections to ensure proper closing"""
    conn = sqlite3.connect(DB_FILE)
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Initialize database, create tables if they don't exist"""
    # Check if database file exists
    db_exists = os.path.exists(DB_FILE)

    # Flag to check if we need to update existing clients with currency info
    need_currency_update = False
    if db_exists:
        # Check if clients table already has currency columns
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(clients)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        if 'currency_code' not in column_names or 'currency_symbol' not in column_names:
            need_currency_update = True
        conn.close()

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Create tables if they don't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        tax_id TEXT NOT NULL,
        address TEXT NOT NULL,
        country TEXT NOT NULL,
        email TEXT,
        currency_code TEXT,
        currency_symbol TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY,
        description TEXT NOT NULL,
        unit_price REAL NOT NULL,
        unit_type TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY,
        client_id INTEGER NOT NULL,
        service_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        date TEXT NOT NULL,
        invoice_number TEXT NOT NULL,
        apply_iva BOOLEAN DEFAULT 1,
        apply_irpf BOOLEAN DEFAULT 1,
        FOREIGN KEY (client_id) REFERENCES clients (id),
        FOREIGN KEY (service_id) REFERENCES services (id)
    )
    ''')

    # Insert sample data if database was just created
    if not db_exists:
        try:
            # Sample clients
            cursor.execute('''
            INSERT INTO clients (name, tax_id, address, country, email, currency_code, currency_symbol) VALUES
            (?, ?, ?, ?, ?, ?, ?),
            (?, ?, ?, ?, ?, ?, ?)
            ''', ('Artificial Intelligence Orchestrator LLC', '84-4004678', '16192 Coastal Highway Delaware', 'EEUU', 'Sara.enrriquez@aio.ai', 'USD', '$',
                 'Empresa Ejemplo S.L.', 'B12345678', 'Calle Ejemplo 123', 'España', 'contacto@ejemplo.com', 'EUR', '€'))

            # Sample services
            cursor.execute('''
            INSERT INTO services (description, unit_price, unit_type) VALUES
            (?, ?, ?),
            (?, ?, ?),
            (?, ?, ?)
            ''', ('Consultoría técnica', 75.00, 'hora',
                 'Desarrollo de software', 65.00, 'hora',
                 'Mantenimiento mensual', 150.00, 'mes'))

            print("Sample data inserted successfully")
        except Exception as e:
            print(f"Error inserting sample data: {e}")

    conn.commit()

    # Update existing clients with currency information if needed
    if need_currency_update:
        print("Updating existing clients with currency information...")
        try:
            # Get all clients
            cursor.execute('SELECT id, country FROM clients')
            clients = cursor.fetchall()

            # Update each client based on their country
            for client_id, country in clients:
                if country.upper() in ['USA', 'EEUU', 'UNITED STATES', 'ESTADOS UNIDOS']:
                    cursor.execute(
                        'UPDATE clients SET currency_code = ?, currency_symbol = ? WHERE id = ?',
                        ('USD', '$', client_id)
                    )
                else:
                    cursor.execute(
                        'UPDATE clients SET currency_code = ?, currency_symbol = ? WHERE id = ?',
                        ('EUR', '€', client_id)
                    )

            conn.commit()
            print("Currency information updated successfully")
        except Exception as e:
            print(f"Error updating currency information: {e}")

    conn.close()

    print(f"Database initialized at {DB_FILE}")

def get_clients():
    """Get all clients from the database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM clients')
        return cursor.fetchall()

def get_services():
    """Get all services from the database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM services')
        return cursor.fetchall()

def get_client(client_id):
    """Get a specific client by ID"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM clients WHERE id = ?', (client_id,))
        return cursor.fetchone()

def get_service(service_id):
    """Get a specific service by ID"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM services WHERE id = ?', (service_id,))
        return cursor.fetchone()

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
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute('''
        INSERT INTO invoices (client_id, service_id, quantity, date, invoice_number, apply_iva, apply_irpf)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (client_id, service_id, quantity, date, invoice_number, apply_iva, apply_irpf))

        invoice_id = cursor.lastrowid
        conn.commit()

        return invoice_id

def get_recent_invoices(limit=5):
    """Get the most recent invoices with basic info"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Common invoice query fields
        invoice_query = '''
        SELECT i.id, i.invoice_number, i.date, c.name, s.description, i.quantity,
               s.unit_price * i.quantity AS subtotal,
               i.apply_iva, i.apply_irpf, i.client_id, c.currency_symbol
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
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # First get the invoice data
    cursor.execute('''
    SELECT * FROM invoices WHERE invoice_number = ? LIMIT 1
    ''', (invoice_number,))

    invoice_data = cursor.fetchone()

    if not invoice_data:
        conn.close()
        return None

    # Get client data separately
    cursor.execute('SELECT * FROM clients WHERE id = ?', (invoice_data[1],))
    client_data = cursor.fetchone()

    # Get service data separately
    cursor.execute('SELECT * FROM services WHERE id = ?', (invoice_data[2],))
    service_data = cursor.fetchone()

    conn.close()

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
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        # First check if the invoice exists
        cursor.execute('SELECT id FROM invoices WHERE invoice_number = ?', (invoice_number,))
        invoice = cursor.fetchone()

        if not invoice:
            conn.close()
            return False

        # Delete the invoice
        cursor.execute('DELETE FROM invoices WHERE invoice_number = ?', (invoice_number,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error deleting invoice: {e}")
        conn.rollback()
        conn.close()
        return False

def get_invoice_stats_by_month(year=None):
    """Get invoice statistics grouped by month"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Extract month from date field (format: DD/MM/YYYY)
    if year:
        cursor.execute('''
        SELECT
            CAST(substr(date, 4, 2) AS INTEGER) as month,
            COUNT(*) as count
        FROM invoices
        WHERE date IS NOT NULL
          AND length(date) >= 10
          AND substr(date, 7, 4) = ?
        GROUP BY month
        ORDER BY month
        ''', (str(year),))
    else:
        cursor.execute('''
        SELECT
            CAST(substr(date, 4, 2) AS INTEGER) as month,
            COUNT(*) as count
        FROM invoices
        WHERE date IS NOT NULL AND length(date) >= 10
        GROUP BY month
        ORDER BY month
        ''')

    stats = cursor.fetchall()
    conn.close()

    return stats

def get_revenue_stats_by_month(year=None):
    """Get revenue statistics grouped by month"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # First, get all invoices with their details
    if year:
        cursor.execute('''
        SELECT
            CAST(substr(i.date, 4, 2) AS INTEGER) as month,
            s.unit_price * i.quantity as amount,
            c.currency_code,
            c.currency_symbol
        FROM invoices i
        JOIN services s ON i.service_id = s.id
        JOIN clients c ON i.client_id = c.id
        WHERE i.date IS NOT NULL
          AND length(i.date) >= 10
          AND substr(i.date, 7, 4) = ?
        ORDER BY month
        ''', (str(year),))
    else:
        cursor.execute('''
        SELECT
            CAST(substr(i.date, 4, 2) AS INTEGER) as month,
            s.unit_price * i.quantity as amount,
            c.currency_code,
            c.currency_symbol
        FROM invoices i
        JOIN services s ON i.service_id = s.id
        JOIN clients c ON i.client_id = c.id
        WHERE i.date IS NOT NULL AND length(i.date) >= 10
        ORDER BY month
        ''')

    invoices = cursor.fetchall()
    conn.close()

    # Process the data to combine amounts by month
    monthly_totals = {}
    default_currency = '€'
    default_currency_code = 'EUR'

    for invoice in invoices:
        month = invoice[0]
        amount = invoice[1]
        currency_code = invoice[2] or default_currency_code
        currency_symbol = invoice[3] or default_currency

        # Convert USD to EUR if needed (using a simple conversion rate)
        if currency_code == 'USD':
            # Approximate conversion rate: 1 USD = 0.85 EUR
            amount = amount * 0.85
            currency_symbol = '€'
            currency_code = 'EUR'

        if month not in monthly_totals:
            monthly_totals[month] = {'total': 0, 'currency_symbol': currency_symbol, 'currency_code': currency_code}

        monthly_totals[month]['total'] += amount

    # Convert to the format expected by the API
    stats = [(month, data['total'], data['currency_symbol']) for month, data in monthly_totals.items()]
    stats.sort()  # Sort by month

    return stats

def get_invoice_stats_by_client(year=None):
    """Get invoice statistics grouped by client"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    if year:
        cursor.execute('''
        SELECT
            c.name,
            COUNT(*) as count
        FROM invoices i
        JOIN clients c ON i.client_id = c.id
        WHERE substr(i.date, 7, 4) = ?
        GROUP BY c.name
        ORDER BY count DESC
        ''', (str(year),))
    else:
        cursor.execute('''
        SELECT
            c.name,
            COUNT(*) as count
        FROM invoices i
        JOIN clients c ON i.client_id = c.id
        GROUP BY c.name
        ORDER BY count DESC
        ''')

    stats = cursor.fetchall()
    conn.close()

    return stats

def get_invoices_by_year(year):
    """Get all invoices for a specific year"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Extract year from date field (format: DD/MM/YYYY)
    cursor.execute('''
    SELECT i.id, i.invoice_number, i.date, c.name, s.description, i.quantity,
           s.unit_price * i.quantity AS subtotal,
           i.apply_iva, i.apply_irpf, i.client_id, c.currency_symbol
    FROM invoices i
    JOIN clients c ON i.client_id = c.id
    JOIN services s ON i.service_id = s.id
    WHERE substr(i.date, 7, 4) = ?
    ORDER BY i.date DESC
    ''', (str(year),))

    invoices = cursor.fetchall()
    conn.close()

    return invoices

def get_available_invoice_years():
    """Get list of years for which invoices exist"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Extract unique years from date field
    cursor.execute('''
    SELECT DISTINCT substr(date, 7, 4) as year
    FROM invoices
    WHERE date IS NOT NULL AND length(date) >= 10
    ORDER BY year DESC
    ''')

    years = [int(row[0]) for row in cursor.fetchall()]
    conn.close()

    return years

def get_monthly_invoice_stats_by_client(year=None):
    """Get monthly invoice statistics grouped by client"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    if year:
        cursor.execute('''
        SELECT
            CAST(substr(i.date, 4, 2) AS INTEGER) as month,
            c.name as client,
            COUNT(*) as count
        FROM invoices i
        JOIN clients c ON i.client_id = c.id
        WHERE substr(i.date, 7, 4) = ?
        GROUP BY month, client
        ORDER BY month, count DESC
        ''', (str(year),))
    else:
        cursor.execute('''
        SELECT
            CAST(substr(i.date, 4, 2) AS INTEGER) as month,
            c.name as client,
            COUNT(*) as count
        FROM invoices i
        JOIN clients c ON i.client_id = c.id
        GROUP BY month, client
        ORDER BY month, count DESC
        ''')

    stats = cursor.fetchall()
    conn.close()

    return stats

def add_client(name, tax_id, address, country, email, currency_code='EUR', currency_symbol='€'):
    """Add a new client to the database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO clients (name, tax_id, address, country, email, currency_code, currency_symbol)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (name, tax_id, address, country, email, currency_code, currency_symbol))

    client_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return client_id

def update_client(client_id, name, tax_id, address, country, email, currency_code='EUR', currency_symbol='€'):
    """Update an existing client in the database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
    UPDATE clients
    SET name = ?, tax_id = ?, address = ?, country = ?, email = ?, currency_code = ?, currency_symbol = ?
    WHERE id = ?
    ''', (name, tax_id, address, country, email, currency_code, currency_symbol, client_id))

    conn.commit()
    conn.close()

    return True

def delete_client(client_id):
    """Delete a client from the database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        # First check if the client has invoices
        cursor.execute('SELECT COUNT(*) FROM invoices WHERE client_id = ?', (client_id,))
        invoice_count = cursor.fetchone()[0]

        if invoice_count > 0:
            # Client has invoices, cannot delete
            conn.close()
            return False

        # Delete the client
        cursor.execute('DELETE FROM clients WHERE id = ?', (client_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error deleting client: {e}")
        conn.rollback()
        conn.close()
        return False

def add_service(description, unit_price, unit_type):
    """Add a new service to the database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO services (description, unit_price, unit_type)
    VALUES (?, ?, ?)
    ''', (description, unit_price, unit_type))

    service_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return service_id

def update_service(service_id, description, unit_price, unit_type):
    """Update an existing service in the database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
    UPDATE services
    SET description = ?, unit_price = ?, unit_type = ?
    WHERE id = ?
    ''', (description, unit_price, unit_type, service_id))

    conn.commit()
    conn.close()

    return True

def delete_service(service_id):
    """Delete a service from the database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        # First check if the service has invoices
        cursor.execute('SELECT COUNT(*) FROM invoices WHERE service_id = ?', (service_id,))
        invoice_count = cursor.fetchone()[0]

        if invoice_count > 0:
            # Service has invoices, cannot delete
            conn.close()
            return False

        # Delete the service
        cursor.execute('DELETE FROM services WHERE id = ?', (service_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error deleting service: {e}")
        conn.rollback()
        conn.close()
        return False
