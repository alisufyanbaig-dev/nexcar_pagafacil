"""
Application configuration module.
"""
import os


class Config:
    """Base configuration class."""
    
    # Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    DEBUG = os.getenv('FLASK_ENV') == 'development'
    
    # Proxy configuration
    PROXY_HOST = os.getenv('PROXY_HOST', 'gw.dataimpulse.com')
    PROXY_PORT = int(os.getenv('PROXY_PORT', '823'))
    PROXY_USERNAME = os.getenv('PROXY_USERNAME', '3f4e5d29475e1682aa60__cr.mx')
    PROXY_PASSWORD = os.getenv('PROXY_PASSWORD', '8c8d76378fbdee8f')
    
    # Scraper configuration
    BASE_URL = os.getenv('BASE_URL', 'https://www.pagafacil.gob.mx/pagafacilv2/epago/cv/')
    FORM_URL = os.getenv('FORM_URL', 'control_vehicular_25.php')
    
    # Request configuration
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '30'))
    MAX_RETRY_ATTEMPTS = int(os.getenv('MAX_RETRY_ATTEMPTS', '3'))
    
    # Captcha configuration
    CAPTCHA_MAX_ATTEMPTS = int(os.getenv('CAPTCHA_MAX_ATTEMPTS', '2'))
    TWOCAPTCHA_API_KEY = os.getenv('TWOCAPTCHA_API_KEY')


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}