"""
Script para inicializar una base de datos vacía con la estructura correcta.
Este script crea una base de datos con las tablas necesarias pero sin datos personales.
"""
import os
import sqlite3

# Nombre del archivo de base de datos
DB_FILE = 'invoices.db'

def init_empty_db():
    """Inicializa una base de datos vacía con la estructura correcta"""
    # Si la base de datos ya existe, la eliminamos
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    
    # Conectamos a la base de datos (se creará automáticamente)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Creamos la tabla de clientes
    cursor.execute('''
    CREATE TABLE clients (
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
    
    # Creamos la tabla de servicios
    cursor.execute('''
    CREATE TABLE services (
        id INTEGER PRIMARY KEY,
        description TEXT NOT NULL,
        unit_price REAL NOT NULL,
        unit_type TEXT NOT NULL
    )
    ''')
    
    # Creamos la tabla de facturas
    cursor.execute('''
    CREATE TABLE invoices (
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
    
    # Agregamos algunos datos de ejemplo (opcional)
    # Cliente de ejemplo
    cursor.execute('''
    INSERT INTO clients (name, tax_id, address, country, email, currency_code, currency_symbol)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', ('Empresa Ejemplo S.L.', 'B12345678', 'Calle Ejemplo 123', 'España', 'contacto@ejemplo.com', 'EUR', '€'))
    
    # Servicio de ejemplo
    cursor.execute('''
    INSERT INTO services (description, unit_price, unit_type)
    VALUES (?, ?, ?)
    ''', ('Servicio de consultoría', 50.0, 'hora'))
    
    # Guardamos los cambios y cerramos la conexión
    conn.commit()
    conn.close()
    
    print(f"Base de datos vacía creada en {DB_FILE}")

if __name__ == "__main__":
    init_empty_db()
