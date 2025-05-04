# Invoice Generator Tests

This directory contains test modules for the Invoice Generator application.

## Test Modules

- `test_database.py`: Tests for database structure, schema, and basic database operations
- `test_routes.py`: Tests for Flask routes and API endpoints

## Running Tests

You can run the tests using Python's unittest framework:

```bash
# Run all tests
python -m unittest discover -s tests

# Run a specific test file
python -m unittest tests.test_database
python -m unittest tests.test_routes

# Run a specific test case
python -m unittest tests.test_database.DatabaseTestCase.test_database_exists
```

## Test Requirements

- Python 3.6+
- Flask
- SQLite3

## Adding New Tests

When adding new tests, please follow these guidelines:

1. Create a new test file with the `test_` prefix
2. Use the `unittest` framework for consistency
3. Document your test functions with docstrings
4. Group related tests in test classes that inherit from `unittest.TestCase`
