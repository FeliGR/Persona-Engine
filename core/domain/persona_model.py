import logging
from dataclasses import dataclass, field
from typing import Any, Dict, ClassVar, Tuple

from core.domain.exceptions import PersonaValidationError


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
        for trait in self.TRAIT_NAMES:
            value = getattr(self, trait)
            if not isinstance(value, (int, float)):
                invalid_traits.append(
                    f"{trait} must be a number, got {type(value).__name__}"
                )
            elif not (self.MIN_TRAIT_VALUE <= value <= self.MAX_TRAIT_VALUE):
                invalid_traits.append(
                    f"{trait} ({value}) must be between {self.MIN_TRAIT_VALUE} and {self.MAX_TRAIT_VALUE}"
                )
        if invalid_traits:
            raise PersonaValidationError("; ".join(invalid_traits))

    def to_dict(self, include_user_id: bool = True) -> Dict[str, Any]:
        data = {trait: getattr(self, trait) for trait in self.TRAIT_NAMES}
        if include_user_id and hasattr(self, "user_id"):
            data["user_id"] = self.user_id
        return data
