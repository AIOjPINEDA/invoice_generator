"""
Route definitions for the Invoice Generator application.
"""
from flask import render_template, request, jsonify, redirect, flash, url_for
from datetime import datetime
from src import models
from src import utils
from src.finance import finance_routes
from src.models import estimates as estimate_models # Added import for estimates

def register_routes(app):
    """Register all application routes"""

    # Register finance routes
    finance_routes.register_expense_routes(app)

    @app.route('/')
    def index():
        """Main page with the invoice generation form"""
        clients = models.get_clients()
        services = models.get_services()
        config = utils.load_config()

        # Get last selections from config
        last_client_id = config.get('preferences', {}).get('last_client_id')
        last_service_id = config.get('preferences', {}).get('last_service_id')

        # Get recent invoices (now includes currency_symbol at index 10)
        recent_invoices = models.get_recent_invoices(5) # Limit to 5 for main page
        recent_estimates = estimate_models.get_recent_estimates(5) # Limit to 5 for main page

        # Get current page for navbar highlighting
        current_page = 'home'

        # Get today's date in YYYY-MM-DD format for the date input
        today_date = datetime.now().strftime('%Y-%m-%d')

        return render_template('index.html',
                              clients=clients,
                              services=services,
                              last_client_id=last_client_id,
                              last_service_id=last_service_id,
                              recent_invoices=recent_invoices,
                              recent_estimates=recent_estimates, # Pass recent estimates
                              currency_symbol=config.get('currency', {}).get('symbol', '€'),
                              current_page=current_page,
                              today_date=today_date)

    @app.route('/get_client/<int:client_id>')
    def get_client(client_id):
        """API endpoint to get client details"""
        client = models.get_client(client_id)
        if client:
            # Check if client has currency information
            currency_code = client[6] if len(client) > 6 and client[6] else 'EUR'
            currency_symbol = client[7] if len(client) > 7 and client[7] else '€'

            data = {
                'id': client[0],
                'name': client[1],
                'tax_id': client[2],
                'address': client[3],
                'country': client[4],
                'email': client[5],
                'currency_code': currency_code,
                'currency_symbol': currency_symbol
            }
            return jsonify(data)
        return jsonify({'error': 'Client not found'}), 404

    @app.route('/get_service/<int:service_id>')
    def get_service(service_id):
        """API endpoint to get service details"""
        service = models.get_service(service_id)
        if service:
            data = {
                'id': service[0],
                'description': service[1],
                'unit_price': service[2],
                'unit_type': service[3]
            }
            return jsonify(data)
        return jsonify({'error': 'Service not found'}), 404

    @app.route('/generate_invoice', methods=['POST'])
    def generate_invoice():
        """Generate invoice based on form data"""
        client_id = request.form.get('client_id')
        service_id = request.form.get('service_id')
        quantity = request.form.get('quantity', 1)
        apply_iva = request.form.get('apply_iva') == '1'  # Checkbox for IVA
        apply_irpf = request.form.get('apply_irpf') == '1'  # Checkbox for IRPF

        # Get invoice date from form or use today's date
        invoice_date = request.form.get('invoice_date')
        if invoice_date:
            # Convert from YYYY-MM-DD to DD/MM/YYYY
            date_obj = datetime.strptime(invoice_date, '%Y-%m-%d')
            formatted_date = date_obj.strftime('%d/%m/%Y')
        else:
            formatted_date = datetime.now().strftime('%d/%m/%Y')

        client = models.get_client(int(client_id))
        service = models.get_service(int(service_id))

        # Get currency from client if available, otherwise use default from config
        config = utils.load_config()
        if len(client) > 6 and client[6]:  # Client has currency_code
            currency_code = client[6]
            currency_symbol = client[7] if len(client) > 7 and client[7] else '$' if currency_code == 'USD' else '€'
        else:
            currency_code = config.get('currency', {}).get('code', 'EUR')
            currency_symbol = config.get('currency', {}).get('symbol', '€')

        # Save last selections to config
        config['preferences']['last_client_id'] = int(client_id)
        config['preferences']['last_service_id'] = int(service_id)
        utils.save_config(config)

        invoice_number = models.generate_invoice_number(int(client_id))

        # Calculate totals
        totals = utils.calculate_invoice_totals(
            service[2],
            int(quantity),
            apply_iva,
            apply_irpf
        )

        # Save the invoice to database with tax preferences
        models.save_invoice(
            int(client_id),
            int(service_id),
            int(quantity),
            formatted_date,
            invoice_number,
            apply_iva,
            apply_irpf
        )

        # Get issuer data from config
        issuer = config.get('issuer', {})

        return render_template('invoice.html',
                               client=client,
                               service=service,
                               quantity=quantity,
                               date=formatted_date,
                               invoice_number=invoice_number,
                               subtotal=totals.get('subtotal', 0),
                               iva=totals.get('iva_amount', 0),
                               irpf=totals.get('irpf_amount', 0),
                               total=totals.get('total', 0),
                               currency_code=currency_code,
                               currency_symbol=currency_symbol,
                               issuer=issuer)

    @app.route('/generate_estimate', methods=['POST'])
    def generate_estimate():
        """Generate estimate based on form data"""
        client_id = request.form.get('client_id')
        service_id = request.form.get('service_id')
        quantity = request.form.get('quantity', 1)
        
        estimate_date_str = request.form.get('issue_date')
        valid_until_date_str = request.form.get('valid_until_date')
        
        # IRPF rate is expected as a string like "0.07", convert to float
        irpf_rate_str = request.form.get('irpf_rate')
        try:
            irpf_rate = float(irpf_rate_str) if irpf_rate_str else 0.0
        except ValueError:
            flash('Invalid IRPF rate format.', 'error')
            return redirect(request.referrer or '/')

        notes = request.form.get('notes', '')
        terms = request.form.get('terms', '')

        if not client_id or not service_id or not quantity or not estimate_date_str:
            flash('Missing required fields for estimate generation.', 'error')
            return redirect(request.referrer or '/')

        try:
            quantity = int(quantity)
        except ValueError:
            flash('Invalid quantity.', 'error')
            return redirect(request.referrer or '/')

        client = models.get_client(int(client_id))
        service = models.get_service(int(service_id))

        if not client or not service:
            flash('Invalid client or service selected.', 'error')
            return redirect(request.referrer or '/')

        config = utils.load_config()
        # Save last selections to config
        if 'preferences' not in config:
            config['preferences'] = {}
        config['preferences']['last_client_id'] = int(client_id)
        config['preferences']['last_service_id'] = int(service_id)
        utils.save_config(config)

        # Generate estimate number with proper date object
        issue_date_obj = datetime.strptime(estimate_date_str, '%Y-%m-%d')
        estimate_number = estimate_models.generate_estimate_number(issue_date_obj)

        # save_estimate handles financial calculations internally
        estimate_id = estimate_models.save_estimate(
            client_id=int(client_id),
            service_id=int(service_id),
            quantity=quantity,
            issue_date_str=estimate_date_str,  # Corrected parameter name
            valid_until_date_str=valid_until_date_str,
            irpf_rate_decimal=irpf_rate,  # Corrected parameter name
            notes=notes,
            terms=terms,
            estimate_number_override=estimate_number # Pass the generated number
        )

        if not estimate_id:
            flash('Failed to save estimate.', 'error')
            return redirect(request.referrer or '/')

        # Fetch the full estimate details to render the page
        # This ensures all calculated fields are fresh from the DB
        estimate_data = estimate_models.get_estimate_by_number(estimate_number)
        if not estimate_data:
            flash('Failed to retrieve estimate after saving.', 'error')
            return redirect(request.referrer or '/')
            
        issuer = config.get('issuer', {})
        
        # Determine currency symbol from client or default
        currency_symbol = client[7] if client and len(client) > 7 and client[7] else config.get('currency', {}).get('symbol', '€')


        # The 'estimate_detail.html' template will be created in the next step
        return render_template('estimate_detail.html', 
                               estimate_data=estimate_data,
                               client=models.get_client(estimate_data['client_id']), # Fetch full client for template
                               service=models.get_service(estimate_data['service_id']), # Fetch full service for template
                               issuer=issuer,
                               currency_symbol=currency_symbol,
                               current_page='estimates') # For navbar highlighting

    @app.route('/view_invoice/<invoice_number>')
    def view_invoice(invoice_number):
        """View a specific invoice by its number"""
        invoice_data = models.get_invoice_by_number(invoice_number)

        if not invoice_data:
            return "Invoice not found", 404

        # Get client data
        client = invoice_data['client']

        # Get currency from client if available, otherwise use default from config
        config = utils.load_config()
        if client and len(client) > 6 and client[6]:  # Client has currency_code
            currency_code = client[6]
            currency_symbol = client[7] if len(client) > 7 and client[7] else '$' if currency_code == 'USD' else '€'
        else:
            currency_code = config.get('currency', {}).get('code', 'EUR')
            currency_symbol = config.get('currency', {}).get('symbol', '€')

        # Get issuer data from config
        issuer = config.get('issuer', {})

        # Calculate totals
        service = invoice_data['service']
        quantity = invoice_data['quantity']

        # Make sure we're using the correct price from the service
        if service and len(service) > 2:
            unit_price = service[2]
            totals = utils.calculate_invoice_totals(
                unit_price,
                quantity,
                invoice_data['apply_iva'],
                invoice_data['apply_irpf']
            )
        else:
            # Fallback if service data is incomplete
            totals = {
                'subtotal': 0,
                'iva': 0,
                'irpf': 0,
                'total': 0
            }

        return render_template('invoice.html',
                              client=client,
                              service=service,
                              quantity=quantity,
                              date=invoice_data['date'],
                              invoice_number=invoice_data['invoice_number'],
                              subtotal=totals.get('subtotal', 0),
                              iva=totals.get('iva_amount', 0),
                              irpf=totals.get('irpf_amount', 0),
                              total=totals.get('total', 0),
                              currency_code=currency_code,
                              currency_symbol=currency_symbol,
                              issuer=issuer)

    @app.route('/estimate/<estimate_number>')
    def view_estimate(estimate_number):
        """View a specific estimate by its number"""
        estimate_data = estimate_models.get_estimate_by_number(estimate_number)

        if not estimate_data:
            flash(f"Estimate {estimate_number} not found.", "error")
            return redirect(url_for('index')) # Or a dedicated estimates list page

        client = models.get_client(estimate_data['client_id'])
        service = models.get_service(estimate_data['service_id'])
        
        config = utils.load_config()
        issuer = config.get('issuer', {})
        
        # Determine currency symbol from client or default
        currency_symbol = client[7] if client and len(client) > 7 and client[7] else config.get('currency', {}).get('symbol', '€')

        # 'estimate_detail.html' will be used here as well
        return render_template('estimate_detail.html',
                               estimate_data=estimate_data,
                               client=client,
                               service=service,
                               issuer=issuer,
                               currency_symbol=currency_symbol,
                               current_page='estimates')


    @app.route('/estimates')
    def list_estimates():
        """List all estimates"""
        # For now, using get_recent_estimates. Later, a dedicated get_all_estimates might be needed.
        estimates_list = estimate_models.get_recent_estimates(limit=100) # Get up to 100 recent estimates
        config = utils.load_config()
        default_currency_symbol = config.get('currency', {}).get('symbol', '€')
        
        # 'all_estimates.html' will be created in a future step
        return render_template('all_estimates.html', 
                               estimates=estimates_list, 
                               default_currency_symbol=default_currency_symbol,
                               current_page='estimates')

    @app.route('/delete_invoice/<invoice_number>')
    def delete_invoice(invoice_number):
        """Delete a specific invoice by its number"""
        success = models.delete_invoice(invoice_number)

        if success:
            return redirect('/')
        else:
            return "Error deleting invoice", 400

    @app.route('/delete_estimate/<estimate_number>')
    def delete_estimate(estimate_number):
        """Delete a specific estimate by its number"""
        success = estimate_models.delete_estimate(estimate_number)

        if success:
            flash(f'Estimate {estimate_number} deleted successfully.', 'success')
        else:
            flash(f'Error deleting estimate {estimate_number}.', 'error')
        
        # Redirect to the main page or a dedicated estimates list page
        return redirect(request.referrer or url_for('index'))

    # API routes for charts
    @app.route('/api/invoice_stats')
    def api_invoice_stats():
        """Get invoice statistics for charts"""
        # Get year parameter, default to current year
        year = request.args.get('year', datetime.now().year)

        # Get invoice counts by month for the selected year
        stats = models.get_invoice_stats_by_month(year)

        # Format data for ApexCharts
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        counts = [0] * 12  # Initialize with zeros

        # Fill in actual counts
        for month, count in stats:
            if 1 <= month <= 12:
                counts[month-1] = count

        return jsonify({
            'months': months,
            'counts': counts,
            'year': year
        })

    @app.route('/api/revenue_stats')
    def api_revenue_stats():
        """Get revenue statistics for charts"""
        # Get year parameter, default to current year
        year = request.args.get('year', datetime.now().year)

        # Get revenue by month for the selected year
        stats = models.get_revenue_stats_by_month(year)

        # Format data for ApexCharts
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        amounts = [0] * 12  # Initialize with zeros

        # Default currency
        currency = '€'

        # Fill in actual amounts
        for month, amount, curr in stats:
            if 1 <= month <= 12:
                amounts[month-1] = amount
                currency = curr or currency

        return jsonify({
            'months': months,
            'amounts': amounts,
            'currency': currency,
            'year': year
        })

    @app.route('/api/client_stats')
    def api_client_stats():
        """Get client distribution statistics for charts"""
        # Get year parameter, default to current year
        year = request.args.get('year', datetime.now().year)

        # Get invoice counts by client for the selected year
        stats = models.get_invoice_stats_by_client(year)

        # Format data for ApexCharts
        labels = []
        values = []

        # Calculate percentages
        total = sum(count for _, count in stats)

        if total > 0:
            # Add top clients (up to 4)
            for client_name, count in stats[:4]:
                labels.append(client_name)
                values.append(round((count / total) * 100))

            # Group remaining clients as "Others" if there are more than 4
            if len(stats) > 4:
                others_count = sum(count for _, count in stats[4:])
                labels.append('Others')
                values.append(round((others_count / total) * 100))
        else:
            # Sample data if no invoices
            labels = ['No Data']
            values = [100]

        return jsonify({
            'labels': labels,
            'values': values,
            'year': year
        })

    @app.route('/api/client_monthly_stats')
    def api_client_monthly_stats():
        """Get combined client and monthly statistics for charts"""
        # Get year parameter, default to current year
        year = request.args.get('year', datetime.now().year)

        # Get monthly invoice counts by client for the selected year
        stats = models.get_monthly_invoice_stats_by_client(year)

        # Get all clients for the year
        client_stats = models.get_invoice_stats_by_client(year)

        # Get top clients (up to 5)
        top_clients = [client_name for client_name, _ in client_stats[:5]]

        # If there are more than 5 clients, add "Others"
        if len(client_stats) > 5:
            top_clients.append('Others')

        # Initialize data structure
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        series = []

        # Create a series for each top client
        for client in top_clients:
            client_data = {
                'name': client,
                'data': [0] * 12  # Initialize with zeros for all months
            }
            series.append(client_data)

        # Fill in the data
        for month, client, count in stats:
            if 1 <= month <= 12:
                month_index = month - 1

                # Find the client in our series
                client_index = -1
                for i, client_series in enumerate(series):
                    if client_series['name'] == client:
                        client_index = i
                        break

                # If client is not in top clients, add to "Others"
                if client_index == -1 and 'Others' in top_clients:
                    client_index = top_clients.index('Others')

                # Update the count if we found the client
                if client_index != -1:
                    series[client_index]['data'][month_index] += count

        return jsonify({
            'months': months,
            'series': series,
            'year': year
        })

    @app.route('/dashboard')
    def dashboard():
        """Dashboard page with charts and statistics"""
        # Get year parameter, default to current year
        selected_year = request.args.get('year', datetime.now().year)

        # Get available years from the database
        available_years = models.get_available_invoice_years()
        if not available_years:
            available_years = [datetime.now().year]

        # Get basic statistics
        clients = models.get_clients()

        # Get invoices for the selected year
        year_invoices = models.get_invoices_by_year(selected_year)

        # Calculate total invoices
        total_invoices = len(year_invoices)

        # Calculate total revenue
        total_revenue = 0
        for invoice in year_invoices:
            subtotal = invoice[6]  # subtotal is at index 6
            total_revenue += subtotal

        # Get total clients
        total_clients = len(clients)

        # Get current month name
        current_month = datetime.now().strftime('%B %Y')

        # Get default currency symbol
        config = utils.load_config()
        currency_symbol = config.get('currency', {}).get('symbol', '€')

        # Get current page for navbar highlighting
        current_page = 'dashboard'

        return render_template('dashboard.html',
                              total_invoices=total_invoices,
                              total_revenue=total_revenue,
                              total_clients=total_clients,
                              current_month=current_month,
                              currency_symbol=currency_symbol,
                              available_years=available_years,
                              selected_year=int(selected_year),
                              current_page=current_page)

    @app.route('/all_invoices')
    def all_invoices():
        """Show all invoices with filtering options"""
        # Get year parameter, default to current year
        selected_year = request.args.get('year', datetime.now().year)

        # Get all invoices for the selected year
        all_invoices = models.get_invoices_by_year(selected_year)

        # Get available years from the database
        available_years = models.get_available_invoice_years()
        if not available_years:
            available_years = [datetime.now().year]

        # Calculate statistics
        total_amount = sum(invoice[6] for invoice in all_invoices)
        unique_clients = len(set(invoice[3] for invoice in all_invoices))
        client_names = sorted(set(invoice[3] for invoice in all_invoices))

        # Get default currency symbol
        config = utils.load_config()
        currency_symbol = config.get('currency', {}).get('symbol', '€')

        # Get current page for navbar highlighting
        current_page = 'all_invoices'

        return render_template('all_invoices.html',
                              invoices=all_invoices,
                              total_amount=total_amount,
                              unique_clients=unique_clients,
                              client_names=client_names,
                              available_years=available_years,
                              selected_year=selected_year,
                              currency_symbol=currency_symbol,
                              current_page=current_page)

    @app.route('/manage_clients')
    def manage_clients():
        """Manage clients page"""
        # Get all clients
        clients = models.get_clients()

        # Get current page for navbar highlighting
        current_page = 'manage_clients'

        return render_template('manage_clients.html',
                              clients=clients,
                              current_page=current_page)

    @app.route('/save_client', methods=['POST'])
    def save_client():
        """Save client data (add or update)"""
        client_id = request.form.get('client_id')
        client_name = request.form.get('client_name')
        tax_id = request.form.get('tax_id')
        address = request.form.get('address')
        country = request.form.get('country')
        email = request.form.get('email')
        currency_code = request.form.get('currency_code')

        # Set currency symbol based on currency code
        currency_symbol = '$' if currency_code == 'USD' else '£' if currency_code == 'GBP' else '€'

        if client_id and client_id.isdigit() and int(client_id) > 0:
            # Update existing client
            models.update_client(
                int(client_id),
                client_name,
                tax_id,
                address,
                country,
                email,
                currency_code,
                currency_symbol
            )
        else:
            # Add new client
            models.add_client(
                client_name,
                tax_id,
                address,
                country,
                email,
                currency_code,
                currency_symbol
            )

        return redirect('/manage_clients')

    @app.route('/delete_client', methods=['POST'])
    def delete_client():
        """Delete a client"""
        client_id = request.form.get('delete_id')

        if client_id and client_id.isdigit():
            success = models.delete_client(int(client_id))
            if not success:
                # Client has invoices, cannot delete
                flash("Cannot delete this client because it has invoices associated with it. Delete the invoices first.", "error")

        return redirect('/manage_clients')

    @app.route('/manage_services')
    def manage_services():
        """Manage services page"""
        # Get all services
        services = models.get_services()

        # Get default currency symbol
        config = utils.load_config()
        currency_symbol = config.get('currency', {}).get('symbol', '€')

        # Get current page for navbar highlighting
        current_page = 'manage_services'

        return render_template('manage_services.html',
                              services=services,
                              currency_symbol=currency_symbol,
                              current_page=current_page)

    @app.route('/save_service', methods=['POST'])
    def save_service():
        """Save service data (add or update)"""
        service_id = request.form.get('service_id')
        service_description = request.form.get('service_description')
        unit_price = request.form.get('unit_price')
        unit_type = request.form.get('unit_type')

        if service_id and service_id.isdigit() and int(service_id) > 0:
            # Update existing service
            models.update_service(
                int(service_id),
                service_description,
                float(unit_price),
                unit_type
            )
        else:
            # Add new service
            models.add_service(
                service_description,
                float(unit_price),
                unit_type
            )

        return redirect('/manage_services')

    @app.route('/delete_service', methods=['POST'])
    def delete_service():
        """Delete a service"""
        service_id = request.form.get('delete_id')

        if service_id and service_id.isdigit():
            success = models.delete_service(int(service_id))
            if not success:
                # Service has invoices, cannot delete
                flash("Cannot delete this service because it has invoices associated with it. Delete the invoices first.", "error")

        return redirect('/manage_services')
