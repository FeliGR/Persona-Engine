from utils.logger import logger
from core.domain.persona_model import Persona
from core.domain.exceptions import TraitNotFoundError

class PersonaDomainService:
    @classmethod
    def update_trait(
        cls, persona: Persona, trait_name: str, new_value: float
    ) -> Persona:
        if trait_name not in Persona.TRAIT_NAMES:
            logger.error(f"Trait '{trait_name}' not found on Persona")
            raise TraitNotFoundError(f"Trait '{trait_name}' not found on Persona.")

        setattr(persona, trait_name, new_value)
        persona.validate_ranges()
        logger.info(f"Successfully updated trait '{trait_name}' to {new_value}")
        return persona
