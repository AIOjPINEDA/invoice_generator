"""
Expenses and income tracking module for the Invoice Generator application.
"""
from src.models.db import get_db_connection

def get_expense_categories():
    """Get all expense categories from the database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM expense_categories ORDER BY name')
        return cursor.fetchall()

def get_income_sources():
    """Get all income sources from the database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM income_sources ORDER BY name')
        return cursor.fetchall()

def add_expense(category_id, description, amount, date, payment_method=None, receipt_image=None, notes=None, tax_deductible=True):
    """Add a new expense to the database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO expenses (category_id, description, amount, date, payment_method, receipt_image, notes, tax_deductible)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (category_id, description, amount, date, payment_method, receipt_image, notes, tax_deductible))
        expense_id = cursor.lastrowid
        conn.commit()
        return expense_id

def add_income(source_id, description, amount, date, notes=None):
    """Add a new income to the database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO incomes (source_id, description, amount, date, notes)
        VALUES (?, ?, ?, ?, ?)
        ''', (source_id, description, amount, date, notes))
        income_id = cursor.lastrowid
        conn.commit()
        return income_id

def get_expenses(limit=None):
    """Get all expenses from the database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if limit:
            cursor.execute('''
            SELECT e.*, c.name as category_name
            FROM expenses e
            LEFT JOIN expense_categories c ON e.category_id = c.id
            ORDER BY e.date DESC LIMIT ?
            ''', (limit,))
        else:
            cursor.execute('''
            SELECT e.*, c.name as category_name
            FROM expenses e
            LEFT JOIN expense_categories c ON e.category_id = c.id
            ORDER BY e.date DESC
            ''')
        return cursor.fetchall()

def get_incomes(limit=None):
    """Get all incomes from the database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if limit:
            cursor.execute('''
            SELECT i.*, s.name as source_name
            FROM incomes i
            LEFT JOIN income_sources s ON i.source_id = s.id
            ORDER BY i.date DESC LIMIT ?
            ''', (limit,))
        else:
            cursor.execute('''
            SELECT i.*, s.name as source_name
            FROM incomes i
            LEFT JOIN income_sources s ON i.source_id = s.id
            ORDER BY i.date DESC
            ''')
        return cursor.fetchall()

def get_expenses_by_period(start_date, end_date):
    """Get expenses for a specific period"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
        SELECT e.*, c.name as category_name
        FROM expenses e
        LEFT JOIN expense_categories c ON e.category_id = c.id
        WHERE e.date BETWEEN ? AND ?
        ORDER BY e.date DESC
        ''', (start_date, end_date))
        return cursor.fetchall()

def get_incomes_by_period(start_date, end_date):
    """Get incomes for a specific period"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
        SELECT i.*, s.name as source_name
        FROM incomes i
        LEFT JOIN income_sources s ON i.source_id = s.id
        WHERE i.date BETWEEN ? AND ?
        ORDER BY i.date DESC
        ''', (start_date, end_date))
        return cursor.fetchall()

def get_expenses_by_category(year=None):
    """Get expenses grouped by category"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if year:
            cursor.execute('''
            SELECT c.name, SUM(e.amount) as total
            FROM expenses e
            JOIN expense_categories c ON e.category_id = c.id
            WHERE substr(e.date, 7, 4) = ?
            GROUP BY c.name
            ORDER BY total DESC
            ''', (str(year),))
        else:
            cursor.execute('''
            SELECT c.name, SUM(e.amount) as total
            FROM expenses e
            JOIN expense_categories c ON e.category_id = c.id
            GROUP BY c.name
            ORDER BY total DESC
            ''')
        return cursor.fetchall()

def get_tax_deductible_expenses(year):
    """Get tax deductible expenses for a specific year"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
        SELECT e.*, c.name as category_name
        FROM expenses e
        LEFT JOIN expense_categories c ON e.category_id = c.id
        WHERE e.tax_deductible = 1 AND substr(e.date, 7, 4) = ?
        ORDER BY e.date DESC
        ''', (str(year),))
        return cursor.fetchall()

def get_financial_summary(year):
    """Get financial summary for a specific year"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Get total expenses
        cursor.execute('''
        SELECT SUM(amount) FROM expenses
        WHERE substr(date, 7, 4) = ?
        ''', (str(year),))
        total_expenses = cursor.fetchone()[0] or 0

        # Get total incomes (including invoices)
        cursor.execute('''
        SELECT SUM(amount) FROM incomes
        WHERE substr(date, 7, 4) = ?
        ''', (str(year),))
        total_incomes = cursor.fetchone()[0] or 0

        # Get total from invoices
        cursor.execute('''
        SELECT SUM(s.unit_price * i.quantity)
        FROM invoices i
        JOIN services s ON i.service_id = s.id
        WHERE substr(i.date, 7, 4) = ?
        ''', (str(year),))
        total_invoices = cursor.fetchone()[0] or 0

        # Get tax deductible expenses
        cursor.execute('''
        SELECT SUM(amount) FROM expenses
        WHERE tax_deductible = 1 AND substr(date, 7, 4) = ?
        ''', (str(year),))
        tax_deductible = cursor.fetchone()[0] or 0

        return {
            'total_expenses': total_expenses,
            'total_incomes': total_incomes + total_invoices,
            'total_invoices': total_invoices,
            'tax_deductible': tax_deductible,
            'profit': (total_incomes + total_invoices) - total_expenses
        }


