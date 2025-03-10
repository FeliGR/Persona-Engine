"""
Flask Application Factory Module

This module provides a factory pattern implementation for creating and configuring
Flask applications in different environments (development, testing, production).
It handles the registration of extensions, repositories, use cases, blueprints,
error handlers, and routes.

The ApplicationFactory class ensures consistent application setup with proper
dependency injection and configuration based on the environment.
"""

import os
from typing import Type

from flask import Flask

from adapters.controllers.persona_controller import create_persona_blueprint
from adapters.repositories.sqlalchemy_persona_repository import \
    SQLAlchemyPersonaRepository
from config import Config, DevelopmentConfig, ProductionConfig, TestingConfig
from usecases.get_or_create_persona_use_case import GetOrCreatePersonaUseCase
from usecases.get_persona_use_case import GetPersonaUseCase
from usecases.update_persona_use_case import UpdatePersonaUseCase
from utils.logger import app_logger

from .extensions import register_extensions
from .handlers import (register_error_handlers, register_request_hooks,
                       register_shutdown_handlers)
from .routes import register_routes


class ApplicationFactory:
    """
    Factory class for creating and configuring a Flask application.
    """

    @staticmethod
    def create_app(config_class: Type[Config] = None) -> Flask:
        """
        Creates and configures a Flask application instance.

        Args:
            config_class (Type[Config], optional): The configuration class to use. Defaults to None.

        Returns:
            Flask: The configured Flask application instance.
        """
        if config_class is None:
            env = os.environ.get("FLASK_ENV", "development").lower()
            config_map = {
                "development": DevelopmentConfig,
                "production": ProductionConfig,
                "testing": TestingConfig,
            }
            config_class = config_map.get(env, DevelopmentConfig)

        flask_app = Flask(__name__)
        flask_app.config.from_object(config_class)

        register_extensions(flask_app)
        ApplicationFactory._register_repositories(flask_app)
        ApplicationFactory._register_use_cases(flask_app)
        ApplicationFactory._register_blueprints(flask_app)
        register_error_handlers(flask_app)
        register_request_hooks(flask_app)
        register_shutdown_handlers(flask_app)
        register_routes(flask_app)

        app_logger.info(
            "Application started in %s mode",
            os.environ.get("FLASK_ENV", "development").lower(),
        )
        return flask_app

    @staticmethod
    def _register_repositories(flask_app: Flask) -> None:
        """
        Registers repositories and attaches them to the Flask app.

        Args:
            flask_app (Flask): The Flask application instance.
        """
        flask_app.persona_repository = SQLAlchemyPersonaRepository(
            flask_app.config["DB_URI"]
        )
        app_logger.info("Using SQLAlchemy repository")

    @staticmethod
    def _register_use_cases(flask_app: Flask) -> None:
        """
        Registers use cases and attaches them to the Flask app.

        Args:
            flask_app (Flask): The Flask application instance.
        """
        repo = flask_app.persona_repository
        flask_app.get_or_create_persona_use_case = GetOrCreatePersonaUseCase(repo)
        flask_app.get_persona_use_case = GetPersonaUseCase(repo)
        flask_app.update_persona_use_case = UpdatePersonaUseCase(repo)

    @staticmethod
    def _register_blueprints(flask_app: Flask) -> None:
        """
        Registers blueprints for the Flask application.

        Args:
            flask_app (Flask): The Flask application instance.
        """
        persona_bp = create_persona_blueprint(
            flask_app.get_persona_use_case,
            flask_app.get_or_create_persona_use_case,
            flask_app.update_persona_use_case,
        )
        flask_app.register_blueprint(persona_bp)


# Create convenience function for WSGI servers
create_app = ApplicationFactory.create_app

# Create default application instance
app = create_app()

if __name__ == "__main__":
    app.run(
        host=app.config.get("HOST", "0.0.0.0"),
        port=app.config.get("PORT", 5001),
        debug=app.config.get("DEBUG", False),
    )
