"""
Service-related database operations for the Invoice Generator application.
"""
from src.models.db import get_db_connection

def get_services():
    """Get all services from the database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM services')
        return cursor.fetchall()

def get_service(service_id):
    """Get a specific service by ID"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM services WHERE id = ?', (service_id,))
        return cursor.fetchone()

def add_service(description, unit_price, unit_type):
    """Add a new service to the database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute('''
        INSERT INTO services (description, unit_price, unit_type)
        VALUES (?, ?, ?)
        ''', (description, unit_price, unit_type))

        service_id = cursor.lastrowid
        conn.commit()
        return service_id

def update_service(service_id, description, unit_price, unit_type):
    """Update an existing service in the database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute('''
        UPDATE services
        SET description = ?, unit_price = ?, unit_type = ?
        WHERE id = ?
        ''', (description, unit_price, unit_type, service_id))

        conn.commit()
        return True

def delete_service(service_id):
    """Delete a service from the database"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # First check if the service has invoices
            cursor.execute('SELECT COUNT(*) FROM invoices WHERE service_id = ?', (service_id,))
            invoice_count = cursor.fetchone()[0]

            if invoice_count > 0:
                # Service has invoices, cannot delete
                return False

            # Delete the service
            cursor.execute('DELETE FROM services WHERE id = ?', (service_id,))
            conn.commit()
            return True
    except Exception as e:
        print(f"Error deleting service: {e}")
        return False
