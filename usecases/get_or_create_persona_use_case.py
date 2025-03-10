"""
Get or Create Persona Use Case Module

This module implements the use case for retrieving an existing persona profile
or creating a new one if it doesn't exist. This ensures that every user will
have a persona profile available when requested.

The use case acts as an intermediary between the controller and repository layers,
encapsulating the business logic for persona retrieval and creation while maintaining
separation of concerns between the application layers.
"""

from typing import Optional

from adapters.loggers.logger_adapter import app_logger
from core.domain.persona_model import Persona
from core.interfaces.persona_repository_interface import IPersonaRepository
from core.interfaces.use_case_interfaces import IGetOrCreatePersonaUseCase


class GetOrCreatePersonaUseCase(IGetOrCreatePersonaUseCase):
    """
    Use case implementation for retrieving or creating a persona.

    This class implements the IGetOrCreatePersonaUseCase interface, providing
    the business logic for retrieving existing personas from the repository or
    creating new ones with default values when necessary. This ensures that
    every user has a valid persona profile available.
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

    def execute(self, user_id: str) -> Persona:
        """
        Retrieves an existing Persona or creates a new one if none exists.

        Args:
            user_id (str): The unique user ID.

        Returns:
            Persona: The retrieved or newly created Persona.

        Raises:
            ValueError: If the user_id is invalid.
        """
        if not user_id or not isinstance(user_id, str):
            app_logger.error("Invalid user_id provided: %r", user_id)
            raise ValueError("User ID must be a non-empty string")

        try:
            app_logger.debug("Retrieving persona for user_id: %s", user_id)
            persona = self._get_persona(user_id)

            if not persona:
                app_logger.info(
                    "No persona found for user_id: %s. Creating new persona.", user_id
                )
                persona = self._create_and_save_persona(user_id)

            return persona

        except Exception as e:
            app_logger.error(
                "Error in GetOrCreatePersonaUseCase for user_id %s: %s", user_id, str(e)
            )
            raise

    def _get_persona(self, user_id: str) -> Optional[Persona]:
        """
        Fetches a Persona from the repository.

        Args:
            user_id (str): The unique user ID.

        Returns:
            Optional[Persona]: The retrieved Persona or None if not found.
        """
        try:
            return self.repository.get_persona(user_id)
        except Exception as e:
            app_logger.error("Repository error while fetching persona: %s", str(e))
            raise

    def _create_and_save_persona(self, user_id: str) -> Persona:
        """
        Creates and saves a new default Persona.

        Args:
            user_id (str): The unique user ID.

        Returns:
            Persona: The newly created Persona.
        """
        try:
            persona = self._create_default_persona(user_id)
            self.repository.save_persona(user_id, persona)
            app_logger.debug(
                "Successfully created and saved persona for user_id: %s", user_id
            )
            return persona
        except Exception as e:
            app_logger.error(
                "Failed to create/save persona for user_id %s: %s", user_id, str(e)
            )
            raise

    def _create_default_persona(self, user_id: str) -> Persona:
        """
        Creates a Persona with default trait values.

        Args:
            user_id (str): The unique user ID.

        Returns:
            Persona: The newly created Persona instance.
        """
        return Persona(
            user_id=user_id,
            openness=3.0,
            conscientiousness=3.0,
            extraversion=3.0,
            agreeableness=3.0,
            neuroticism=3.0,
        )
