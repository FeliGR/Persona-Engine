import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, ClassVar, Tuple
from core.exceptions import TraitValidationError, TraitNotFoundError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PersonaValidationError(ValueError):

    pass


@dataclass
class Persona:

    MIN_TRAIT_VALUE: ClassVar[float] = 1.0
    MAX_TRAIT_VALUE: ClassVar[float] = 5.0
    TRAIT_NAMES: ClassVar[Tuple[str, ...]] = (
        "openness",
        "conscientiousness",
        "extraversion",
        "agreeableness",
        "neuroticism",
    )

    openness: float = 3.0
    conscientiousness: float = 3.0
    extraversion: float = 3.0
    agreeableness: float = 3.0
    neuroticism: float = 3.0

    metadata: Dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        try:
            self.validate_ranges()
            logger.info(f"Created valid Persona with traits: {self.to_dict()}")
        except PersonaValidationError as e:
            logger.error(f"Failed to create valid Persona: {str(e)}")
            raise

    def validate_ranges(self) -> None:
        invalid_traits = []

        for trait_name in self.TRAIT_NAMES:
            trait_value = getattr(self, trait_name)
            if not isinstance(trait_value, (int, float)):
                invalid_traits.append(
                    f"{trait_name} must be a number, got {type(trait_value).__name__}"
                )
            elif (
                trait_value < self.MIN_TRAIT_VALUE or trait_value > self.MAX_TRAIT_VALUE
            ):
                invalid_traits.append(
                    f"{trait_name} ({trait_value}) must be between "
                    f"{self.MIN_TRAIT_VALUE} and {self.MAX_TRAIT_VALUE}"
                )

        if invalid_traits:
            error_msg = "; ".join(invalid_traits)
            raise PersonaValidationError(error_msg)

    def to_dict(self) -> Dict[str, float]:
        return {trait: getattr(self, trait) for trait in self.TRAIT_NAMES}
