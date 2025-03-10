"""
Persona Model Module

This module defines the Persona domain model representing users' personality traits
based on the Five-Factor Model (Big Five): Openness, Conscientiousness, Extraversion,
Agreeableness, and Neuroticism. Each trait is normalized on a scale from 1.0 to 5.0.

The Persona class provides validation logic for trait boundaries, data conversion
utilities, and integrates with SQLAlchemy ORM for database persistence. This model
serves as the core domain entity for personality-based features in the system.
"""

from sqlalchemy import Column, Float, String
from sqlalchemy.ext.declarative import declarative_base

from adapters.loggers.logger_adapter import app_logger
from core.domain.exceptions import PersonaValidationError

Base = declarative_base()


class Persona(Base):
    """
    Represents a persona with personality traits.

    Attributes:
        user_id (str): Unique identifier for the persona.
        openness (float): Value for the openness trait.
        conscientiousness (float): Value for the conscientiousness trait.
        extraversion (float): Value for the extraversion trait.
        agreeableness (float): Value for the agreeableness trait.
        neuroticism (float): Value for the neuroticism trait.
    """

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
        """
        Initialize a Persona instance with the provided trait values.

        Args:
            user_id (str): The unique identifier for the persona.
            openness (float, optional): The openness trait value. Defaults to 3.0.
            conscientiousness (float, optional): The conscientiousness trait value. Defaults to 3.0.
            extraversion (float, optional): The extraversion trait value. Defaults to 3.0.
            agreeableness (float, optional): The agreeableness trait value. Defaults to 3.0.
            neuroticism (float, optional): The neuroticism trait value. Defaults to 3.0.

        Raises:
            PersonaValidationError: If any trait value is outside the allowed range.
        """
        self.user_id = user_id
        self.openness = openness
        self.conscientiousness = conscientiousness
        self.extraversion = extraversion
        self.agreeableness = agreeableness
        self.neuroticism = neuroticism
        self.validate_ranges()
        app_logger.info("Created valid Persona with traits: %s", self.to_dict())

    def validate_ranges(self) -> None:
        """
        Validates that all trait values are within the allowed range.

        Raises:
            PersonaValidationError: If any trait value is outside the allowed range.
        """
        invalid_traits = []
        for trait in self.TRAIT_NAMES:
            value = getattr(self, trait)
            if not self.MIN_TRAIT_VALUE <= value <= self.MAX_TRAIT_VALUE:
                invalid_traits.append(
                    (
                        f"{trait} ({value}) must be between {self.MIN_TRAIT_VALUE} "
                        f"and {self.MAX_TRAIT_VALUE}"
                    )
                )

        if invalid_traits:
            raise PersonaValidationError("; ".join(invalid_traits))

    def to_dict(self) -> dict:
        """
        Returns a dictionary representation of the Persona instance.

        Returns:
            dict: A dictionary containing the persona's attributes.
        """
        return {
            "user_id": self.user_id,
            "openness": self.openness,
            "conscientiousness": self.conscientiousness,
            "extraversion": self.extraversion,
            "agreeableness": self.agreeableness,
            "neuroticism": self.neuroticism,
        }
