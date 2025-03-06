"""
Persona Controller Interface Module

This module defines the abstract interface for persona controllers in the application.
The IPersonaController interface establishes the required contract for any controller
implementation that handles persona-related operations, ensuring consistent API behavior
across different adapters.

This interface defines the standard operations for retrieving, creating, and updating
persona profiles while abstracting away the specific transport protocols or frameworks used.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple

ResponseType = Tuple[Dict[str, Any], int]


class IPersonaController(ABC):
    """
    Abstract interface for persona controller implementations.

    This interface defines the required methods for controllers that handle
    persona-related API operations. Any concrete controller implementation must
    provide functionality for retrieving, creating, and updating personas while
    maintaining consistent response formats.
    """

    @abstractmethod
    def get_persona(self, user_id: str) -> ResponseType:
        """
        Retrieve a persona by user ID.

        Args:
            user_id (str): The unique identifier for the user.

        Returns:
            ResponseType: A tuple containing the response data and HTTP status code.
        """

    @abstractmethod
    def create_persona(self) -> ResponseType:
        """
        Create a new persona.

        Returns:
            ResponseType: A tuple containing the response data and HTTP status code.
        """

    @abstractmethod
    def update_persona(self, user_id: str) -> ResponseType:
        """
        Update an existing persona.

        Args:
            user_id (str): The unique identifier for the user.

        Returns:
            ResponseType: A tuple containing the response data and HTTP status code.
        """
