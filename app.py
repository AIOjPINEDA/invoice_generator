"""
Invoice Generator - A simple Flask application for generating invoices.

This is the main entry point for the application.
"""
from src import create_app, models

# Initialize database
models.init_db()

# Create Flask application
app = create_app()

if __name__ == '__main__':
    # Start with a specific port (8888) to avoid common ports that might be in use
    port = 8888
    
    print(f"Starting server on http://localhost:{port}")
    try:
        app.run(debug=True, host='0.0.0.0', port=port)
    except OSError as e:
        print(f"Port {port} is in use. Please try a different port or free up this port.")
        print("Error details:", e)
