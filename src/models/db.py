"""
Database connection and initialization for the Invoice Generator application.
"""
import sqlite3
import os
from contextlib import contextmanager

# Database file
DB_FILE = 'db/invoices.db'

@contextmanager
def get_db_connection(db_path=None):  # Add db_path parameter with a default
    """Context manager for database connections to ensure proper closing"""
    path_to_connect = db_path if db_path else DB_FILE  # Use db_path if provided
    conn = sqlite3.connect(path_to_connect)
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
    need_invoice_update = False

    if db_exists:
        # Check if clients table already has currency columns
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(clients)")
            columns = cursor.fetchall()
            column_names = [column[1] for column in columns]
            if 'currency_code' not in column_names or 'currency_symbol' not in column_names:
                need_currency_update = True

            # Check if invoices table has all required columns
            cursor.execute("PRAGMA table_info(invoices)")
            invoice_columns = cursor.fetchall()
            invoice_column_names = [column[1] for column in invoice_columns]
            required_invoice_columns = ['subtotal', 'iva_amount', 'irpf_amount', 'total_amount', 'currency_code', 'currency_symbol']
            for col in required_invoice_columns:
                if col not in invoice_column_names:
                    need_invoice_update = True
                    break

    with get_db_connection() as conn:
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
            subtotal REAL,
            iva_amount REAL,
            irpf_amount REAL,
            total_amount REAL,
            currency_code TEXT,
            currency_symbol TEXT,
            FOREIGN KEY (client_id) REFERENCES clients (id),
            FOREIGN KEY (service_id) REFERENCES services (id)
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS estimates (
            id INTEGER PRIMARY KEY,
            estimate_number TEXT NOT NULL,
            client_id INTEGER NOT NULL,
            service_id INTEGER NOT NULL,
            quantity REAL NOT NULL,
            issue_date TEXT NOT NULL,
            valid_until_date TEXT NOT NULL,
            subtotal REAL NOT NULL,
            iva_amount REAL NOT NULL,
            irpf_rate REAL NOT NULL,
            irpf_amount REAL NOT NULL,
            total REAL NOT NULL,
            currency TEXT NOT NULL,
            status TEXT NOT NULL,
            notes TEXT,
            terms TEXT,
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

        # Update invoices table structure if needed
        if need_invoice_update:
            print("Updating invoices table structure...")
            # Add missing columns to invoices table
            required_invoice_columns = [
                ('subtotal', 'REAL'),
                ('iva_amount', 'REAL'),
                ('irpf_amount', 'REAL'),
                ('total_amount', 'REAL'),
                ('currency_code', 'TEXT'),
                ('currency_symbol', 'TEXT')
            ]

            for col_name, col_type in required_invoice_columns:
                try:
                    cursor.execute(f'ALTER TABLE invoices ADD COLUMN {col_name} {col_type}')
                    print(f"Added column {col_name} to invoices table.")
                except Exception as e:
                    # Column might already exist, ignore the error
                    pass

            conn.commit()
            print("Invoices table structure updated successfully.")

    print(f"Database initialized at {DB_FILE}")

def get_date_filter_clause(year=None):
    """Generate SQL clause for date filtering"""
    base_clause = "date IS NOT NULL AND length(date) >= 10"
    if year:
        return f"{base_clause} AND substr(date, 7, 4) = ?"
    return base_clause
