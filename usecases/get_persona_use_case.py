from utils.logger import logger
from core.domain.exceptions import PersonaNotFoundError
from core.domain.persona_model import Persona
from usecases.persona_repository_interface import IPersonaRepository

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
