import os


class Config:
    DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
    TESTING = os.environ.get("TESTING", "False").lower() == "true"
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

    DB_URI = os.environ.get("DB_URI", "sqlite:///persona.db")

    API_RATE_LIMIT = int(os.environ.get("API_RATE_LIMIT", "100"))
    SECRET_KEY = os.environ.get("SECRET_KEY", "development-key-change-in-production")

    VERSION = "0.1.0"
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", 5001))

    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")

    DEFAULT_RATE_LIMITS = ["100 per day", "10 per minute"]


class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    REPOSITORY_TYPE = "memory"


class ProductionConfig(Config):
    DEBUG = False
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "WARNING")
    REPOSITORY_TYPE = os.environ.get("REPOSITORY_TYPE", "postgres")


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    REPOSITORY_TYPE = "memory"
