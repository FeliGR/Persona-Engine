class DomainError(Exception):

    pass


class ValidationError(DomainError):

    pass


class TraitNotFoundError(ValidationError):

    pass


class TraitValidationError(ValidationError):

    pass
