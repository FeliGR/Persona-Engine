from flask import Flask
from utils.logger import logger
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


def register_extensions(app: Flask) -> None:
    if not app.config["TESTING"]:

        CORS(
            app,
            resources={r"/api/*": {"origins": app.config.get("CORS_ORIGINS", "*")}},
        )

        Limiter(
            app=app,
            key_func=get_remote_address,
            default_limits=app.config.get(
                "DEFAULT_RATE_LIMITS", ["100 per day", "10 per minute"]
            ),
        )
    logger.debug("Extensions registered")
