from contextlib import contextmanager
from typing import Optional, List
from utils.logger import logger

from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker

from core.domain.persona_model import Persona, Base
from core.domain.exceptions import DatabaseError
from core.interfaces.persona_repository_interface import IPersonaRepository
from utils.logger import logger


class SQLAlchemyPersonaRepository(IPersonaRepository):
    def __init__(self, db_uri: str, echo: bool = False):
        self.engine = create_engine(db_uri, echo=echo)
        self.Session = sessionmaker(bind=self.engine, expire_on_commit=False)
        Base.metadata.create_all(self.engine)
        logger.info("Database schema initialized successfully using ORM")

    @contextmanager
    def _session_scope(self):
        session = self.Session()
        try:
            yield session
            session.commit()
        except exc.SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database transaction failed: {e}", exc_info=True)
            raise DatabaseError(f"Database operation failed: {e}")
        finally:
            session.close()

    def get_persona(self, user_id: str) -> Optional[Persona]:
        logger.debug(f"Retrieving persona for user_id: {user_id}")
        with self._session_scope() as session:
            persona = session.query(Persona).filter_by(user_id=user_id).first()
            if persona:
                logger.info(f"Persona found for user_id: {user_id}")
                return persona
            logger.info(f"No persona found for user_id: {user_id}")
            return None

    def save_persona(self, user_id: str, persona: Persona) -> None:
        if not user_id:
            raise ValueError("User ID cannot be empty")
        if not isinstance(persona, Persona):
            raise ValueError("Invalid persona object")
        logger.debug(f"Saving persona for user_id: {user_id}")
        with self._session_scope() as session:
            merged_persona = session.merge(persona)
            session.flush()
            logger.info(f"Persona saved successfully for user_id: {user_id}")

    def list_personas(self, limit: int = 100, offset: int = 0) -> List[tuple]:
        logger.debug(f"Listing personas with limit={limit}, offset={offset}")
        with self._session_scope() as session:
            personas = session.query(Persona).offset(offset).limit(limit).all()
            logger.info(f"Retrieved {len(personas)} personas")
            return [(p.user_id, p) for p in personas]
