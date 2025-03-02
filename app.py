from flask import Flask, jsonify, request, g
from werkzeug.exceptions import HTTPException
import atexit
import time
import os
from typing import Type
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from adapters.repositories.in_memory_persona_repository import InMemoryPersonaRepository
from application.get_or_create_persona_use_case import GetOrCreatePersonaUseCase
from application.update_persona_use_case import UpdatePersonaUseCase
from adapters.controllers.persona_controller import create_persona_blueprint
from utils.logger import logger
from config import Config, DevelopmentConfig, ProductionConfig, TestingConfig


class ApplicationFactory:

    @staticmethod
    def create_app(config_class: Type[Config] = None) -> Flask:

        if config_class is None:
            env = os.environ.get("FLASK_ENV", "development").lower()
            config_map = {
                "development": DevelopmentConfig,
                "production": ProductionConfig,
                "testing": TestingConfig,
            }
            config_class = config_map.get(env, DevelopmentConfig)

        app = Flask(__name__)
        app.config.from_object(config_class)

        ApplicationFactory._register_extensions(app)
        ApplicationFactory._register_repositories(app)
        ApplicationFactory._register_use_cases(app)
        ApplicationFactory._register_blueprints(app)
        ApplicationFactory._register_error_handlers(app)
        ApplicationFactory._register_request_hooks(app)
        ApplicationFactory._register_shutdown_handlers(app)

        @app.route("/")
        def index():
            return jsonify(
                {
                    "status": "ok",
                    "service": "persona-engine",
                    "version": app.config.get("VERSION", "0.1.0"),
                }
            )

        @app.route("/health")
        def health():
            return jsonify({"status": "healthy", "timestamp": time.time()})

        logger.info(
            f"Application started in {os.environ.get('FLASK_ENV', 'development').lower()} mode"
        )
        return app

    @staticmethod
    def _register_extensions(app: Flask) -> None:
        """Register Flask extensions."""
        if not app.config["TESTING"]:

            from flask_cors import CORS

            CORS(
                app,
                resources={r"/api/*": {"origins": app.config.get("CORS_ORIGINS", "*")}},
            )

            limiter = Limiter(
                app=app,
                key_func=get_remote_address,
                default_limits=app.config.get(
                    "DEFAULT_RATE_LIMITS", ["100 per day", "10 per minute"]
                ),
            )

    @staticmethod
    def _register_repositories(app: Flask) -> None:
        """Register repositories based on configuration."""
        repo_type = app.config.get("REPOSITORY_TYPE", "memory")
        if repo_type == "memory":
            app.persona_repository = InMemoryPersonaRepository()
        elif repo_type == "postgres":
            from adapters.repositories.sqlalchemy_persona_repository import (
                SQLAlchemyPersonaRepository,
            )

            app.persona_repository = SQLAlchemyPersonaRepository(app.config["DB_URI"])
        else:
            app.persona_repository = InMemoryPersonaRepository()

        logger.info(f"Using {repo_type} repository")

    @staticmethod
    def _register_use_cases(app: Flask) -> None:
        """Register use cases with their dependencies."""
        repo = app.persona_repository
        app.get_or_create_persona_use_case = GetOrCreatePersonaUseCase(repo)
        app.update_persona_use_case = UpdatePersonaUseCase(repo)

    @staticmethod
    def _register_blueprints(app: Flask) -> None:
        """Register all blueprints with the app."""
        persona_bp = create_persona_blueprint(
            app.get_or_create_persona_use_case, app.update_persona_use_case
        )
        app.register_blueprint(persona_bp)

    @staticmethod
    def _register_error_handlers(app: Flask) -> None:
        """Register error handlers for various exceptions."""

        @app.errorhandler(400)
        def handle_bad_request(error):
            logger.warning(f"Bad request: {error}")
            return jsonify({"error": "Bad request", "message": str(error)}), 400

        @app.errorhandler(404)
        def handle_not_found(error):
            return jsonify({"error": "Resource not found", "message": str(error)}), 404

        @app.errorhandler(429)
        def handle_rate_limit_exceeded(error):
            logger.warning(f"Rate limit exceeded: {error}")
            return jsonify({"error": "Too many requests", "message": str(error)}), 429

        @app.errorhandler(HTTPException)
        def handle_http_exception(error):
            logger.error(f"HTTP exception: {error}")
            return (
                jsonify({"error": error.name, "message": error.description}),
                error.code,
            )

        @app.errorhandler(Exception)
        def handle_exception(error):
            logger.error(f"Unhandled exception: {str(error)}", exc_info=True)
            return (
                jsonify(
                    {
                        "error": "Internal server error",
                        "message": "An unexpected error occurred",
                    }
                ),
                500,
            )

    @staticmethod
    def _register_request_hooks(app: Flask) -> None:
        """Register request hooks for logging and metrics."""

        @app.before_request
        def before_request():
            g.start_time = time.time()
            logger.debug(f"Request started: {request.method} {request.path}")

        @app.after_request
        def after_request(response):
            if hasattr(g, "start_time"):
                elapsed = time.time() - g.start_time
                logger.info(
                    f"Request completed: {request.method} {request.path} - Status: {response.status_code} - Time: {elapsed:.4f}s"
                )
            return response

    @staticmethod
    def _register_shutdown_handlers(app: Flask) -> None:
        """Register shutdown handlers."""

        def on_exit():
            logger.info("Application shutting down")
            if hasattr(app, "persona_repository"):
                # Implement close/cleanup method in repositories if needed
                pass

        atexit.register(on_exit)


create_app = ApplicationFactory.create_app
app = create_app()

if __name__ == "__main__":
    app.run(
        host=app.config.get("HOST", "0.0.0.0"),
        port=app.config.get("PORT", 5001),
        debug=app.config.get("DEBUG", False),
    )
