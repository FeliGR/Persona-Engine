"""
Persona Repository Interface Module

This module defines the abstract repository interface for persona persistence operations.
The IPersonaRepository interface establishes the required contract for any repository
implementation that handles persona data storage and retrieval, ensuring consistent
data access patterns across different storage mechanisms.

The repository pattern abstracts the data layer and provides a collection-like interface
for accessing domain objects, decoupling the domain model from the underlying data source.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple

from core.domain.persona_model import Persona


class IPersonaRepository(ABC):
    """
    Abstract interface for persona repository implementations.

    This interface defines the standard operations for persisting and retrieving
    persona entities. Any concrete repository implementation must provide functionality
    for storing, retrieving, and listing personas regardless of the underlying
    storage technology.
    """

    @abstractmethod
    def get_persona(self, user_id: str) -> Persona:
        """
        Retrieve a persona by user ID.

        Args:
            user_id (str): The unique identifier for the user.

        Returns:
            Persona: The retrieved persona entity.

        Raises:
            PersonaNotFoundError: If no persona exists for the given user ID.
            DatabaseError: If a data access error occurs.
        """

    @abstractmethod
    def save_persona(self, user_id: str, persona: Persona) -> None:
        """
        Save a persona entity for a specific user.

        If a persona already exists for the given user ID, it will be updated.
        Otherwise, a new persona entry will be created.

        Args:
            user_id (str): The unique identifier for the user.
            persona (Persona): The persona entity to save.

        Raises:
            DatabaseError: If a data access or persistence error occurs.
        """

    @abstractmethod
    def list_personas(
        self, limit: int = 100, offset: int = 0
    ) -> List[Tuple[str, Persona]]:
        """
        Retrieve a paginated list of personas.

        Args:
            limit (int, optional): Maximum number of personas to retrieve. Defaults to 100.
            offset (int, optional): Number of personas to skip. Defaults to 0.

        Returns:
            List[Tuple[str, Persona]]: A list of tuples containing user IDs and their corresponding
                                      persona entities.

        Raises:
            DatabaseError: If a data access error occurs.
        """
