"""
Models package for the Invoice Generator application.
This module exports all database functions for easy access.
"""

# Import database initialization
from src.models.db import init_db

# Import client functions
from src.models.clients import (
    get_clients,
    get_client,
    add_client,
    update_client,
    delete_client
)

# Import service functions
from src.models.services import (
    get_services,
    get_service,
    add_service,
    update_service,
    delete_service
)

# Import invoice functions
from src.models.invoices import (
    generate_invoice_number,
    save_invoice,
    get_recent_invoices,
    get_invoice_by_number,
    delete_invoice,
    get_invoices_by_year,
    get_available_invoice_years
)

# Import statistics functions
from src.models.stats import (
    get_invoice_stats_by_month,
    get_revenue_stats_by_month,
    get_invoice_stats_by_client,
    get_monthly_invoice_stats_by_client
)

# Export all functions
__all__ = [
    'init_db',
    'get_clients',
    'get_client',
    'add_client',
    'update_client',
    'delete_client',
    'get_services',
    'get_service',
    'add_service',
    'update_service',
    'delete_service',
    'generate_invoice_number',
    'save_invoice',
    'get_recent_invoices',
    'get_invoice_by_number',
    'delete_invoice',
    'get_invoices_by_year',
    'get_available_invoice_years',
    'get_invoice_stats_by_month',
    'get_revenue_stats_by_month',
    'get_invoice_stats_by_client',
    'get_monthly_invoice_stats_by_client'
]
