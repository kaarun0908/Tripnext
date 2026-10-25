import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

def normalize_db_url(url):
    if not url:
        return url
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg2://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'tripnest-default-dev-secret-key-replace-in-prod')
    
    db_url = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/tripnest')
    SQLALCHEMY_DATABASE_URI = normalize_db_url(db_url)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Session and Cookie Security
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    
    # In test mode, allow isolated in-memory test database or dedicated test db
    test_db = os.environ.get('TEST_DATABASE_URL')
    if test_db and 'postgres' in test_db and os.environ.get('USE_PG_FOR_TESTS'):
        SQLALCHEMY_DATABASE_URI = normalize_db_url(test_db)
    else:
        # Fast, completely isolated test database that works across environments
        SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    SQLALCHEMY_ENGINE_OPTIONS = {}

class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
