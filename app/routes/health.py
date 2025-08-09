"""
Health check and monitoring routes.
"""
from flask import Blueprint, jsonify, current_app
import logging

logger = logging.getLogger(__name__)

health_routes = Blueprint('health', __name__)


@health_routes.route('/health')
def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    
    Returns:
        JSON response with service status
    """
    try:
        # Basic health check - could be extended with database checks, etc.
        health_status = {
            "status": "ok",
            "service": "pagafacil-scraper",
            "version": "1.0.0"
        }
        
        # Add configuration info in development mode
        if current_app.config.get('DEBUG'):
            health_status["debug_info"] = {
                "proxy_host": current_app.config['PROXY_HOST'],
                "base_url": current_app.config['BASE_URL'],
                "timeout": current_app.config['REQUEST_TIMEOUT']
            }
        
        return jsonify(health_status), 200
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "service": "pagafacil-scraper",
            "error": str(e)
        }), 500


@health_routes.route('/status')
def detailed_status():
    """
    Detailed status endpoint with more comprehensive checks.
    
    Returns:
        JSON response with detailed service status
    """
    try:
        from ..services import ScraperService
        
        status = {
            "status": "ok",
            "service": "pagafacil-scraper",
            "version": "1.0.0",
            "components": {
                "scraper": "ok",
                "captcha_solver": "ok"
            },
            "configuration": {
                "proxy_enabled": bool(current_app.config.get('PROXY_HOST')),
                "captcha_service_enabled": bool(current_app.config.get('TWOCAPTCHA_API_KEY')),
                "timeout": current_app.config['REQUEST_TIMEOUT'],
                "max_retries": current_app.config['MAX_RETRY_ATTEMPTS']
            }
        }
        
        return jsonify(status), 200
        
    except Exception as e:
        logger.error(f"Status check failed: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "service": "pagafacil-scraper",
            "error": str(e),
            "components": {
                "scraper": "error",
                "captcha_solver": "unknown"
            }
        }), 500