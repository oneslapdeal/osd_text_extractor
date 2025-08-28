class DomainException(Exception):
    """Base exception for domain layer errors."""

    pass


class TextLengthError(DomainException):
    """Raised when text length does not satisfy domain constraints."""

    pass
