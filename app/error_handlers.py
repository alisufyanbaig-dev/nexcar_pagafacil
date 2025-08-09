"""
Centralized error handling for the Flask application.
"""
from flask import jsonify
import logging

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    """
    Register error handlers for the Flask application.
    
    Args:
        app: Flask application instance
    """
    
    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request errors."""
        logger.warning(f"Bad request: {error}")
        return jsonify({
            "codigo": "error",
            "info": None,
            "error": {
                "mensaje": "Bad request - invalid parameters"
            }
        }), 400
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found errors."""
        logger.warning(f"Not found: {error}")
        return jsonify({
            "codigo": "error",
            "info": None,
            "error": {
                "mensaje": "Endpoint not found"
            }
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 Method Not Allowed errors."""
        logger.warning(f"Method not allowed: {error}")
        return jsonify({
            "codigo": "error",
            "info": None,
            "error": {
                "mensaje": "Method not allowed"
            }
        }), 405
    
    @app.errorhandler(500)
    def internal_server_error(error):
        """Handle 500 Internal Server Error."""
        logger.error(f"Internal server error: {error}", exc_info=True)
        return jsonify({
            "codigo": "error",
            "info": None,
            "error": {
                "mensaje": "Internal server error"
            }
        }), 500
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """Handle any unexpected errors."""
        logger.error(f"Unexpected error: {error}", exc_info=True)
        return jsonify({
            "codigo": "error",
            "info": None,
            "error": {
                "mensaje": "An unexpected error occurred"
            }
        }), 500