"""
Main Flask application entry point for Paga Fácil vehicle tax scraper.

This modular Flask application scrapes vehicle tax information from
the Mexican government's Paga Fácil website.
"""
import os
import logging
from app import create_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Get configuration environment
config_name = os.getenv('FLASK_ENV', 'development')

# Create Flask application using the factory pattern
app = create_app()

if __name__ == '__main__':
    # Get port from environment variable (for Heroku compatibility)
    port = int(os.environ.get('PORT', 5000))
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=port,
        debug=app.config.get('DEBUG', False)
    )