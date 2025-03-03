import logging
from typing import Dict, Any, Optional

from application.persona_repository_interface import IPersonaRepository
from core.persona_domain_service import PersonaDomainService
from core.domain.persona_model import Persona


logger = logging.getLogger(__name__)


class UpdatePersonaUseCase:

    def __init__(self, repository: IPersonaRepository):

        self.repository = repository

    def execute(
        self, user_id: str, trait_name: str, new_value: float
    ) -> Dict[str, Any]:

        try:

            self._validate_inputs(user_id, trait_name, new_value)

            logger.info(f"Updating trait '{trait_name}' for user '{user_id}'")

            persona = self._get_persona(user_id)

            updated_persona = self._apply_update(persona, trait_name, new_value)

            self._save_persona(user_id, updated_persona)

            logger.info(
                f"Successfully updated trait '{trait_name}' for user '{user_id}'"
            )
            return updated_persona

        except ValueError as e:
            logger.warning(f"Validation error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to update persona trait: {str(e)}", exc_info=True)
            raise RuntimeError(f"Persona trait update failed: {str(e)}") from e

    def _validate_inputs(self, user_id: str, trait_name: str, new_value: float) -> None:

        if not user_id:
            raise ValueError("User ID cannot be empty")
        if not trait_name:
            raise ValueError("Trait name cannot be empty")
        if not isinstance(new_value, (int, float)):
            raise ValueError("Trait value must be a number")

    def _get_persona(self, user_id: str) -> Optional[Persona]:
        try:
            return self.repository.get_persona(user_id)
        except Exception as e:
            logger.error(f"Repository error while fetching persona: {str(e)}")
            raise

    def _apply_update(
        self, persona: Dict[str, Any], trait_name: str, new_value: float
    ) -> Dict[str, Any]:

        return PersonaDomainService.update_trait(persona, trait_name, new_value)

    def _save_persona(self, user_id: str, persona: Dict[str, Any]) -> None:

        try:
            self.repository.save_persona(user_id, persona)
        except Exception as e:
            logger.error(f"Failed to save persona: {str(e)}")
            raise RuntimeError("Could not save updated persona") from e
