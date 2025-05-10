"""
BBVA bank statement import functionality.
"""
import os
import openpyxl
from datetime import datetime
from src.finance import expenses
from src.finance.category_matcher import match_expense_category, match_income_source

def import_bbva_statement(file_path, default_expense_category=None, default_income_source=None, check_duplicates=True):
    """
    Import expenses and incomes from BBVA bank statement.

    Args:
        file_path: Path to the BBVA Excel file
        default_expense_category: Default category ID for expenses
        default_income_source: Default source ID for incomes
        check_duplicates: Whether to check for duplicate transactions

    Returns:
        dict: Result of the import operation
    """
    if not os.path.exists(file_path):
        return {
            'success': False,
            'message': f'File not found: {file_path}',
            'expenses_imported': 0,
            'incomes_imported': 0,
            'errors': [f'File not found: {file_path}']
        }

    try:
        # Load the workbook
        wb = openpyxl.load_workbook(file_path)

        # Get the active sheet
        sheet = wb.active

        # Get all values
        rows = []
        for row in sheet.iter_rows(values_only=True):
            rows.append(row)

        # Skip header row
        data_rows = rows[1:]

        # Initialize counters
        expenses_imported = 0
        incomes_imported = 0
        errors = []
        transactions = []

        # Process each row
        for row in data_rows:
            try:
                # Skip empty rows
                if not row or len(row) < 3:
                    continue

                date = row[0]
                description = row[1]
                amount = row[2]

                # Skip rows with missing data
                if not date or not description or amount is None:
                    continue

                # Convert date to string format if it's a datetime object
                if isinstance(date, datetime):
                    date_str = date.strftime('%d/%m/%Y')
                else:
                    # Try to parse the date string
                    try:
                        date_obj = datetime.strptime(str(date), '%d/%m/%Y')
                        date_str = date_obj.strftime('%d/%m/%Y')
                    except ValueError:
                        # If parsing fails, use the original value
                        date_str = str(date)

                # Clean up description
                if description:
                    description = str(description).strip()
                else:
                    description = "Sin descripción"

                # Add transaction to list for duplicate checking
                transactions.append({
                    'date': date_str,
                    'description': description,
                    'amount': amount,
                    'type': 'expense' if amount < 0 else 'income'
                })

                # Determine if it's an expense or income based on the amount
                if amount < 0:
                    # It's an expense (negative amount)
                    # Make the amount positive for storage
                    amount = abs(amount)

                    # Categorize the expense based on the description using the improved matcher
                    category_id = match_expense_category(description)

                    # If no category was found, use the default
                    if not category_id and default_expense_category:
                        category_id = default_expense_category

                    # Determine payment method based on description
                    payment_method = 'Tarjeta' if 'TARJETA' in description.upper() else 'Transferencia'

                    # If we have a category, save the expense
                    if category_id:
                        expenses.add_expense(
                            category_id=category_id,
                            description=description,
                            amount=amount,
                            date=date_str,
                            payment_method=payment_method,
                            notes='Imported from BBVA statement',
                            tax_deductible=is_tax_deductible(description, category_id)
                        )
                        expenses_imported += 1
                else:
                    # It's an income (positive amount)
                    # Categorize the income based on the description using the improved matcher
                    source_id = match_income_source(description)

                    # If no source was found, use the default
                    if not source_id and default_income_source:
                        source_id = default_income_source

                    # If we have a source, save the income
                    if source_id:
                        expenses.add_income(
                            source_id=source_id,
                            description=description,
                            amount=amount,
                            date=date_str,
                            notes='Imported from BBVA statement'
                        )
                        incomes_imported += 1

            except Exception as e:
                errors.append(str(e))

        result = {
            'success': True,
            'message': f'Successfully imported {expenses_imported} expenses and {incomes_imported} incomes',
            'expenses_imported': expenses_imported,
            'incomes_imported': incomes_imported,
            'errors': errors,
            'transactions': transactions
        }

        # Check for duplicates if requested
        if check_duplicates and transactions:
            duplicates = detect_duplicate_transactions(transactions)
            if duplicates:
                result['duplicates'] = duplicates
                result['message'] += f' (Found {len(duplicates)} potential duplicates)'

        return result

    except Exception as e:
        return {
            'success': False,
            'message': f'Error importing data: {str(e)}',
            'expenses_imported': 0,
            'incomes_imported': 0,
            'errors': [str(e)]
        }

def detect_duplicate_transactions(transactions, days_threshold=3):
    """
    Detect potential duplicate transactions in the database.

    Args:
        transactions (list): List of transaction dictionaries
        days_threshold (int): Number of days to consider for duplicates

    Returns:
        list: List of potential duplicate transactions
    """
    # Get existing transactions from database
    existing_expenses = expenses.get_expenses()
    existing_incomes = expenses.get_incomes()

    # Convert to dictionaries for easier comparison
    existing_transactions = []

    for expense in existing_expenses:
        existing_transactions.append({
            'id': expense[0],
            'date': expense[3],
            'description': expense[2],
            'amount': -expense[4],  # Negative for expenses
            'type': 'expense'
        })

    for income in existing_incomes:
        existing_transactions.append({
            'id': income[0],
            'date': income[3],
            'description': income[2],
            'amount': income[4],
            'type': 'income'
        })

    # Find potential duplicates
    duplicates = []

    for new_trans in transactions:
        for existing in existing_transactions:
            # Check if amounts match
            if abs(new_trans['amount'] - existing['amount']) < 0.01:
                # Check if descriptions are similar
                if (new_trans['description'].lower() in existing['description'].lower() or
                    existing['description'].lower() in new_trans['description'].lower()):

                    # Check if dates are close
                    try:
                        new_date = datetime.strptime(new_trans['date'], '%d/%m/%Y')
                        existing_date = datetime.strptime(existing['date'], '%d/%m/%Y')
                        days_diff = abs((new_date - existing_date).days)

                        if days_diff <= days_threshold:
                            duplicates.append({
                                'new_transaction': new_trans,
                                'existing_transaction': existing,
                                'days_difference': days_diff
                            })
                    except ValueError:
                        # If date parsing fails, still consider it a potential duplicate
                        duplicates.append({
                            'new_transaction': new_trans,
                            'existing_transaction': existing,
                            'days_difference': 'unknown'
                        })

    return duplicates

def is_tax_deductible(description, category_id):
    """
    Determine if an expense is tax deductible based on its description and category.

    Args:
        description: The expense description
        category_id: The expense category ID

    Returns:
        bool: True if tax deductible, False otherwise
    """
    # Non-deductible categories
    non_deductible_categories = [3, 10]  # Comidas, Otros

    # Check if category is non-deductible
    if category_id in non_deductible_categories:
        return False

    # Check for specific non-deductible keywords in description
    non_deductible_keywords = ['personal', 'privado', 'regalo', 'ocio', 'entretenimiento']
    desc_lower = description.lower()

    for keyword in non_deductible_keywords:
        if keyword in desc_lower:
            return False

    # Default to deductible
    return True
