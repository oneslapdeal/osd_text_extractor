class InfrastructureException(Exception):
    """Base exception for infrastructure layer errors."""

    pass


class ExtractionError(InfrastructureException):
    """Raised when extraction process fails at the infrastructure layer."""

    pass
