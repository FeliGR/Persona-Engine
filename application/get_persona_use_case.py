import logging

from core.persona_model import Persona
from application.persona_repository_interface import IPersonaRepository

logger = logging.getLogger(__name__)


class PersonaNotFoundError(Exception):
    pass


class GetPersonaUseCase:
    def __init__(self, repository: IPersonaRepository):
        self.repository = repository

    def execute(self, user_id: str) -> Persona:
        if not user_id or not isinstance(user_id, str):
            raise ValueError("User ID must be a non-empty string")

        persona = self.repository.get_persona(user_id)

        if not persona:
            logger.info(f"No persona found for user_id: {user_id}")
            raise PersonaNotFoundError(f"Persona not found for user_id: {user_id}")

        return persona
