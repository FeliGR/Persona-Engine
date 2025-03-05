from utils.logger import logger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Float
from core.domain.exceptions import PersonaValidationError

Base = declarative_base()


class Persona(Base):
    __tablename__ = "personas"

    user_id = Column(String(36), primary_key=True, nullable=False)
    openness = Column(Float, nullable=False, default=3.0)
    conscientiousness = Column(Float, nullable=False, default=3.0)
    extraversion = Column(Float, nullable=False, default=3.0)
    agreeableness = Column(Float, nullable=False, default=3.0)
    neuroticism = Column(Float, nullable=False, default=3.0)

    MIN_TRAIT_VALUE = 1.0
    MAX_TRAIT_VALUE = 5.0
    TRAIT_NAMES = (
        "openness",
        "conscientiousness",
        "extraversion",
        "agreeableness",
        "neuroticism",
    )

    def __init__(
        self,
        user_id: str,
        openness: float = 3.0,
        conscientiousness: float = 3.0,
        extraversion: float = 3.0,
        agreeableness: float = 3.0,
        neuroticism: float = 3.0,
    ):
        self.user_id = user_id
        self.openness = openness
        self.conscientiousness = conscientiousness
        self.extraversion = extraversion
        self.agreeableness = agreeableness
        self.neuroticism = neuroticism
        self.validate_ranges()
        logger.info(f"Created valid Persona with traits: {self.to_dict()}")

    def validate_ranges(self) -> None:
        invalid_traits = []
        for trait in self.TRAIT_NAMES:
            value = getattr(self, trait)
            if not (self.MIN_TRAIT_VALUE <= value <= self.MAX_TRAIT_VALUE):
                invalid_traits.append(
                    f"{trait} ({value}) must be between {self.MIN_TRAIT_VALUE} and {self.MAX_TRAIT_VALUE}"
                )
        if invalid_traits:
            raise PersonaValidationError("; ".join(invalid_traits))

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "openness": self.openness,
            "conscientiousness": self.conscientiousness,
            "extraversion": self.extraversion,
            "agreeableness": self.agreeableness,
            "neuroticism": self.neuroticism,
        }
