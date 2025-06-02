#!/usr/bin/env python3
"""
Initialize the database for the Invoice Generator application.
This script creates all tables including the estimates table that was missing.
"""
import os
import sys

# Add the parent directory to sys.path to allow importing from src
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the init_db function from the db module
from src.models.db import init_db

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Database initialization complete. The estimates table has been added.")

