"""
Use Case Interfaces Module

This module defines the abstract interfaces for application use cases related to personas.
These interfaces establish the required contracts for the core application logic,
separating business rules from external concerns like UI and data storage.

Each use case interface represents a specific operation that the application can perform,
encapsulating business rules and application-specific logic while depending only on
the domain model and other interfaces.
"""

from abc import ABC, abstractmethod

from core.domain.persona_model import Persona


class IGetPersonaUseCase(ABC):
    """
    Abstract interface for the get persona use case.

    This use case handles retrieving an existing persona by user ID.
    It enforces the business rules for persona retrieval and handles
    appropriate error cases when a persona cannot be found.
    """

    @abstractmethod
    def execute(self, user_id: str) -> Persona:
        """
        Execute the use case to retrieve a persona.

        Args:
            user_id (str): The unique identifier for the user.

        Returns:
            Persona: The retrieved persona entity.

        Raises:
            PersonaNotFoundError: If no persona exists for the given user ID.
        """


class IGetOrCreatePersonaUseCase(ABC):
    """
    Abstract interface for the get or create persona use case.

    This use case handles retrieving an existing persona by user ID or
    creating a new one if it doesn't exist. This ensures every user
    will have a persona profile available.
    """

    @abstractmethod
    def execute(self, user_id: str) -> Persona:
        """
        Execute the use case to get an existing persona or create a new one.

        Args:
            user_id (str): The unique identifier for the user.

        Returns:
            Persona: The retrieved or newly created persona entity.
        """


class IUpdatePersonaUseCase(ABC):
    """
    Abstract interface for the update persona use case.

    This use case handles updating a specific trait in an existing persona.
    It enforces the business rules for trait updates and ensures the
    persona remains valid after the change.
    """

    @abstractmethod
    def execute(self, user_id: str, trait_name: str, new_value: float) -> Persona:
        """
        Execute the use case to update a persona trait.

        Args:
            user_id (str): The unique identifier for the user.
            trait_name (str): The name of the trait to update.
            new_value (float): The new value to set for the trait.

        Returns:
            Persona: The updated persona entity.

        Raises:
            PersonaNotFoundError: If no persona exists for the given user ID.
            TraitNotFoundError: If the specified trait doesn't exist.
            TraitValidationError: If the trait value is invalid.
        """
