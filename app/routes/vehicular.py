"""
Vehicle tax information routes.
"""
from flask import Blueprint, request, jsonify, current_app
from ..services import ScraperService
from ..utils.validators import validate_plate, validate_vin
import logging

logger = logging.getLogger(__name__)

vehicular_routes = Blueprint('vehicular', __name__, url_prefix='/api/vehicular')

# Initialize scraper service (will be configured when app starts)
scraper_service = None


def init_scraper_service():
    """Initialize the scraper service with current app config."""
    global scraper_service
    if scraper_service is None:
        scraper_service = ScraperService(
            proxy_host=current_app.config['PROXY_HOST'],
            proxy_port=current_app.config['PROXY_PORT'],
            proxy_username=current_app.config['PROXY_USERNAME'],
            proxy_password=current_app.config['PROXY_PASSWORD'],
            base_url=current_app.config['BASE_URL'],
            form_url=current_app.config['FORM_URL'],
            request_timeout=current_app.config['REQUEST_TIMEOUT'],
            max_retry_attempts=current_app.config['MAX_RETRY_ATTEMPTS'],
            captcha_max_attempts=current_app.config['CAPTCHA_MAX_ATTEMPTS']
        )
    return scraper_service


@vehicular_routes.route('/tenencia/<string:plate>')
def get_vehicular_tenencia(plate):
    """
    Get vehicle tax information by plate and VIN.
    
    Args:
        plate (str): Vehicle license plate
        
    Query Parameters:
        niv (str): Vehicle Identification Number (VIN)
        
    Returns:
        JSON response with vehicle tax information
    """
    try:
        # Get VIN from query parameters
        vin = request.args.get('niv')
        if not vin:
            return jsonify({
                "codigo": "error",
                "info": None,
                "error": {
                    "mensaje": "Parameter 'niv' (VIN) is required"
                }
            }), 400
        
        # Validate input parameters
        plate_validation = validate_plate(plate)
        if not plate_validation['valid']:
            return jsonify({
                "codigo": "error",
                "info": None,
                "error": {
                    "mensaje": f"Invalid plate format: {plate_validation['message']}"
                }
            }), 400
            
        vin_validation = validate_vin(vin)
        if not vin_validation['valid']:
            return jsonify({
                "codigo": "error",
                "info": None,
                "error": {
                    "mensaje": f"Invalid VIN format: {vin_validation['message']}"
                }
            }), 400
        
        # Initialize scraper service if needed
        service = init_scraper_service()
        
        # Scrape vehicle information
        result = service.get_vehicle_info(plate, vin)
        
        # Determine HTTP status code based on result
        status_code = 200 if result['codigo'] == 'ok' else 404
        
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error in get_vehicular_tenencia: {str(e)}", exc_info=True)
        return jsonify({
            "codigo": "error",
            "info": None,
            "error": {
                "mensaje": f"Internal server error: {str(e)}"
            }
        }), 500