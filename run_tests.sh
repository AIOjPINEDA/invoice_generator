#!/bin/bash

# Invoice Generator Test Runner
# This script runs all tests for the Invoice Generator application

echo "=== Invoice Generator Test Suite ==="
echo ""

# Activate conda environment
echo "Activating conda environment..."
source ~/miniconda3/etc/profile.d/conda.sh
conda activate invoice_generator

# Check if environment is activated
if [[ "$CONDA_DEFAULT_ENV" != "invoice_generator" ]]; then
    echo "Error: Failed to activate invoice_generator environment"
    exit 1
fi

echo "Environment activated: $CONDA_DEFAULT_ENV"
echo ""

# Run all tests
echo "Running all tests..."
echo "===================="
python -m unittest discover -s tests -v

echo ""
echo "=== Test Summary ==="
echo "All tests completed."
echo ""

# Optional: Run specific test categories
echo "To run specific test categories:"
echo "  Unit tests:        python -m unittest discover -s tests/unit -v"
echo "  Integration tests: python -m unittest discover -s tests/integration -v"
echo "  Functional tests:  python -m unittest discover -s tests/functional -v"
