# Invoice Generator 2025

A minimalist Flask application for generating invoices and estimates with automatic tax calculations.

## Features

- Clean, minimalist responsive interface
- Client and service management
- Invoice and Estimate generation
- Custom document date selection
- Multi-currency support (USD, EUR, GBP)
- Automatic tax calculations (VAT 21% and IRPF 15%)
- Configurable invoice numbering (previous month or current month)
- Recent documents list with view and delete options
- Dashboard with interactive charts for invoice data

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url> # Replace <repository-url> with your actual repo URL
    cd invoice_generator
    ```

2.  **Set up the Conda environment:**
    The `environment.yml` file specifies all dependencies.
    ```bash
    # Create the conda environment from the YAML file
    conda env create -f environment.yml

    # Activate the newly created environment
    conda activate invoice_generator
    ```
    *Note: If you prefer using Mamba (a faster Conda alternative), you can use `mamba env create -f environment.yml`.*

3.  **Initialize the database:**
    The first time you run the application, or if the database file (`invoices.db`) is missing, it will be automatically created with a basic schema and sample data.

4.  **Run the application:**
    ```bash
    ./run.sh
    ```
    The application will be accessible at `http://localhost:8888` by default.

## Running the Application

The `run.sh` script starts the Flask development server.

```bash
# Default usage (starts on port 8888)
./run.sh

# Specify a custom port
./run.sh 9000

# Start without automatically opening the browser
./run.sh --no-browser

# Display help for the run script
./run.sh --help
```

Ensure the `invoice_generator` Conda environment is active before running the script.

## Configuration

Edit `config.json` in the root directory to customize:
- **Issuer Details**: Your company/freelancer name, tax ID, address, contact information.
- **Bank Information**: IBAN and bank name for including in invoices.
- **Currency Settings**: Default currency symbol.
- **Invoice Numbering**: `invoice_number_use_previous_month` (true/false).
- **Tax Rates**: Default VAT and IRPF percentages (though these can often be toggled per invoice).

## Client and Service Management

Manage your clients and services through the dedicated sections in the web interface:

### Clients
- Add, edit, and delete clients.
- Store client details: name, tax ID, address, country, email.
- Assign a default currency (EUR, USD, GBP) to each client.

### Services
- Add, edit, and delete services.
- Define service descriptions, unit prices, and unit types (e.g., hour, day, project).

## Document Numbering

### Invoices
- Default format: `YYMM-XXX-N`
    - `YYMM`: Year and month (configurable to be the previous month or current month via `config.json`).
    - `XXX`: Client initials (derived from client name).
    - `N`: A sequential number for that client and month/year.

### Estimates (Presupuestos)
- *(This section will be updated once estimate numbering is finalized)*

## Dashboard

The dashboard provides an overview of your invoicing activity with charts for:
- Monthly invoice counts.
- Monthly revenue.
- Invoice distribution by client.
- *(More charts can be added as new features are developed)*.

## License

This project is for personal use.
