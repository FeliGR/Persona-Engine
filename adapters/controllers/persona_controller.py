from flask import Blueprint, request, jsonify, current_app
from marshmallow import Schema, fields, ValidationError
from functools import wraps
import time
from typing import Any, Callable, Dict, Tuple, TypeVar, cast

from application.get_or_create_persona_use_case import GetOrCreatePersonaUseCase
from application.update_persona_use_case import UpdatePersonaUseCase
from utils.logger import logger

ResponseType = Tuple[Dict[str, Any], int]
F = TypeVar("F", bound=Callable[..., ResponseType])


class TraitUpdateSchema(Schema):

    trait = fields.String(
        required=True,
        validate=lambda x: x
        in [
            "openness",
            "conscientiousness",
            "extraversion",
            "agreeableness",
            "neuroticism",
        ],
    )
    value = fields.Float(required=True, validate=lambda x: 1.0 <= x <= 5.0)


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
    get_or_create_uc: GetOrCreatePersonaUseCase, update_uc: UpdatePersonaUseCase
) -> Blueprint:
    bp = Blueprint("persona", __name__)

    @bp.route("/api/persona", methods=["POST"])
    def create_persona() -> ResponseType:
        """
        Create a new persona.
        You could either use default values or accept a JSON payload for customization.
        """
        try:
            data = request.get_json(silent=True) or {}

            user_id = data.get("user_id")
            if not user_id:
                return ApiResponse.error("user_id is required", status_code=400)

            persona = get_or_create_uc.execute(user_id)
            persona_data = {
                "user_id": user_id,
                "openness": persona.openness,
                "conscientiousness": persona.conscientiousness,
                "extraversion": persona.extraversion,
                "agreeableness": persona.agreeableness,
                "neuroticism": persona.neuroticism,
            }
            return ApiResponse.success(
                persona_data, message="Persona created", status_code=201
            )
        except Exception as e:
            logger.error(f"Error creating persona: {str(e)}", exc_info=True)
            return ApiResponse.error("Internal server error", status_code=500)

    @bp.route("/api/persona/<user_id>", methods=["GET"])
    @validate_user_id
    def get_persona(user_id: str) -> ResponseType:

        try:
            persona = get_or_create_uc.execute(user_id)
            persona_data = {
                "user_id": user_id,
                "openness": persona.openness,
                "conscientiousness": persona.conscientiousness,
                "extraversion": persona.extraversion,
                "agreeableness": persona.agreeableness,
                "neuroticism": persona.neuroticism,
            }
            return ApiResponse.success(persona_data)
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
            updated = update_uc.execute(user_id, trait_name, new_value)
            persona_data = {
                "user_id": user_id,
                "openness": updated.openness,
                "conscientiousness": updated.conscientiousness,
                "extraversion": updated.extraversion,
                "agreeableness": updated.agreeableness,
                "neuroticism": updated.neuroticism,
            }
            return ApiResponse.success(
                persona_data, message=f"Trait '{trait_name}' updated", status_code=200
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
            for persona in personas:
                data.append(
                    {
                        "openness": persona.openness,
                        "conscientiousness": persona.conscientiousness,
                        "extraversion": persona.extraversion,
                        "agreeableness": persona.agreeableness,
                        "neuroticism": persona.neuroticism,
                    }
                )
            return ApiResponse.success(data, status_code=200)
        except Exception as e:
            logger.error(f"Error listing personas: {str(e)}", exc_info=True)
            return ApiResponse.error("Internal server error", status_code=500)

    @bp.route("/api/health", methods=["GET"])
    def health_check() -> ResponseType:

        return ApiResponse.success({"status": "ok"})

    return bp
