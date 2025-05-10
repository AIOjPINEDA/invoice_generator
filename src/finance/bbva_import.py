"""
BBVA bank statement import functionality.
"""
import openpyxl
from datetime import datetime
from src import expenses

def import_bbva_statement(file_path, default_expense_category=None, default_income_source=None):
    """
    Import expenses and incomes from BBVA bank statement.
    
    Args:
        file_path: Path to the BBVA Excel file
        default_expense_category: Default category ID for expenses
        default_income_source: Default source ID for incomes
        
    Returns:
        dict: Result of the import operation
    """
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
        
        # Process each row
        for row in data_rows:
            try:
                # This is a placeholder implementation
                # The actual implementation would depend on the structure of the BBVA Excel file
                # For now, we'll assume a simple structure:
                # - Column 0: Date
                # - Column 1: Description
                # - Column 2: Amount
                
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
                        date_str = date.strftime('%d/%m/%Y')
                    except ValueError:
                        # If parsing fails, use the original value
                        date_str = str(date)
                
                # Determine if it's an expense or income based on the amount
                if amount < 0:
                    # It's an expense (negative amount)
                    # Make the amount positive for storage
                    amount = abs(amount)
                    
                    # Categorize the expense based on the description
                    category_id = categorize_expense(description)
                    
                    # If no category was found, use the default
                    if not category_id and default_expense_category:
                        category_id = default_expense_category
                    
                    # If we have a category, save the expense
                    if category_id:
                        expenses.add_expense(
                            category_id=category_id,
                            description=description,
                            amount=amount,
                            date=date_str,
                            payment_method='Bank Transfer',
                            notes='Imported from BBVA statement',
                            tax_deductible=is_tax_deductible(description, category_id)
                        )
                        expenses_imported += 1
                else:
                    # It's an income (positive amount)
                    # Categorize the income based on the description
                    source_id = categorize_income(description)
                    
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
        
        return {
            'success': True,
            'message': f'Successfully imported {expenses_imported} expenses and {incomes_imported} incomes',
            'expenses_imported': expenses_imported,
            'incomes_imported': incomes_imported,
            'errors': errors
        }
    
    except Exception as e:
        return {
            'success': False,
            'message': f'Error importing data: {str(e)}',
            'expenses_imported': 0,
            'incomes_imported': 0,
            'errors': [str(e)]
        }

def categorize_expense(description):
    """
    Categorize an expense based on its description.
    
    Args:
        description: The expense description
        
    Returns:
        int: Category ID or None if no match
    """
    # Convert description to lowercase for case-insensitive matching
    desc_lower = description.lower()
    
    # Define category mappings (description keywords -> category ID)
    category_mappings = {
        1: ['oficina', 'material', 'papeleria', 'tinta', 'impresora'],
        2: ['transporte', 'taxi', 'uber', 'cabify', 'metro', 'bus', 'tren', 'renfe', 'gasolina', 'parking', 'peaje'],
        3: ['restaurante', 'comida', 'cafe', 'bar', 'menu', 'cena', 'almuerzo', 'desayuno'],
        4: ['abogado', 'notario', 'gestor', 'asesor', 'consultor'],
        5: ['seguridad social', 'cotizacion', 'autonomos'],
        6: ['seguro medico', 'adeslas', 'sanitas', 'asisa', 'dkv'],
        7: ['luz', 'agua', 'gas', 'internet', 'telefono', 'movil', 'movistar', 'vodafone', 'orange'],
        8: ['ordenador', 'portatil', 'movil', 'tablet', 'monitor', 'teclado', 'raton', 'software'],
        9: ['curso', 'formacion', 'libro', 'conferencia', 'seminario', 'taller'],
        10: []  # Others (default)
    }
    
    # Check if description contains any of the keywords
    for category_id, keywords in category_mappings.items():
        for keyword in keywords:
            if keyword in desc_lower:
                return category_id
    
    # If no match found, return None
    return None

def categorize_income(description):
    """
    Categorize an income based on its description.
    
    Args:
        description: The income description
        
    Returns:
        int: Source ID or None if no match
    """
    # Convert description to lowercase for case-insensitive matching
    desc_lower = description.lower()
    
    # Define source mappings (description keywords -> source ID)
    source_mappings = {
        1: ['factura', 'pago', 'cliente', 'servicio', 'honorarios', 'consulting'],
        2: ['devolucion', 'hacienda', 'agencia tributaria', 'aeat', 'reembolso'],
        3: ['subvencion', 'ayuda', 'beca', 'grant'],
        4: []  # Others (default)
    }
    
    # Check if description contains any of the keywords
    for source_id, keywords in source_mappings.items():
        for keyword in keywords:
            if keyword in desc_lower:
                return source_id
    
    # If no match found, return None
    return None

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
