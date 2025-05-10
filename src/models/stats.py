"""
Statistics and reporting functions for the Invoice Generator application.
"""
from src.models.db import get_db_connection, get_date_filter_clause

def get_invoice_stats_by_month(year=None):
    """Get invoice statistics grouped by month"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Extract month from date field (format: DD/MM/YYYY)
        date_filter = get_date_filter_clause(year)

        query = f'''
        SELECT
            CAST(substr(date, 4, 2) AS INTEGER) as month,
            COUNT(*) as count
        FROM invoices
        WHERE {date_filter}
        GROUP BY month
        ORDER BY month
        '''

        if year:
            cursor.execute(query, (str(year),))
        else:
            cursor.execute(query)

        stats = cursor.fetchall()
        return stats

def get_revenue_stats_by_month(year=None):
    """Get revenue statistics grouped by month"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # First, get all invoices with their details
        date_filter = get_date_filter_clause(year)
        date_filter = date_filter.replace('date', 'i.date')  # Adjust for table alias

        query = f'''
        SELECT
            CAST(substr(i.date, 4, 2) AS INTEGER) as month,
            s.unit_price * i.quantity as amount,
            c.currency_code,
            c.currency_symbol
        FROM invoices i
        JOIN services s ON i.service_id = s.id
        JOIN clients c ON i.client_id = c.id
        WHERE {date_filter}
        ORDER BY month
        '''

        if year:
            cursor.execute(query, (str(year),))
        else:
            cursor.execute(query)

        invoices = cursor.fetchall()

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
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Build query with conditional WHERE clause
        where_clause = ""
        if year:
            where_clause = "WHERE substr(i.date, 7, 4) = ?"

        query = f'''
        SELECT
            c.name,
            COUNT(*) as count
        FROM invoices i
        JOIN clients c ON i.client_id = c.id
        {where_clause}
        GROUP BY c.name
        ORDER BY count DESC
        '''

        if year:
            cursor.execute(query, (str(year),))
        else:
            cursor.execute(query)

        stats = cursor.fetchall()
        return stats

def get_monthly_invoice_stats_by_client(year=None):
    """Get monthly invoice statistics grouped by client"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Build query with conditional WHERE clause
        where_clause = ""
        if year:
            where_clause = "WHERE substr(i.date, 7, 4) = ?"

        query = f'''
        SELECT
            CAST(substr(i.date, 4, 2) AS INTEGER) as month,
            c.name as client,
            COUNT(*) as count
        FROM invoices i
        JOIN clients c ON i.client_id = c.id
        {where_clause}
        GROUP BY month, client
        ORDER BY month, count DESC
        '''

        if year:
            cursor.execute(query, (str(year),))
        else:
            cursor.execute(query)

        stats = cursor.fetchall()
        return stats
