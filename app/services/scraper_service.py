"""
Service layer wrapper for the PagaFacilScraper.
"""
from scraper import PagaFacilScraper
import logging

logger = logging.getLogger(__name__)


class ScraperService:
    """
    Service layer for vehicle information scraping.
    
    This class wraps the PagaFacilScraper and provides additional
    business logic, validation, and error handling.
    """
    
    def __init__(self, proxy_host, proxy_port, proxy_username, proxy_password,
                 base_url, form_url, request_timeout=30, max_retry_attempts=3,
                 captcha_max_attempts=2):
        """
        Initialize the scraper service.
        
        Args:
            proxy_host: Proxy server hostname
            proxy_port: Proxy server port
            proxy_username: Proxy authentication username
            proxy_password: Proxy authentication password
            base_url: Base URL for the target website
            form_url: Form URL for vehicle queries
            request_timeout: HTTP request timeout in seconds
            max_retry_attempts: Maximum retry attempts for failed requests
            captcha_max_attempts: Maximum captcha solving attempts
        """
        self.scraper = PagaFacilScraper(
            proxy_host=proxy_host,
            proxy_port=proxy_port,
            proxy_username=proxy_username,
            proxy_password=proxy_password
        )
        
        self.config = {
            'base_url': base_url,
            'form_url': form_url,
            'request_timeout': request_timeout,
            'max_retry_attempts': max_retry_attempts,
            'captcha_max_attempts': captcha_max_attempts
        }
        
        logger.info(f"ScraperService initialized with config: {self.config}")
    
    def get_vehicle_info(self, plate, vin):
        """
        Get vehicle tax information.
        
        Args:
            plate: License plate number
            vin: Vehicle Identification Number
            
        Returns:
            Dictionary containing vehicle information and taxes
        """
        try:
            logger.info(f"ScraperService: Getting vehicle info for plate={plate}, vin={vin}")
            
            # Clean and validate inputs
            plate = self._clean_plate(plate)
            vin = self._clean_vin(vin)
            
            # Use the existing scraper logic
            result = self.scraper.get_vehicle_info(plate, vin)
            
            # Add service metadata
            result['_metadata'] = {
                'service_version': '1.0.0',
                'scraper_used': 'PagaFacilScraper',
                'processed_plate': plate,
                'processed_vin': vin
            }
            
            logger.info(f"ScraperService: Result code={result['codigo']}")
            return result
            
        except Exception as e:
            logger.error(f"ScraperService error: {str(e)}", exc_info=True)
            return {
                "codigo": "error",
                "info": None,
                "error": {
                    "mensaje": f"Service error: {str(e)}"
                }
            }
    
    def _clean_plate(self, plate):
        """Clean and normalize license plate."""
        return plate.strip().upper().replace(" ", "")
    
    def _clean_vin(self, vin):
        """Clean and normalize VIN."""
        return vin.strip().upper().replace(" ", "")
    
    def health_check(self):
        """
        Perform a health check on the scraper service.
        
        Returns:
            Dictionary with health status
        """
        try:
            # Basic connectivity test
            # You could extend this to test actual scraping
            return {
                'status': 'healthy',
                'scraper': 'ready',
                'config': self.config
            }
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                'status': 'unhealthy',
                'error': str(e)
            }