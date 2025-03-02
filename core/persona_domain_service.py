import logging
from typing import Optional, Dict, Any
from core.persona_model import Persona
from core.exceptions import TraitNotFoundError, TraitValidationError


logger = logging.getLogger(__name__)


class PersonaDomainService:

    @classmethod
    def update_trait(
        cls, persona: Persona, trait_name: str, new_value: float
    ) -> Persona:

        logger.debug(
            f"Updating trait '{trait_name}' to {new_value} for persona: {persona.id}"
        )

        try:

            if not hasattr(persona, trait_name):
                logger.error(f"Trait '{trait_name}' not found on Persona")
                raise TraitNotFoundError(f"Trait '{trait_name}' not found on Persona.")

            previous_value = getattr(persona, trait_name)

            setattr(persona, trait_name, new_value)

            try:
                persona.validate_ranges()
                logger.info(
                    f"Successfully updated trait '{trait_name}' from {previous_value} to {new_value}"
                )
                return persona
            except Exception as e:
                logger.error(f"Validation error after updating trait: {str(e)}")

                setattr(persona, trait_name, previous_value)
                raise TraitValidationError(
                    f"Invalid value for trait '{trait_name}': {str(e)}"
                )

        except Exception as e:
            if not isinstance(e, (TraitNotFoundError, TraitValidationError)):
                logger.exception(f"Unexpected error updating trait: {str(e)}")
                raise
            raise

    @staticmethod
    def _create_snapshot(persona: Persona) -> Dict[str, Any]:

        return {key: getattr(persona, key) for key in vars(persona)}

    @staticmethod
    def _restore_snapshot(persona: Persona, snapshot: Dict[str, Any]) -> None:

        for key, value in snapshot.items():
            setattr(persona, key, value)
