from utils.logger import logger
from core.domain.persona_model import Persona
from usecases.persona_repository_interface import IPersonaRepository
from core.persona_domain_service import PersonaDomainService

class UpdatePersonaUseCase:
    def __init__(self, repository: IPersonaRepository):
        self.repository = repository

    def execute(self, user_id: str, trait_name: str, new_value: float) -> Persona:
        self._validate_inputs(user_id, trait_name, new_value)
        logger.info(f"Updating trait '{trait_name}' for user '{user_id}'")

        persona = self.repository.get_persona(user_id)
        if persona is None:
            logger.info(f"No persona found for user_id: {user_id}")
            raise ValueError(f"No persona found for user '{user_id}'")

        updated_persona = PersonaDomainService.update_trait(
            persona, trait_name, new_value
        )

        self.repository.save_persona(user_id, updated_persona)

        refreshed_persona = self.repository.get_persona(user_id)
        logger.info(f"Successfully updated trait '{trait_name}' for user '{user_id}'")

        return refreshed_persona

    def _validate_inputs(self, user_id: str, trait_name: str, new_value: float) -> None:
        if not user_id:
            raise ValueError("User ID cannot be empty")
        if not trait_name:
            raise ValueError("Trait name cannot be empty")
        if not isinstance(new_value, (int, float)):
            raise ValueError("Trait value must be a number")
