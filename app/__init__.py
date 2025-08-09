"""
Flask application factory and configuration.
"""
import os
from flask import Flask
from .routes import vehicular_routes, health_routes
from .error_handlers import register_error_handlers


def create_app(config=None):
    """
    Application factory for creating Flask app instances.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    if config:
        app.config.update(config)
    else:
        from .config import Config
        app.config.from_object(Config)
    
    # Register blueprints
    app.register_blueprint(vehicular_routes)
    app.register_blueprint(health_routes)
    
    # Register error handlers
    register_error_handlers(app)
    
    return app