"""Custom exception classes for eBay API errors."""


class EbayAPIError(Exception):
    """Base exception for all eBay API errors."""

    def __init__(self, message: str, status_code: int | None = None, response_data: dict | None = None):
        """
        Initialize eBay API error.

        Args:
            message: Error message
            status_code: HTTP status code if applicable
            response_data: Additional response data from API
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data


class AuthError(EbayAPIError):
    """Raised when authentication fails or credentials are invalid."""

    pass


class NotFoundError(EbayAPIError):
    """Raised when a requested resource is not found."""

    def __init__(self, message: str = "Resource not found", **kwargs):
        super().__init__(message, **kwargs)


class RateLimitExceeded(EbayAPIError):
    """Raised when API rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded", retry_after: int | None = None, **kwargs):
        """
        Initialize rate limit error.

        Args:
            message: Error message
            retry_after: Seconds to wait before retrying
            **kwargs: Additional arguments for base class
        """
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class ServerError(EbayAPIError):
    """Raised when eBay API returns a server error (5xx)."""

    def __init__(self, message: str = "eBay API server error", **kwargs):
        super().__init__(message, **kwargs)


class ValidationError(EbayAPIError):
    """Raised when request validation fails."""

    pass

