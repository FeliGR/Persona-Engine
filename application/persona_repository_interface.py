from abc import ABC, abstractmethod
from typing import List, Tuple

from core.domain.persona_model import Persona


class IPersonaRepository(ABC):

    @abstractmethod
    def get_persona(self, user_id: str) -> Persona:

        pass

    @abstractmethod
    def save_persona(self, user_id: str, persona: Persona) -> None:

        pass

    @abstractmethod
    def list_personas(
        self, limit: int = 100, offset: int = 0
    ) -> List[Tuple[str, Persona]]:

        pass
