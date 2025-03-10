"""
Persona Domain Service Module

This module implements the domain service for persona-related business logic.
It provides the concrete implementation of the IPersonaDomainService interface,
enforcing domain rules and business logic for manipulating persona entities.

Domain services encapsulate complex business rules that don't naturally fit
within the entity models themselves, keeping the domain model focused and clean.
"""

from adapters.loggers.logger_adapter import app_logger
from core.domain.exceptions import TraitNotFoundError
from core.domain.persona_model import Persona
from core.interfaces.persona_domain_service_interface import \
    IPersonaDomainService


class PersonaDomainService(IPersonaDomainService):
    """
    Domain service implementation for persona-related business logic.

    This class provides methods that implement domain-specific operations and business
    rules for persona entities, ensuring that all manipulations follow the domain model
    constraints and validation rules.
    """

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
            TraitValidationError: If the trait value is invalid (raised by validate_ranges).
        """
        if trait_name not in Persona.TRAIT_NAMES:
            app_logger.error("Trait '%s' not found on Persona", trait_name)
            raise TraitNotFoundError(f"Trait '{trait_name}' not found on Persona.")

        setattr(persona, trait_name, new_value)
        persona.validate_ranges()
        app_logger.info("Successfully updated trait '%s' to %s", trait_name, new_value)
        return persona
