"""
Persona Controller Module

This module provides the HTTP controller implementation for the Persona API.
It handles RESTful operations for creating, retrieving, and updating persona
profiles, with proper request validation and error handling.

The controller implements the IPersonaController interface and serves as an
adapter between the HTTP layer and the application's use cases.
"""

from functools import wraps
from typing import Any, Callable, Dict, Tuple, TypeVar, cast

from flask import Blueprint, jsonify, request
from marshmallow import Schema, ValidationError, fields, validate

from core.domain.exceptions import PersonaValidationError, TraitNotFoundError
from core.interfaces.persona_controller_interface import IPersonaController
from usecases.get_or_create_persona_use_case import GetOrCreatePersonaUseCase
from usecases.get_persona_use_case import (GetPersonaUseCase,
                                           PersonaNotFoundError)
from usecases.update_persona_use_case import UpdatePersonaUseCase
from utils.logger import app_logger

ResponseType = Tuple[Dict[str, Any], int]
F = TypeVar("F", bound=Callable[..., ResponseType])


class TraitUpdateSchema(Schema):
    """
    Schema for validating the trait update payload.

    Attributes:
        trait (str): The name of the trait to update. Must be one of:
                     openness, conscientiousness, extraversion, agreeableness, 'neuroticism.
        value (float): The new value for the trait, must be between 1.0 and 5.0.
    """

    trait = fields.String(
        required=True,
        validate=validate.OneOf(
            [
                "openness",
                "conscientiousness",
                "extraversion",
                "agreeableness",
                "neuroticism",
            ]
        ),
    )
    value = fields.Float(
        required=True,
        validate=validate.Range(min=1.0, max=5.0),
    )


class ApiResponse:
    """
    Helper class for constructing API responses.
    """

    @staticmethod
    def success(
        data: Any = None, message: str = None, status_code: int = 200
    ) -> ResponseType:
        """
        Create a success response.

        Args:
            data (Any, optional): The response payload.
            message (str, optional): An optional message.
            status_code (int): The HTTP status code.

        Returns:
            ResponseType: A tuple of the JSON response and status code.
        """
        response = {"status": "success"}
        if data is not None:
            response["data"] = data
        if message is not None:
            response["message"] = message
        return jsonify(response), status_code

    @staticmethod
    def error(
        message: str, details: Any = None, status_code: int = 400
    ) -> ResponseType:
        """
        Create an error response.

        Args:
            message (str): The error message.
            details (Any, optional): Additional error details.
            status_code (int): The HTTP status code.

        Returns:
            ResponseType: A tuple of the JSON response and status code.
        """
        response = {"status": "error", "message": message}
        if details is not None:
            response["details"] = details
        return jsonify(response), status_code


def validate_user_id(f: F) -> F:
    """
    Decorator to validate that the user_id parameter is a non-empty string.

    Args:
        f (Callable): The function to decorate.

    Returns:
        Callable: The decorated function.
    """

    @wraps(f)
    def decorated_function(user_id: str, *args: Any, **kwargs: Any) -> ResponseType:
        if not user_id or not isinstance(user_id, str):
            app_logger.warning("Invalid user ID: %s", user_id)
            return ApiResponse.error("Invalid user ID", status_code=400)
        return f(user_id, *args, **kwargs)

    return cast(F, decorated_function)


class PersonaController(IPersonaController):
    """
    HTTP controller for handling Persona API requests.

    This controller serves as an adapter between the HTTP layer and the application's use cases.
    """

    def __init__(
        self,
        get_persona_uc: GetPersonaUseCase,
        get_or_create_uc: GetOrCreatePersonaUseCase,
        update_uc: UpdatePersonaUseCase,
    ):
        """
        Initialize the PersonaController.

        Args:
            get_persona_uc: Use case for retrieving a persona.
            get_or_create_uc: Use case for getting or creating a persona.
            update_uc: Use case for updating a persona.
        """
        self.get_persona_uc = get_persona_uc
        self.get_or_create_uc = get_or_create_uc
        self.update_uc = update_uc

    def get_persona(self, user_id: str) -> ResponseType:
        """
        Retrieve a persona by user ID.

        Args:
            user_id (str): The unique identifier for the user.

        Returns:
            ResponseType: The response containing the persona data or an error message.
        """
        try:
            persona = self.get_persona_uc.execute(user_id)
            return ApiResponse.success(persona.to_dict(), status_code=200)
        except PersonaNotFoundError:
            return ApiResponse.error(
                message=f"No persona found for user ID: {user_id}", status_code=404
            )
        except Exception as e:
            app_logger.error(
                "Error retrieving persona for user %s: %s",
                user_id,
                str(e),
                exc_info=True,
            )
            return ApiResponse.error("Internal server error", status_code=500)

    def create_persona(self) -> ResponseType:
        """
        Create or retrieve a persona based on the provided user ID.

        Expects a JSON payload with a 'user_id' key.

        Returns:
            ResponseType: The response containing the persona data or an error message.
        """
        try:
            data = request.get_json(silent=True) or {}
            user_id = data.get("user_id")
            if not user_id:
                return ApiResponse.error("user_id is required", status_code=400)
            persona = self.get_or_create_uc.execute(user_id)
            return ApiResponse.success(
                persona.to_dict(), message="Persona created", status_code=201
            )
        except Exception as e:
            app_logger.error("Error creating persona: %s", str(e), exc_info=True)
            return ApiResponse.error("Internal server error", status_code=500)

    def update_persona(self, user_id: str) -> ResponseType:
        """
        Update a persona's trait value.

        Expects a JSON payload with 'trait' and 'value' keys.

        Args:
            user_id (str): The unique identifier for the user.

        Returns:
            ResponseType: The response containing the updated persona data or an error message.
        """
        try:
            data = request.get_json(silent=True) or {}
            if not data:
                return ApiResponse.error("Request body is required", status_code=400)
            validated_data = TraitUpdateSchema().load(data)
            trait_name = validated_data["trait"]
            new_value = validated_data["value"]
            persona = self.update_uc.execute(user_id, trait_name, new_value)
            return ApiResponse.success(
                persona.to_dict(),
                message=f"Trait '{trait_name}' updated",
                status_code=200,
            )
        except TraitNotFoundError as e:
            return ApiResponse.error(str(e), status_code=400)
        except PersonaValidationError as e:
            return ApiResponse.error(str(e), status_code=400)
        except ValueError as e:
            return ApiResponse.error(str(e), status_code=400)
        except ValidationError as err:
            return ApiResponse.error(
                "Validation error", details=err.messages, status_code=400
            )
        except Exception as e:
            app_logger.error(
                "Error updating persona for user %s: %s", user_id, str(e), exc_info=True
            )
            return ApiResponse.error("Internal server error", status_code=500)


def create_persona_blueprint(
    get_persona_use_case: GetPersonaUseCase,
    get_or_create_persona_use_case: GetOrCreatePersonaUseCase,
    update_persona_use_case: UpdatePersonaUseCase,
) -> Blueprint:
    """
    Create and configure a Flask blueprint for persona API endpoints.

    Args:
        get_persona_use_case: Use case for retrieving personas
        get_or_create_persona_use_case: Use case for creating personas
        update_persona_use_case: Use case for updating personas

    Returns:
        Blueprint: Configured Flask blueprint with persona routes
    """
    blueprint = Blueprint("persona", __name__, url_prefix="/api/personas")

    controller = PersonaController(
        get_persona_use_case, get_or_create_persona_use_case, update_persona_use_case
    )

    @blueprint.route("/<user_id>", methods=["GET"])
    def get_persona(user_id):
        return controller.get_persona(user_id)

    @blueprint.route("/", methods=["POST"])
    def create_persona():
        return controller.create_persona()

    @blueprint.route("/<user_id>", methods=["PUT"])
    def update_persona(user_id):
        return controller.update_persona(user_id)

    return blueprint
