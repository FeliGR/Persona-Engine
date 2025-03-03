class DomainError(Exception):
    """Base class for domain-related errors."""

    pass


class ValidationError(DomainError):
    """Base class for validation errors within the domain."""

    pass


class TraitNotFoundError(ValidationError):
    """Raised when a requested trait is not found."""

    pass


class TraitValidationError(ValidationError):
    """Raised when a trait's value is invalid."""

    pass


class PersonaValidationError(ValidationError, ValueError):
    """Raised when persona validation fails."""

    pass


class PersonaNotFoundError(DomainError):
    """Raised when a persona is not found."""

    pass


class PersonaRepositoryError(Exception):
    """Base class for persona repository-related errors."""

    pass


class DatabaseError(PersonaRepositoryError):
    """Raised for database-related errors in the repository."""

    pass
