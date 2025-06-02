"""
Invoice Generator Application
A simple Flask application for generating invoices.
"""
from flask import Flask

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__, template_folder='../templates', static_folder='../static')

    # Configure Flask application
    app.config['SECRET_KEY'] = 'invoice-generator-secret-key-2025-change-in-production'
    app.config['SESSION_TYPE'] = 'filesystem'

    # Import routes after app is created to avoid circular imports
    from src import routes

    # Register routes
    routes.register_routes(app)

    return app
