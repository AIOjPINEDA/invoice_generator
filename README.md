# Invoice Generator 2025

A minimalist Flask application for generating invoices with automatic tax calculations and data visualization.

## Features

- Clean, minimalist responsive interface
- Client and service management
- Custom invoice date selection
- Multi-currency support (USD, EUR, GBP)
- Automatic tax calculations (VAT 21% and IRPF 15%)
- Previous month invoice numbering
- Recent invoices with view and delete options
- Dashboard with interactive charts
- Client and service management

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd invoice_generator
   ```

2. Install Flask:
   ```bash
   pip install flask
   ```

3. Run the application:
   ```bash
   ./run.sh
   ```

## Running the Application

The `run.sh` script provides a simple way to start the application:

```bash
# Default usage (port 8888)
./run.sh

# Custom port
./run.sh 9000

# Show help
./run.sh --help
```

The browser will open automatically when the application starts.

## Configuration

Edit `config.json` to customize:

- Issuer details (name, tax ID, address)
- Bank information

## Client and Service Management

The application provides a complete management interface for clients and services:

### Clients
- Add, edit, and delete clients
- Support for multiple currencies (EUR, USD, GBP)
- Store client details (name, tax ID, address, email)

### Services
- Add, edit, and delete services
- Customizable unit prices and types (hour, day, month, project)

The application automatically handles currency conversion for reporting.

## Invoice Numbering

Invoices use the format `YYMM-XXX-N`:
- `YYMM`: Year and month (previous month)
- `XXX`: Client initials
- `N`: Sequential number

## Dashboard

The application includes a comprehensive dashboard with:
- Monthly invoices by client (stacked bar chart)
- Client distribution (donut chart)
- Monthly revenue (area chart)
- Summary statistics

## License

This project is for personal use.
