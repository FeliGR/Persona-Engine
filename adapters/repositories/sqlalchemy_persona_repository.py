from contextlib import contextmanager
from typing import Optional, Dict, Any
from sqlalchemy import create_engine, Column, String, Float, MetaData, Table, exc
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from typing import List

from application.persona_repository_interface import IPersonaRepository
from core.persona_model import Persona
from utils.logger import logger


class DatabaseError(Exception):

    pass


class SQLAlchemyPersonaRepository(IPersonaRepository):

    def __init__(self, db_uri: str, echo: bool = False, pool_size: int = 5):
        self.engine = self._create_engine(db_uri, echo, pool_size)
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
            logger.critical(f"Failed to create database engine: {str(e)}")
            raise DatabaseError(f"Database initialization failed: {str(e)}")

    def _setup_schema(self) -> None:
        metadata = MetaData()

        self.personas_table = Table(
            "personas",
            metadata,
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

        try:
            metadata.create_all(self.engine)
            logger.info("Database schema initialized successfully")
        except exc.SQLAlchemyError as e:
            logger.error(f"Schema initialization failed: {str(e)}")
            raise DatabaseError(f"Failed to initialize database schema: {str(e)}")

    @contextmanager
    def _session_scope(self):
        session = self.Session()
        try:
            yield session
            session.commit()
        except exc.SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database transaction failed: {str(e)}")
            raise DatabaseError(f"Database operation failed: {str(e)}")
        finally:
            session.close()

    def get_persona(self, user_id: str) -> Optional[Persona]:
        logger.debug(f"Retrieving persona for user_id: {user_id}")

        try:
            with self._session_scope() as session:
                result = (
                    session.query(self.personas_table)
                    .filter_by(user_id=user_id)
                    .first()
                )

                if result:
                    logger.info(f"Persona found for user_id: {user_id}")
                    return Persona(
                        openness=result.openness,
                        conscientiousness=result.conscientiousness,
                        extraversion=result.extraversion,
                        agreeableness=result.agreeableness,
                        neuroticism=result.neuroticism,
                    )

                logger.info(f"No persona found for user_id: {user_id}")
                return None

        except DatabaseError:

            raise
        except Exception as e:
            logger.error(
                f"Unexpected error retrieving persona: {str(e)}", exc_info=True
            )
            raise DatabaseError(f"Failed to retrieve persona: {str(e)}")

    def save_persona(self, user_id: str, persona: Persona) -> None:
        if not user_id:
            raise ValueError("User ID cannot be empty")

        if not isinstance(persona, Persona):
            raise ValueError("Invalid persona object")

        persona_data = self._persona_to_dict(persona)
        logger.debug(f"Saving persona for user_id: {user_id}")

        try:
            with self._session_scope() as session:
                self._save_or_update_persona(session, user_id, persona_data)
                logger.info(f"Persona saved successfully for user_id: {user_id}")
        except DatabaseError:

            raise
        except Exception as e:
            logger.error(f"Unexpected error saving persona: {str(e)}", exc_info=True)
            raise DatabaseError(f"Failed to save persona: {str(e)}")

    def delete_persona(self, user_id: str) -> None:
        if not user_id:
            raise ValueError("User ID cannot be empty")

        logger.debug(f"Deleting persona for user_id: {user_id}")

        try:
            with self._session_scope() as session:
                result = (
                    session.query(self.personas_table)
                    .filter_by(user_id=user_id)
                    .delete()
                )
                if result == 0:
                    logger.warning(f"No persona found to delete for user_id: {user_id}")
                    raise DatabaseError(f"Persona not found for user_id: {user_id}")

                logger.info(f"Deleted persona for user_id: {user_id}")
        except DatabaseError:

            raise
        except Exception as e:
            logger.error(f"Unexpected error deleting persona: {str(e)}", exc_info=True)
            raise DatabaseError(f"Failed to delete persona: {str(e)}")

    def list_personas(self, limit: int = 100, offset: int = 0) -> List[Persona]:
        logger.debug(f"Listing personas with limit={limit}, offset={offset}")

        try:
            with self._session_scope() as session:
                results = (
                    session.query(self.personas_table).limit(limit).offset(offset).all()
                )

                personas = []
                for result in results:
                    personas.append(
                        Persona(
                            openness=result.openness,
                            conscientiousness=result.conscientiousness,
                            extraversion=result.extraversion,
                            agreeableness=result.agreeableness,
                            neuroticism=result.neuroticism,
                        )
                    )

                logger.info(f"Retrieved {len(personas)} personas")
                return personas
        except DatabaseError:

            raise
        except Exception as e:
            logger.error(f"Unexpected error listing personas: {str(e)}", exc_info=True)
            raise DatabaseError(f"Failed to list personas: {str(e)}")

    def _persona_to_dict(self, persona: Persona) -> Dict[str, float]:
        return {
            "openness": persona.openness,
            "conscientiousness": persona.conscientiousness,
            "extraversion": persona.extraversion,
            "agreeableness": persona.agreeableness,
            "neuroticism": persona.neuroticism,
        }

    def _save_or_update_persona(
        self, session: Session, user_id: str, persona_data: Dict[str, Any]
    ) -> None:

        existing = session.query(self.personas_table).filter_by(user_id=user_id).first()

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
