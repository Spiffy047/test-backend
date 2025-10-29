# Flask application configuration for IT ServiceDesk
# Manages environment-specific settings and external service configurations

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class with common settings
    
    Contains shared configuration that applies to all environments.
    Sensitive values are loaded from environment variables with fallbacks.
    """
    
    # === SECURITY CONFIGURATION ===
    # Flask secret key for session management and CSRF protection
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # === DATABASE CONFIGURATION ===
    # Disable SQLAlchemy modification tracking for performance
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # === JWT AUTHENTICATION CONFIGURATION ===
    # JWT secret key for token signing (currently disabled for deployment)
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-change-in-production'
    # JWT tokens don't expire (for development convenience)
    JWT_ACCESS_TOKEN_EXPIRES = False
    
    # === EMAIL SERVICE CONFIGURATION ===
    # SendGrid API credentials for email notifications
    SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
    SENDGRID_FROM_EMAIL = os.environ.get('SENDGRID_FROM_EMAIL') or 'mwanikijoe1@gmail.com'
    
    # === CLOUDINARY CONFIGURATION ===
    # Cloudinary service for image uploads and processing
    CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')

class DevelopmentConfig(Config):
    """Development environment configuration
    
    Features:
    - Debug mode enabled for detailed error messages
    - SQLite database for local development
    - Relaxed security for easier testing
    """
    DEBUG = True  # Enable Flask debug mode
    # Use SQLite for local development (fallback if DATABASE_URL not set)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///servicedesk.db'

class ProductionConfig(Config):
    """Production environment configuration
    
    Features:
    - Debug mode disabled for security
    - PostgreSQL database (required)
    - Enhanced security settings
    """
    DEBUG = False  # Disable debug mode for security
    # PostgreSQL database URL (must be provided via environment variable)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Additional production-specific settings can be added here:
    # - SSL requirements
    # - Logging configuration
    # - Cache settings
    # - Rate limiting

# Configuration mapping for easy access
# Usage: config['development'] or config['production']
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig  # Default to development for safety
}