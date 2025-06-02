# Invoice Generator Tests

This directory contains comprehensive test modules for the Invoice Generator application.

## Quick Start

```bash
# Run all tests
./run_tests.sh

# Run specific test categories
python -m unittest discover -s tests/unit -v        # Unit tests
python -m unittest discover -s tests/integration -v # Integration tests
python -m unittest discover -s tests/functional -v  # Functional tests
```

## Current Test Structure

```
tests/
├── README.md                    # This file
├── TESTING_GUIDE.md            # Detailed testing guide
├── run_tests.sh                # Test runner script
├── conftest.py                 # Shared test configuration
├── test_base.py                # Base test class with utilities
├── unit/                       # Unit tests (10 tests ✅)
│   ├── test_calculations.py    # Financial calculation tests
│   └── test_models.py          # Database model tests
├── integration/                # Integration tests (3 tests ✅)
│   └── test_invoice_flow.py    # Invoice workflow tests
└── functional/                 # Functional tests (ready for expansion)
```

## Test Categories

### Unit Tests (`unit/`) - 10 tests ✅
- Financial calculation functions
- Database model operations
- Individual component testing

### Integration Tests (`integration/`) - 3 tests ✅
- Complete invoice workflow
- Database persistence verification
- Component interaction testing

### Functional Tests (`functional/`) - Ready for expansion
- Flask route testing (future)
- User scenario testing (future)
- API endpoint testing (future)

## Test Standards

- **Isolation**: Each test uses its own temporary database
- **Independence**: Tests can run in any order
- **Documentation**: All tests have clear docstrings
- **Verification**: All tests verified to work before inclusion

## Adding New Tests

1. **Choose test category** (unit/integration/functional)
2. **Create test file** following naming convention
3. **Inherit from TestBase** for common utilities
4. **Follow AAA pattern** (Arrange, Act, Assert)
5. **Run and verify** before committing

See `TESTING_GUIDE.md` for detailed instructions and examples.

## Requirements

- Python 3.12+
- conda environment: `invoice_generator`
- All dependencies automatically handled by test framework
