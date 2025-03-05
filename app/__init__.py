from flask import Flask
from typing import Type
import os
from .extensions import register_extensions
from .handlers import (
    register_error_handlers,
    register_request_hooks,
    register_shutdown_handlers,
)
from .routes import register_routes
from adapters.repositories.sqlalchemy_persona_repository import SQLAlchemyPersonaRepository
from usecases.get_or_create_persona_use_case import GetOrCreatePersonaUseCase
from usecases.get_persona_use_case import GetPersonaUseCase
from usecases.update_persona_use_case import UpdatePersonaUseCase
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

        register_extensions(app)
        ApplicationFactory._register_repositories(app)
        ApplicationFactory._register_use_cases(app)
        ApplicationFactory._register_blueprints(app)
        register_error_handlers(app)
        register_request_hooks(app)
        register_shutdown_handlers(app)
        register_routes(app)

        logger.info(
            f"Application started in {os.environ.get('FLASK_ENV', 'development').lower()} mode"
        )
        return app

    @staticmethod
    def _register_repositories(app: Flask) -> None:
        app.persona_repository = SQLAlchemyPersonaRepository(app.config["DB_URI"])
        logger.info("Using SQLAlchemy repository")

    @staticmethod
    def _register_use_cases(app: Flask) -> None:
        repo = app.persona_repository
        app.get_or_create_persona_use_case = GetOrCreatePersonaUseCase(repo)
        app.get_persona_use_case = GetPersonaUseCase(repo)
        app.update_persona_use_case = UpdatePersonaUseCase(repo)

    @staticmethod
    def _register_blueprints(app: Flask) -> None:
        persona_bp = create_persona_blueprint(
            app.get_persona_use_case,
            app.get_or_create_persona_use_case,
            app.update_persona_use_case,
        )
        app.register_blueprint(persona_bp)


create_app = ApplicationFactory.create_app
app = create_app()

if __name__ == "__main__":
    app.run(
        host=app.config.get("HOST", "0.0.0.0"),
        port=app.config.get("PORT", 5001),
        debug=app.config.get("DEBUG", False),
    )
