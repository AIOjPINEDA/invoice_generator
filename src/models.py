import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    """ Create a database connection to the SQLite database specified by db_file """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"Connection established to {db_file} SQLite database.")
    except Error as e:
        print(f"Error connecting to database: {e}")
    return conn

def init_db(conn):
    """ Initialize the database with the required tables """
    cursor = conn.cursor()
    
    # Create clients table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        address TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Create services table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Create invoices table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY,
        client_id INTEGER NOT NULL,
        service_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        date TEXT NOT NULL,
        invoice_number TEXT NOT NULL UNIQUE, -- Ensure invoice numbers are unique
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

    # Create estimates table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS estimates (
        id INTEGER PRIMARY KEY,
        client_id INTEGER NOT NULL,
        service_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        issue_date TEXT NOT NULL, -- Changed from 'date' to 'issue_date' for clarity
        estimate_number TEXT NOT NULL UNIQUE,
        apply_iva BOOLEAN DEFAULT 1,
        apply_irpf BOOLEAN DEFAULT 1,
        subtotal REAL,
        iva_amount REAL,
        irpf_amount REAL,
        total_amount REAL,
        currency_code TEXT,
        currency_symbol TEXT,
        status TEXT DEFAULT 'Draft', -- e.g., 'Draft', 'Sent', 'Accepted', 'Rejected', 'Expired'
        valid_until TEXT, -- Expiration date of the estimate (format "YYYY-MM-DD")
        notes TEXT, -- Any specific notes for the estimate
        terms TEXT, -- Specific terms and conditions for the estimate
        FOREIGN KEY (client_id) REFERENCES clients (id),
        FOREIGN KEY (service_id) REFERENCES services (id)
    )
    ''')

    # Insert sample data if database was just created
    cursor.execute('SELECT COUNT(*) FROM clients')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
        INSERT INTO clients (name, email, phone, address)
        VALUES
        ('John Doe', 'john@example.com', '123456789', '123 Elm St'),
        ('Jane Smith', 'jane@example.com', '987654321', '456 Oak St')
        ''')

    cursor.execute('SELECT COUNT(*) FROM services')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
        INSERT INTO services (name, description, price)
        VALUES
        ('Service A', 'Description for Service A', 100.0),
        ('Service B', 'Description for Service B', 150.0)
        ''')

    cursor.execute('SELECT COUNT(*) FROM invoices')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
        INSERT INTO invoices (client_id, service_id, quantity, date, invoice_number, subtotal, iva_amount, irpf_amount, total_amount, currency_code, currency_symbol)
        VALUES
        (1, 1, 2, '2023-10-01', 'INV-1001', 200.0, 42.0, 8.0, 250.0, 'USD', '$'),
        (2, 2, 1, '2023-10-02', 'INV-1002', 150.0, 31.5, 6.0, 187.5, 'USD', '$')
        ''')

    cursor.execute('SELECT COUNT(*) FROM estimates')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
        INSERT INTO estimates (client_id, service_id, quantity, issue_date, estimate_number, subtotal, iva_amount, irpf_amount, total_amount, currency_code, currency_symbol, status, valid_until, notes, terms)
        VALUES
        (1, 1, 2, '2023-09-01', 'EST-2001', 180.0, 37.8, 7.2, 225.0, 'USD', '$', 'Draft', '2023-09-30', 'This is a note.', 'Terms and conditions apply.'),
        (2, 2, 1, '2023-09-05', 'EST-2002', 135.0, 28.35, 5.4, 168.75, 'USD', '$', 'Sent', '2023-09-25', '', '')
        ''')

    conn.commit()
    print("Database initialization complete.")

def main():
    database = "my_database.db"

    # Create a database connection
    conn = create_connection(database)

    # Initialize the database
    if conn is not None:
        init_db(conn)
        conn.close()
    else:
        print("Error! cannot create the database connection.")

if __name__ == '__main__':
    main()