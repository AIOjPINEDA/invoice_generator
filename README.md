# Invoice Generator 2025

A minimalist Flask application for generating invoices with automatic tax calculations, expense tracking, and data visualization.

## Features

- Clean, minimalist responsive interface
- Client and service management
- Custom invoice date selection
- Multi-currency support (USD, EUR, GBP)
- Automatic tax calculations (VAT 21% and IRPF 15%)
- Previous month invoice numbering
- Recent invoices with view and delete options
- Dashboard with interactive charts
- Expense and income tracking
- BBVA bank statement import
- Financial summary and tax reports

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd invoice_generator
   ```

2. Set up the conda environment:
   ```bash
   # Run the setup script to create the conda environment
   ./setup_conda.sh
   ```
   This script will create a conda environment named `invoice_generator` with all the required dependencies.

   Alternatively, you can create the environment manually:
   ```bash
   # Using conda
   conda env create -f environment.yml

   # Or using mamba (faster)
   mamba env create -f environment.yml

   # Activate the environment
   conda activate invoice_generator
   ```

4. Run the application:
   ```bash
   ./run.sh
   ```

## Running the Application

The `run.sh` script provides a simple way to start the application. It will automatically activate the conda environment if it exists:

```bash
# Default usage (port 8888)
./run.sh

# Custom port
./run.sh 9000

# Don't open browser automatically
./run.sh --no-browser

# Show help
./run.sh --help
```

The browser will open automatically when the application starts (unless you use the --no-browser option).

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

## Expense and Income Tracking

The application includes a complete expense and income tracking system:

### Expenses
- Add, edit, and delete expenses
- Categorize expenses
- Mark expenses as tax deductible
- Import expenses from BBVA bank statements

### Incomes
- Add, edit, and delete incomes
- Categorize incomes
- Track non-invoice income

### Financial Summary
- Monthly and yearly financial overview
- Tax deductible expenses summary
- Profit/loss calculation
- Tax report generation

## Project Structure

```
invoice_generator/
├── app.py                  # Main entry point
├── run.sh                  # Execution script
├── setup_conda.sh          # Conda environment setup
├── clean_conda.sh          # Conda environment cleanup
├── config.json             # Configuration
├── environment.yml         # Conda dependencies
├── src/                    # Source code
│   ├── invoice/            # Invoice module
│   ├── client/             # Client module
│   ├── service/            # Service module
│   └── finance/            # Finance module
├── static/                 # Static files
│   ├── css/                # Stylesheets
│   ├── js/                 # JavaScript
│   └── img/                # Images
├── templates/              # HTML templates
│   ├── invoice/            # Invoice templates
│   ├── client/             # Client templates
│   ├── service/            # Service templates
│   └── finance/            # Finance templates
├── scripts/                # Utility scripts
└── data/                   # Data files
```

## License

This project is for personal use.
