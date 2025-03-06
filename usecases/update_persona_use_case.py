"""
Update Persona Use Case Module

This module implements the use case for updating specific traits in an existing
persona profile. It enforces the business rules for trait modifications and
ensures that all changes to persona traits follow domain validation rules.

The use case coordinates between the controller, domain service, and repository layers,
maintaining separation of concerns while ensuring that domain rules are consistently
applied when modifying persona traits.
"""

from core.domain.persona_model import Persona
from core.interfaces.persona_repository_interface import IPersonaRepository
from core.interfaces.use_case_interfaces import IUpdatePersonaUseCase
from core.services.persona_domain_service import PersonaDomainService
from utils.logger import app_logger


class UpdatePersonaUseCase(IUpdatePersonaUseCase):
    """
    Use case implementation for updating persona traits.

    This class implements the IUpdatePersonaUseCase interface, providing the business
    logic for modifying trait values on existing personas. It validates inputs,
    coordinates with domain services to apply changes according to domain rules,
    and persists the updated personas through the repository.
    """

    def __init__(self, repository: IPersonaRepository):
        """
        Initialize the use case with a persona repository.

        Args:
            repository (IPersonaRepository): The repository for persona data access.

        Raises:
            ValueError: If the repository is None.
        """
        if not repository:
            raise ValueError("Repository cannot be None")
        self.repository = repository
        self.persona_domain_service = PersonaDomainService()

    def execute(self, user_id: str, trait_name: str, new_value: float) -> Persona:
        """
        Execute the use case to update a specific trait in a persona.

        Args:
            user_id (str): The unique identifier for the user.
            trait_name (str): The name of the trait to update.
            new_value (float): The new value to set for the trait.

        Returns:
            Persona: The updated persona entity.

        Raises:
            ValueError: If inputs are invalid or no persona exists for the user.
            TraitNotFoundError: If the specified trait doesn't exist.
            TraitValidationError: If the trait value is invalid.
        """
        self._validate_inputs(user_id, trait_name, new_value)
        app_logger.info("Updating trait '%s' for user '%s'", trait_name, user_id)

        persona = self.repository.get_persona(user_id)
        if persona is None:
            app_logger.info("No persona found for user_id: %s", user_id)
            raise ValueError(f"No persona found for user '{user_id}'")

        updated_persona = self.persona_domain_service.update_trait(
            persona, trait_name, new_value
        )

        self.repository.save_persona(user_id, updated_persona)

        refreshed_persona = self.repository.get_persona(user_id)
        app_logger.info(
            "Successfully updated trait '%s' for user '%s'", trait_name, user_id
        )

        return refreshed_persona

    def _validate_inputs(self, user_id: str, trait_name: str, new_value: float) -> None:
        """
        Validate the inputs for the update operation.

        Args:
            user_id (str): The unique identifier for the user.
            trait_name (str): The name of the trait to update.
            new_value (float): The new value to set for the trait.

        Raises:
            ValueError: If any of the inputs are invalid.
        """
        if not user_id:
            raise ValueError("User ID cannot be empty")
        if not trait_name:
            raise ValueError("Trait name cannot be empty")
        if not isinstance(new_value, (int, float)):
            raise ValueError("Trait value must be a number")
