"""
Client-related database operations for the Invoice Generator application.
"""
from src.models.db import get_db_connection

def get_clients():
    """Get all clients from the database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM clients')
        return cursor.fetchall()

def get_client(client_id):
    """Get a specific client by ID"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM clients WHERE id = ?', (client_id,))
        return cursor.fetchone()

def add_client(name, tax_id, address, country, email, currency_code='EUR', currency_symbol='€'):
    """Add a new client to the database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute('''
        INSERT INTO clients (name, tax_id, address, country, email, currency_code, currency_symbol)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, tax_id, address, country, email, currency_code, currency_symbol))

        client_id = cursor.lastrowid
        conn.commit()
        return client_id

def update_client(client_id, name, tax_id, address, country, email, currency_code='EUR', currency_symbol='€'):
    """Update an existing client in the database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute('''
        UPDATE clients
        SET name = ?, tax_id = ?, address = ?, country = ?, email = ?, currency_code = ?, currency_symbol = ?
        WHERE id = ?
        ''', (name, tax_id, address, country, email, currency_code, currency_symbol, client_id))

        conn.commit()
        return True

def delete_client(client_id):
    """Delete a client from the database"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # First check if the client has invoices
            cursor.execute('SELECT COUNT(*) FROM invoices WHERE client_id = ?', (client_id,))
            invoice_count = cursor.fetchone()[0]

            if invoice_count > 0:
                # Client has invoices, cannot delete
                return False

            # Delete the client
            cursor.execute('DELETE FROM clients WHERE id = ?', (client_id,))
            conn.commit()
            return True
    except Exception as e:
        print(f"Error deleting client: {e}")
        return False
