"""
Route definitions for the expenses and income tracking module.
"""
import os
from flask import render_template, request, redirect, flash
from datetime import datetime
from src.finance import expenses

def register_expense_routes(app):
    """Register all expense and income routes"""

    @app.route('/expenses')
    def expenses_page():
        """Expenses page with list of expenses"""
        # Get expense categories
        categories = expenses.get_expense_categories()

        # Get recent expenses
        recent_expenses = expenses.get_expenses(10)

        # Get current year
        current_year = datetime.now().year

        # Get expense stats by category for the current year
        expense_stats = expenses.get_expenses_by_category(current_year)

        # Get current page for navbar highlighting
        current_page = 'expenses'

        return render_template('finance/expenses.html',
                              categories=categories,
                              recent_expenses=recent_expenses,
                              expense_stats=expense_stats,
                              current_year=current_year,
                              current_page=current_page)

    @app.route('/add_expense', methods=['POST'])
    def add_expense():
        """Add a new expense"""
        category_id = request.form.get('category_id')
        description = request.form.get('description')
        amount = request.form.get('amount')
        date = request.form.get('date')
        payment_method = request.form.get('payment_method')
        notes = request.form.get('notes')
        tax_deductible = 'tax_deductible' in request.form

        # Validate inputs
        if not all([category_id, description, amount, date]):
            flash('Please fill in all required fields', 'error')
            return redirect('/expenses')

        try:
            # Convert amount to float
            amount = float(amount)

            # Add expense to database
            expenses.add_expense(
                category_id=category_id,
                description=description,
                amount=amount,
                date=date,
                payment_method=payment_method,
                notes=notes,
                tax_deductible=tax_deductible
            )

            flash('Expense added successfully', 'success')
        except Exception as e:
            flash(f'Error adding expense: {str(e)}', 'error')

        return redirect('/expenses')

    @app.route('/incomes')
    def incomes_page():
        """Incomes page with list of incomes"""
        # Get income sources
        sources = expenses.get_income_sources()

        # Get recent incomes
        recent_incomes = expenses.get_incomes(10)

        # Get current year
        current_year = datetime.now().year

        # Get current page for navbar highlighting
        current_page = 'incomes'

        return render_template('finance/incomes.html',
                              sources=sources,
                              recent_incomes=recent_incomes,
                              current_year=current_year,
                              current_page=current_page)

    @app.route('/add_income', methods=['POST'])
    def add_income():
        """Add a new income"""
        source_id = request.form.get('source_id')
        description = request.form.get('description')
        amount = request.form.get('amount')
        date = request.form.get('date')
        notes = request.form.get('notes')

        # Validate inputs
        if not all([source_id, description, amount, date]):
            flash('Please fill in all required fields', 'error')
            return redirect('/incomes')

        try:
            # Convert amount to float
            amount = float(amount)

            # Add income to database
            expenses.add_income(
                source_id=source_id,
                description=description,
                amount=amount,
                date=date,
                notes=notes
            )

            flash('Income added successfully', 'success')
        except Exception as e:
            flash(f'Error adding income: {str(e)}', 'error')

        return redirect('/incomes')

    @app.route('/financial_summary')
    def financial_summary():
        """Financial summary page"""
        # Get year parameter, default to current year
        selected_year = request.args.get('year', datetime.now().year)

        # Get financial summary for the selected year
        summary = expenses.get_financial_summary(selected_year)

        # Get expense stats by category for the selected year
        expense_stats = expenses.get_expenses_by_category(selected_year)

        # Get tax deductible expenses for the selected year
        tax_deductible = expenses.get_tax_deductible_expenses(selected_year)

        # Get current page for navbar highlighting
        current_page = 'financial_summary'

        return render_template('finance/financial_summary.html',
                              summary=summary,
                              expense_stats=expense_stats,
                              tax_deductible=tax_deductible,
                              selected_year=selected_year,
                              current_page=current_page)

    @app.route('/import_expenses', methods=['GET', 'POST'])
    def import_expenses():
        """Import expenses from bank statement"""
        if request.method == 'POST':
            # Check if file was uploaded
            if 'file' not in request.files:
                flash('No file part', 'error')
                return redirect('/expenses')

            file = request.files['file']

            # Check if file is empty
            if file.filename == '':
                flash('No selected file', 'error')
                return redirect('/expenses')

            # Check if file is an Excel file
            if not file.filename.endswith(('.xlsx', '.xls')):
                flash('File must be an Excel file (.xlsx or .xls)', 'error')
                return redirect('/expenses')

            try:
                # Save file temporarily
                temp_path = 'temp_bank_statement.xlsx'
                file.save(temp_path)

                # Get default category and source
                default_category = request.form.get('default_category')
                default_source = request.form.get('default_source')

                # Import expenses from file
                from src.finance.bbva_import import import_bbva_statement
                result = import_bbva_statement(
                    temp_path,
                    default_expense_category=default_category,
                    default_income_source=default_source,
                    check_duplicates=True
                )

                # Remove temporary file
                os.remove(temp_path)

                if result['success']:
                    # Check if there are duplicates
                    if 'duplicates' in result and result['duplicates']:
                        duplicate_count = len(result['duplicates'])
                        flash(f"Successfully imported {result['expenses_imported']} expenses and {result['incomes_imported']} incomes. Found {duplicate_count} potential duplicates.", 'warning')
                    else:
                        flash(f"Successfully imported {result['expenses_imported']} expenses and {result['incomes_imported']} incomes", 'success')
                else:
                    flash(f"Error importing data: {result['message']}", 'error')
            except Exception as e:
                flash(f'Error importing data: {str(e)}', 'error')

            return redirect('/expenses')

        # GET request - show import form
        return render_template('finance/import_expenses.html',
                              current_page='expenses')
