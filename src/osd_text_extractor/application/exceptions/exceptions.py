class ApplicationException(Exception):
    """Base exception for application layer errors."""

    pass


class UnsupportedFormatError(ApplicationException):
    """Raised when provided content format is not supported by the app layer."""

    pass
