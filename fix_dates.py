#!/usr/bin/env python3
"""
Script to check and fix date formats in the invoice database.
Ensures all dates are in DD/MM/YYYY format.
"""
import sqlite3
import re
from datetime import datetime

# Database file
DB_FILE = 'invoices.db'

def is_valid_date_format(date_str):
    """Check if the date string is in DD/MM/YYYY format"""
    pattern = r'^\d{2}/\d{2}/\d{4}$'
    return bool(re.match(pattern, date_str))

def convert_to_standard_format(date_str):
    """
    Convert various date formats to DD/MM/YYYY
    Handles:
    - YYYY-MM-DD
    - MM/DD/YYYY
    - D/M/YYYY
    - DD-MM-YYYY
    """
    # Try different formats
    formats = [
        '%Y-%m-%d',  # YYYY-MM-DD
        '%m/%d/%Y',  # MM/DD/YYYY
        '%d-%m-%Y',  # DD-MM-YYYY
        '%d/%m/%Y',  # DD/MM/YYYY (already correct, but might have leading zeros issues)
    ]
    
    for fmt in formats:
        try:
            date_obj = datetime.strptime(date_str, fmt)
            return date_obj.strftime('%d/%m/%Y')
        except ValueError:
            continue
    
    # If we get here, none of the formats worked
    print(f"Warning: Could not parse date '{date_str}'")
    return date_str

def fix_dates():
    """Check and fix all dates in the invoices table"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Get all invoices
    cursor.execute('SELECT id, date, invoice_number FROM invoices')
    invoices = cursor.fetchall()
    
    fixed_count = 0
    
    for invoice_id, date_str, invoice_number in invoices:
        if not is_valid_date_format(date_str):
            try:
                fixed_date = convert_to_standard_format(date_str)
                if fixed_date != date_str:
                    print(f"Fixing invoice {invoice_number}: {date_str} -> {fixed_date}")
                    cursor.execute('UPDATE invoices SET date = ? WHERE id = ?', (fixed_date, invoice_id))
                    fixed_count += 1
            except Exception as e:
                print(f"Error fixing date for invoice {invoice_number}: {e}")
    
    # Commit changes if any
    if fixed_count > 0:
        conn.commit()
        print(f"Fixed {fixed_count} date(s)")
    else:
        print("All dates are in the correct format (DD/MM/YYYY)")
    
    conn.close()

if __name__ == "__main__":
    fix_dates()
