"""
Route modules for the Flask application.
"""
from .vehicular import vehicular_routes
from .health import health_routes

__all__ = ['vehicular_routes', 'health_routes']