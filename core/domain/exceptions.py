"""
Domain Exceptions Module

This module defines the custom exceptions used throughout the Persona Engine application.
It provides a hierarchy of exception types to handle different error scenarios:

- Domain errors: Base exceptions for domain-specific failures
- Validation errors: For input and entity validation failures
- Repository errors: For data access and persistence issues

These exceptions help maintain clear error boundaries between application layers
and provide specific error handling for domain-related operations.
"""


class DomainError(Exception):
    """Base class for domain-related errors."""


class ValidationError(DomainError):
    """Base class for validation errors within the domain."""


class TraitNotFoundError(ValidationError):
    """Raised when a requested trait is not found."""


class TraitValidationError(ValidationError):
    """Raised when a trait's value is invalid."""


class PersonaValidationError(ValidationError, ValueError):
    """Raised when persona validation fails."""


class PersonaNotFoundError(DomainError):
    """Raised when a persona is not found."""


class PersonaRepositoryError(Exception):
    """Base class for persona repository-related errors."""


class DatabaseError(PersonaRepositoryError):
    """Raised for database-related errors in the repository."""
