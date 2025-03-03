import logging
import threading
from typing import Optional, Dict, List, Tuple

from application.persona_repository_interface import (
    IPersonaRepository,
    PersonaRepositoryError,
)
from core.domain.persona_model import Persona


class InMemoryPersonaRepository(IPersonaRepository):

    def __init__(self):
        self._storage: Dict[str, Persona] = {}
        self._lock = threading.RLock()
        self._logger = logging.getLogger(__name__)
        self._logger.debug("Initialized InMemoryPersonaRepository")

    def get_persona(self, user_id: str) -> Optional[Persona]:
        if not user_id:
            self._logger.error("Attempted to retrieve persona with empty user_id")
            raise ValueError("user_id cannot be empty or None")

        try:
            with self._lock:
                persona = self._storage.get(user_id)
                self._logger.debug(
                    f"Retrieved persona for user_id={user_id}: {'Found' if persona else 'Not found'}"
                )
                return persona
        except Exception as e:
            self._logger.exception(f"Error retrieving persona for user_id={user_id}")
            raise PersonaRepositoryError(f"Failed to retrieve persona: {str(e)}") from e

    def save_persona(self, user_id: str, persona: Persona) -> None:
        if not user_id:
            self._logger.error("Attempted to save persona with empty user_id")
            raise ValueError("user_id cannot be empty or None")

        if persona is None:
            self._logger.error(f"Attempted to save None persona for user_id={user_id}")
            raise ValueError("persona cannot be None")

        try:
            with self._lock:
                self._storage[user_id] = persona
                self._logger.debug(f"Saved persona for user_id={user_id}")
        except Exception as e:
            self._logger.exception(f"Error saving persona for user_id={user_id}")
            raise PersonaRepositoryError(f"Failed to save persona: {str(e)}") from e

    def list_personas(
        self, limit: int = 100, offset: int = 0
    ) -> List[Tuple[str, Persona]]:
        with self._lock:
            all_personas = list(self._storage.items())
            return all_personas[offset : offset + limit]
