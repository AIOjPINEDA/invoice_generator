# Invoice Generator Testing Guide

## Quick Start

To run all tests:
```bash
./run_tests.sh
```

## Current Test Coverage

### ✅ Unit Tests (`tests/unit/`)
- **test_calculations.py** - Financial calculation functions
  - Basic IVA/IRPF calculations
  - Tax combinations (with/without IVA, with/without IRPF)
  - Edge cases and validation

- **test_models.py** - Database models and operations
  - Client creation and retrieval
  - Service creation and retrieval
  - Database table structure validation
  - Column existence verification

### ✅ Integration Tests (`tests/integration/`)
- **test_invoice_flow.py** - Complete invoice workflow
  - Invoice creation with calculations
  - Tax application scenarios
  - Database persistence verification

### 📝 Functional Tests (`tests/functional/`)
- *Ready for future Flask route testing*

## Test Standards Implemented

### ✅ Structure
- Organized by test type (unit/integration/functional)
- Base test class with common utilities
- Isolated test databases for each test
- Proper setup/teardown for clean tests

### ✅ Best Practices
- AAA pattern (Arrange, Act, Assert)
- Descriptive test names and docstrings
- Independent test execution
- Comprehensive assertions

### ✅ Utilities
- `TestBase` class with common functionality
- `DatabaseTestMixin` for database testing
- Test data fixtures in `conftest.py`
- Automatic test database cleanup

## Adding New Tests

### 1. Choose Test Category
- **Unit**: Testing individual functions
- **Integration**: Testing component interactions
- **Functional**: Testing user-facing features

### 2. Create Test File
```python
# tests/unit/test_new_feature.py
import unittest
from tests.test_base import TestBase

class NewFeatureTests(TestBase):
    """Tests for new feature functionality."""
    
    def test_specific_behavior(self):
        """Test specific behavior description."""
        # Arrange
        # Act
        # Assert
        pass
```

### 3. Run and Verify
```bash
# Test your new file
python -m unittest tests.unit.test_new_feature -v

# Run all tests to ensure no regressions
./run_tests.sh
```

## Test Results Summary

**Total Tests: 15**
- Unit Tests: 12 ✅
- Integration Tests: 3 ✅
- Functional Tests: 0 (ready for expansion)

**All tests passing** ✅

## Next Steps for Test Expansion

1. **Flask Route Testing** - Add functional tests for web endpoints
2. **Estimate Flow Testing** - Add integration tests for estimate workflow
3. **Error Handling Tests** - Add tests for edge cases and error scenarios
4. **Performance Tests** - Add tests for large data sets
5. **API Testing** - Add tests for any API endpoints

## Maintenance

- Tests are automatically isolated with temporary databases
- No manual cleanup required
- Tests can be run independently or as a suite
- All tests verified to work before inclusion in repository
