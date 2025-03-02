from abc import ABC, abstractmethod
from typing import Optional, List
from core.persona_model import Persona


class PersonaRepositoryError(Exception):

    pass


class IPersonaRepository(ABC):

    @abstractmethod
    def get_persona(self, user_id: str) -> Persona:

        pass

    @abstractmethod
    def save_persona(self, user_id: str, persona: Persona) -> None:

        pass

    @abstractmethod
    def delete_persona(self, user_id: str) -> None:

        pass

    @abstractmethod
    def list_personas(self, limit: int = 100, offset: int = 0) -> List[Persona]:

        pass
