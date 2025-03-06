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

        _app = Flask(__name__)
        app.config.from_object(config_class)

        register_extensions(app)
        ApplicationFactory._register_repositories(app)
        ApplicationFactory._register_use_cases(app)
        ApplicationFactory._register_blueprints(app)
        register_error_handlers(app)
        register_request_hooks(app)
        register_shutdown_handlers(_app)
        register_routes(app)

        app_logger.info(
            "Application started in %s mode",
            os.environ.get("FLASK_ENV", "development").lower(),
        )
        return app

    @staticmethod
    def _register_repositories(_app: Flask) -> None:
        """
        Registers repositories and attaches them to the Flask app.

        Args:
            app (Flask): The Flask application instance.
        """
        _app.persona_repository = SQLAlchemyPersonaRepository(_app.config["DB_URI"])
        app_logger.info("Using SQLAlchemy repository")

    @staticmethod
    def _register_use_cases(_app: Flask) -> None:
        """
        Registers use cases and attaches them to the Flask app.

        Args:
            app (Flask): The Flask application instance.
        """
        repo = _app.persona_repository
        _app.get_or_create_persona_use_case = GetOrCreatePersonaUseCase(repo)
        _app.get_persona_use_case = GetPersonaUseCase(repo)
        _app.update_persona_use_case = UpdatePersonaUseCase(repo)

    @staticmethod
    def _register_blueprints(_app: Flask) -> None:
        """
        Registers blueprints for the Flask application.

        Args:
            app (Flask): The Flask application instance.
        """
        app.register_blueprint(create_persona_blueprint)


create_app = ApplicationFactory.create_app
app = create_app()

if __name__ == "__main__":
    app.run(
        host=app.config.get("HOST", "0.0.0.0"),
        port=app.config.get("PORT", 5001),
        debug=app.config.get("DEBUG", False),
    )
