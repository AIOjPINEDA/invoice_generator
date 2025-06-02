"""
Shared test configuration and fixtures for Invoice Generator tests.
"""
from datetime import datetime, timedelta


# Test data fixtures
TEST_CLIENTS = [
    {
        'name': 'Test Client LLC',
        'tax_id': 'TC001',
        'address': '123 Test Street',
        'country': 'Spain',
        'email': 'test@client.com',
        'currency_code': 'EUR',
        'currency_symbol': '€'
    }
]

TEST_SERVICES = [
    {
        'description': 'Test Service',
        'unit_price': 100.0,
        'unit_type': 'hour'
    }
]

def get_test_date(days_offset=0):
    """Get a test date with optional offset from today."""
    return (datetime.now() + timedelta(days=days_offset)).strftime('%Y-%m-%d')
