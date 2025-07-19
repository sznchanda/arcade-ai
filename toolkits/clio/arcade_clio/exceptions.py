"""Custom exceptions for the Clio toolkit."""

from arcade_tdk.errors import ToolExecutionError


class ClioError(ToolExecutionError):
    """Base exception for Clio-related errors."""

    def __init__(self, message: str, *, retry: bool = False) -> None:
        super().__init__(message=message, developer_message=message, retry=retry)


class ClioAuthenticationError(ClioError):
    """Raised when authentication with Clio fails."""

    def __init__(self, message: str = "Authentication failed") -> None:
        super().__init__(message=message, retry=False)


class ClioPermissionError(ClioError):
    """Raised when the user lacks required permissions."""

    def __init__(self, message: str = "Insufficient permissions") -> None:
        super().__init__(message=message, retry=False)


class ClioResourceNotFoundError(ClioError):
    """Raised when a requested resource is not found."""

    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message=message, retry=False)


class ClioRateLimitError(ClioError):
    """Raised when API rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded") -> None:
        super().__init__(message=message, retry=True)


class ClioValidationError(ClioError):
    """Raised when request validation fails."""

    def __init__(self, message: str = "Validation error") -> None:
        super().__init__(message=message, retry=False)


class ClioServerError(ClioError):
    """Raised when the Clio server returns a 5xx error."""

    def __init__(self, message: str = "Server error") -> None:
        super().__init__(message=message, retry=True)


class ClioTimeoutError(ClioError):
    """Raised when a request to Clio times out."""

    def __init__(self, message: str = "Request timeout") -> None:
        super().__init__(message=message, retry=True)
