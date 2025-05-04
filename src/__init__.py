"""
Invoice Generator Application
A simple Flask application for generating invoices.
"""
from flask import Flask

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    
    # Import routes after app is created to avoid circular imports
    from src import routes
    
    # Register routes
    routes.register_routes(app)
    
    return app
