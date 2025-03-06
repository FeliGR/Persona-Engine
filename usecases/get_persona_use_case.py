"""
Get Persona Use Case Module

This module implements the use case for retrieving an existing persona profile
by user ID. It enforces the business rules for persona retrieval and provides
proper error handling for cases when a persona cannot be found.

The use case acts as an intermediary between the controller and repository layers,
ensuring that domain rules are consistently applied when retrieving personas.
"""

from core.domain.exceptions import PersonaNotFoundError
from core.domain.persona_model import Persona
from core.interfaces.persona_repository_interface import IPersonaRepository
from core.interfaces.use_case_interfaces import IGetPersonaUseCase
from utils.logger import app_logger


class GetPersonaUseCase(IGetPersonaUseCase):
    """
    Use case implementation for retrieving a persona by user ID.

    This class implements the IGetPersonaUseCase interface, providing the business
    logic for retrieving existing personas from the repository. It performs basic
    input validation and handles the case when a persona cannot be found for the
    specified user ID.
    """

    def __init__(self, repository: IPersonaRepository):
        """
        Initialize the use case with a persona repository.

        Args:
            repository (IPersonaRepository): The repository for persona data access.
        """
        self.repository = repository

    def execute(self, user_id: str) -> Persona:
        """
        Execute the use case to retrieve a persona.

        Args:
            user_id (str): The unique identifier for the user.

        Returns:
            Persona: The retrieved persona entity.

        Raises:
            ValueError: If the user ID is empty or not a string.
            PersonaNotFoundError: If no persona exists for the given user ID.
        """
        if not user_id or not isinstance(user_id, str):
            raise ValueError("User ID must be a non-empty string")

        persona = self.repository.get_persona(user_id)

        if not persona:
            app_logger.info("No persona found for user_id: %s", user_id)
            raise PersonaNotFoundError(f"Persona not found for user_id: {user_id}")

        return persona
