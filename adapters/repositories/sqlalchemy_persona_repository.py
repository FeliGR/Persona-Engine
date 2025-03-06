"""
This module provides an implementation of the IPersonaRepository interface using SQLAlchemy.

It defines the SQLAlchemyPersonaRepository class, which handles database operations
for persona entities.
"""

from contextlib import contextmanager
from typing import List, Optional

from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker

from core.domain.exceptions import DatabaseError
from core.domain.persona_model import Base, Persona
from core.interfaces.persona_repository_interface import IPersonaRepository
from utils.logger import logger


class SQLAlchemyPersonaRepository(IPersonaRepository):
    """
    SQLAlchemyPersonaRepository implements the IPersonaRepository interface using SQLAlchemy
    for ORM-based persistence.

    Attributes:
        engine: The SQLAlchemy engine instance.
        session_factory: A sessionmaker configured to interact with the database.
    """

    def __init__(self, db_uri: str, echo: bool = False):
        self.engine = create_engine(db_uri, echo=echo)
        self.session_factory = sessionmaker(bind=self.engine, expire_on_commit=False)
        Base.metadata.create_all(self.engine)
        logger.info("Database schema initialized successfully using ORM")

    @contextmanager
    def _session_scope(self):
        """
        Provide a transactional scope around a series of operations.

        Yields:
            A SQLAlchemy session object.

        Raises:
            DatabaseError: If a SQLAlchemyError occurs during the transaction.
        """
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except exc.SQLAlchemyError as e:
            session.rollback()
            logger.error("Database transaction failed: %s", e, exc_info=True)
            raise DatabaseError(f"Database operation failed: {e}") from e
        finally:
            session.close()

    def get_persona(self, user_id: str) -> Optional[Persona]:
        """
        Retrieve a persona from the database based on the provided user_id.

        Args:
            user_id (str): The unique identifier for the persona.

        Returns:
            Optional[Persona]: The persona instance if found, otherwise None.
        """
        logger.debug("Retrieving persona for user_id: %s", user_id)
        with self._session_scope() as session:
            persona = session.query(Persona).filter_by(user_id=user_id).first()
            if persona:
                logger.info("Persona found for user_id: %s", user_id)
                return persona
            logger.info("No persona found for user_id: %s", user_id)
            return None

    def save_persona(self, user_id: str, persona: Persona) -> None:
        """
        Save or update a persona in the database.

        Args:
            user_id (str): The unique identifier for the persona.
            persona (Persona): The persona object to be saved.

        Raises:
            ValueError: If user_id is empty or persona is not a valid Persona instance.
        """
        if not user_id:
            raise ValueError("User ID cannot be empty")
        if not isinstance(persona, Persona):
            raise ValueError("Invalid persona object")
        logger.debug("Saving persona for user_id: %s", user_id)
        with self._session_scope() as session:
            session.merge(persona)
            session.flush()
            logger.info("Persona saved successfully for user_id: %s", user_id)

    def list_personas(self, limit: int = 100, offset: int = 0) -> List[tuple]:
        """
        List personas from the database with pagination.

        Args:
            limit (int): Maximum number of personas to retrieve. Defaults to 100.
            offset (int): Number of personas to skip. Defaults to 0.

        Returns:
            List[tuple]: A list of tuples, where each tuple contains the user_id
            and the corresponding Persona object.
        """
        logger.debug("Listing personas with limit=%s, offset=%s", limit, offset)
        with self._session_scope() as session:
            personas = session.query(Persona).offset(offset).limit(limit).all()
            logger.info("Retrieved %s personas", len(personas))
            return [(p.user_id, p) for p in personas]
