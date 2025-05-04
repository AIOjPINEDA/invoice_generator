import database as db
import os
import sqlite3

# Remove the database if it exists
if os.path.exists('invoices.db'):
    os.remove('invoices.db')
    print("Removed existing database")

# Initialize the database
db.init_db()

# Check if tables were created
conn = sqlite3.connect('invoices.db')
cursor = conn.cursor()

# List tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("\nTables in the database:")
for table in tables:
    print(f"- {table[0]}")

# Check clients table
print("\nClients:")
cursor.execute("SELECT * FROM clients")
clients = cursor.fetchall()
for client in clients:
    print(client)

# Check services table
print("\nServices:")
cursor.execute("SELECT * FROM services")
services = cursor.fetchall()
for service in services:
    print(service)

conn.close()
