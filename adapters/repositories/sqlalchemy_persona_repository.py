from contextlib import contextmanager
from typing import Optional, Dict, Any, List

from sqlalchemy import (
    create_engine,
    Column,
    String,
    Float,
    MetaData,
    Table,
    exc,
    select,
)
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

from usecases.persona_repository_interface import IPersonaRepository
from core.domain.exceptions import DatabaseError
from core.domain.persona_model import Persona
from utils.logger import logger


class SQLAlchemyPersonaRepository(IPersonaRepository):
    def __init__(self, db_uri: str, echo: bool = False, pool_size: int = 5):
        self.engine = self._create_engine(db_uri, echo, pool_size)
        self.metadata = MetaData()  # cache metadata as an instance attribute
        self.personas_table = self._define_personas_table()
        self._setup_schema()
        self.Session = sessionmaker(bind=self.engine)

    def _create_engine(self, db_uri: str, echo: bool, pool_size: int) -> Engine:
        try:
            return create_engine(
                db_uri,
                echo=echo,
                poolclass=QueuePool,
                pool_size=pool_size,
                max_overflow=10,
                pool_timeout=30,
                pool_recycle=3600,
            )
        except Exception as e:
            logger.critical(f"Failed to create database engine: {e}")
            raise DatabaseError(f"Database initialization failed: {e}")

    def _define_personas_table(self) -> Table:
        return Table(
            "personas",
            self.metadata,
            Column(
                "user_id",
                String(36),
                primary_key=True,
                nullable=False,
                comment="Unique user identifier",
            ),
            Column(
                "openness",
                Float,
                nullable=False,
                comment="Openness personality trait score",
            ),
            Column(
                "conscientiousness",
                Float,
                nullable=False,
                comment="Conscientiousness personality trait score",
            ),
            Column(
                "extraversion",
                Float,
                nullable=False,
                comment="Extraversion personality trait score",
            ),
            Column(
                "agreeableness",
                Float,
                nullable=False,
                comment="Agreeableness personality trait score",
            ),
            Column(
                "neuroticism",
                Float,
                nullable=False,
                comment="Neuroticism personality trait score",
            ),
        )

    def _setup_schema(self) -> None:
        try:
            self.metadata.create_all(self.engine)
            logger.info("Database schema initialized successfully")
        except exc.SQLAlchemyError as e:
            logger.error(f"Schema initialization failed: {e}")
            raise DatabaseError(f"Failed to initialize database schema: {e}")

    @contextmanager
    def _session_scope(self):
        session = self.Session()
        try:
            yield session
            session.commit()
        except exc.SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database transaction failed: {e}")
            raise DatabaseError(f"Database operation failed: {e}")
        finally:
            session.close()

    def _row_to_persona(self, row: Any) -> Persona:
        return Persona(
            openness=row.openness,
            conscientiousness=row.conscientiousness,
            extraversion=row.extraversion,
            agreeableness=row.agreeableness,
            neuroticism=row.neuroticism,
        )

    def get_persona(self, user_id: str) -> Optional[Persona]:
        logger.debug(f"Retrieving persona for user_id: {user_id}")
        with self._session_scope() as session:
            try:
                stmt = select(self.personas_table).where(
                    self.personas_table.c.user_id == user_id
                )
                result = session.execute(stmt).first()
                if result:
                    logger.info(f"Persona found for user_id: {user_id}")
                    # result may be a tuple so we take the first element
                    persona_row = result[0] if isinstance(result, tuple) else result
                    return self._row_to_persona(persona_row)
                logger.info(f"No persona found for user_id: {user_id}")
                return None
            except exc.SQLAlchemyError as e:
                logger.error(f"Error retrieving persona: {e}", exc_info=True)
                raise DatabaseError(f"Failed to retrieve persona: {e}")

    def save_persona(self, user_id: str, persona: Persona) -> None:
        if not user_id:
            raise ValueError("User ID cannot be empty")

        if not isinstance(persona, Persona):
            raise ValueError("Invalid persona object")

        persona_data: Dict[str, Any] = persona.to_dict(include_user_id=False)
        logger.debug(f"Saving persona for user_id: {user_id}")

        with self._session_scope() as session:
            try:
                self._save_or_update_persona(session, user_id, persona_data)
                logger.info(f"Persona saved successfully for user_id: {user_id}")
            except exc.SQLAlchemyError as e:
                logger.error(f"Error saving persona: {e}", exc_info=True)
                raise DatabaseError(f"Failed to save persona: {e}")

    def list_personas(self, limit: int = 100, offset: int = 0) -> List[tuple]:
        logger.debug(f"Listing personas with limit={limit}, offset={offset}")
        with self._session_scope() as session:
            try:
                stmt = select(self.personas_table).limit(limit).offset(offset)
                results = session.execute(stmt).all()
                personas = []
                for row in results:
                    record = row[0] if isinstance(row, tuple) else row
                    personas.append((record.user_id, self._row_to_persona(record)))
                logger.info(f"Retrieved {len(personas)} personas")
                return personas
            except exc.SQLAlchemyError as e:
                logger.error(f"Error listing personas: {e}", exc_info=True)
                raise DatabaseError(f"Failed to list personas: {e}")

    def _save_or_update_persona(
        self, session: Session, user_id: str, persona_data: Dict[str, Any]
    ) -> None:
        stmt = select(self.personas_table).where(
            self.personas_table.c.user_id == user_id
        )
        existing = session.execute(stmt).first()
        if existing:
            session.query(self.personas_table).filter_by(user_id=user_id).update(
                persona_data
            )
            logger.debug(f"Updated existing persona for user_id: {user_id}")
        else:
            session.execute(
                self.personas_table.insert().values(user_id=user_id, **persona_data)
            )
            logger.debug(f"Inserted new persona for user_id: {user_id}")
