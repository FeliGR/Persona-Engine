"""
Persona Domain Service Interface Module

This module defines the abstract interface for persona domain services in the application.
The IPersonaDomainService interface establishes the required contract for any service
implementation that handles persona-related domain operations, ensuring consistent
behavior and business rule enforcement.

Domain services encapsulate business logic that doesn't naturally fit within entities,
providing operations that work across multiple aggregates or require domain-specific logic.
"""

from abc import ABC, abstractmethod

from core.domain.persona_model import Persona


class IPersonaDomainService(ABC):
    """
    Abstract interface for persona domain service implementations.

    This interface defines methods for domain operations on personas that involve
    business rules and logic. Any concrete domain service implementation must provide
    functionality that enforces domain integrity and business rules when manipulating
    persona entities.
    """

    @abstractmethod
    def update_trait(
        self, persona: Persona, trait_name: str, new_value: float
    ) -> Persona:
        """
        Update a specific trait value in a persona.

        This method validates and updates the specified trait with the new value,
        ensuring all domain rules regarding trait values are enforced.

        Args:
            persona (Persona): The persona entity to update.
            trait_name (str): The name of the trait to update.
            new_value (float): The new value to set for the trait.

        Returns:
            Persona: The updated persona entity.

        Raises:
            TraitNotFoundError: If the specified trait doesn't exist.
            TraitValidationError: If the trait value is invalid.
        """
