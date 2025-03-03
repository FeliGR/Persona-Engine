import time
from functools import wraps
from typing import Any, Callable, Dict, Tuple, TypeVar, cast

from flask import Blueprint, request, jsonify, current_app
from marshmallow import Schema, fields, ValidationError, validate

from usecases.get_or_create_persona_use_case import GetOrCreatePersonaUseCase
from usecases.get_persona_use_case import GetPersonaUseCase, PersonaNotFoundError
from usecases.update_persona_use_case import UpdatePersonaUseCase

from utils.logger import logger

ResponseType = Tuple[Dict[str, Any], int]
F = TypeVar("F", bound=Callable[..., ResponseType])


class TraitUpdateSchema(Schema):
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

    @staticmethod
    def success(
        data: Any = None, message: str = None, status_code: int = 200
    ) -> ResponseType:
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
        response = {"status": "error", "message": message}
        if details is not None:
            response["details"] = details
        return jsonify(response), status_code


def validate_user_id(f: F) -> F:

    @wraps(f)
    def decorated_function(user_id: str, *args: Any, **kwargs: Any) -> ResponseType:
        if not user_id or not isinstance(user_id, str):
            logger.warning(f"Invalid user ID: {user_id}")
            return ApiResponse.error("Invalid user ID", status_code=400)
        return f(user_id, *args, **kwargs)

    return cast(F, decorated_function)


def create_persona_blueprint(
    get_persona_uc: GetPersonaUseCase,
    get_or_create_uc: GetOrCreatePersonaUseCase,
    update_uc: UpdatePersonaUseCase,
) -> Blueprint:
    bp = Blueprint("persona", __name__)

    @bp.route("/api/persona", methods=["POST"])
    def create_persona() -> ResponseType:
        try:
            data = request.get_json(silent=True) or {}

            user_id = data.get("user_id")
            if not user_id:
                return ApiResponse.error("user_id is required", status_code=400)

            persona = get_or_create_uc.execute(user_id)

            setattr(persona, "user_id", user_id)

            return ApiResponse.success(
                persona.to_dict(), message="Persona created", status_code=201
            )
        except Exception as e:
            logger.error(f"Error creating persona: {str(e)}", exc_info=True)
            return ApiResponse.error("Internal server error", status_code=500)

    @bp.route("/api/persona/<user_id>", methods=["GET"])
    @validate_user_id
    def get_persona(user_id: str) -> ResponseType:
        try:
            try:
                persona = get_persona_uc.execute(user_id)
                return ApiResponse.success(persona.to_dict(), status_code=200)
            except PersonaNotFoundError:
                return ApiResponse.error(
                    f"No persona found for user ID: {user_id}", status_code=404
                )
        except Exception as e:
            logger.error(
                f"Error retrieving persona for user {user_id}: {str(e)}", exc_info=True
            )
            return ApiResponse.error("Internal server error", status_code=500)

    @bp.route("/api/persona/<user_id>", methods=["PATCH"])
    @validate_user_id
    def update_persona(user_id: str) -> ResponseType:

        try:
            data = request.get_json(silent=True) or {}
            if not data:
                return ApiResponse.error("Request body is required", status_code=400)

            try:
                validated_data = TraitUpdateSchema().load(data)
            except ValidationError as err:
                return ApiResponse.error(
                    "Validation error", details=err.messages, status_code=400
                )

            trait_name = validated_data["trait"]
            new_value = validated_data["value"]
            persona = update_uc.execute(user_id, trait_name, new_value)

            setattr(persona, "user_id", user_id)

            return ApiResponse.success(
                persona.to_dict(),
                message=f"Trait '{trait_name}' updated",
                status_code=200,
            )
        except Exception as e:
            logger.error(
                f"Error updating persona for user {user_id}: {str(e)}", exc_info=True
            )
            return ApiResponse.error("Internal server error", status_code=500)

    @bp.route("/api/persona", methods=["GET"])
    def list_personas() -> ResponseType:

        try:

            limit = int(request.args.get("limit", 100))
            offset = int(request.args.get("offset", 0))

            personas = current_app.persona_repository.list_personas(
                limit=limit, offset=offset
            )
            data = []
            for user_id, persona in personas:
                setattr(persona, "user_id", user_id)
                data.append(persona.to_dict())
            return ApiResponse.success(data, status_code=200)
        except Exception as e:
            logger.error(f"Error listing personas: {str(e)}", exc_info=True)
            return ApiResponse.error("Internal server error", status_code=500)

    return bp
