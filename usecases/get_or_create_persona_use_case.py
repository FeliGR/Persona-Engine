from typing import Optional

from core.domain.persona_model import Persona
from core.interfaces.persona_repository_interface import IPersonaRepository
from core.interfaces.use_case_interfaces import IGetOrCreatePersonaUseCase
from utils.logger import logger


class GetOrCreatePersonaUseCase(IGetOrCreatePersonaUseCase):

    def __init__(self, repository: IPersonaRepository):
        if not repository:
            raise ValueError("Repository cannot be None")
        self.repository = repository

    def execute(self, user_id: str) -> Persona:
        if not user_id or not isinstance(user_id, str):
            logger.error(f"Invalid user_id provided: {user_id!r}")
            raise ValueError("User ID must be a non-empty string")

        try:
            logger.debug(f"Retrieving persona for user_id: {user_id}")
            persona = self._get_persona(user_id)

            if not persona:
                logger.info(
                    f"No persona found for user_id: {user_id}. Creating new persona."
                )
                persona = self._create_and_save_persona(user_id)

            return persona

        except Exception as e:
            logger.exception(
                f"Error in GetOrCreatePersonaUseCase for user_id {user_id}: {str(e)}"
            )
            raise

    def _get_persona(self, user_id: str) -> Optional[Persona]:
        try:
            return self.repository.get_persona(user_id)
        except Exception as e:
            logger.error(f"Repository error while fetching persona: {str(e)}")
            raise

    def _create_and_save_persona(self, user_id: str) -> Persona:
        try:
            persona = self._create_default_persona(user_id)
            self.repository.save_persona(user_id, persona)
            logger.debug(
                f"Successfully created and saved persona for user_id: {user_id}"
            )
            return persona
        except Exception as e:
            logger.error(
                f"Failed to create/save persona for user_id {user_id}: {str(e)}"
            )
            raise

    def _create_default_persona(self, user_id: str) -> Persona:
        return Persona(
            user_id=user_id,
            openness=3.0,
            conscientiousness=3.0,
            extraversion=3.0,
            agreeableness=3.0,
            neuroticism=3.0,
        )