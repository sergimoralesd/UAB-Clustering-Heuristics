class FetchError(Exception):
    """Raised when a transaction cannot be fetched."""


class NotFoundError(FetchError):
    """Raised when the txid is not found in the chosen source."""

class ConfigurationError(Exception):
    """Raised when the programs lacks configuration values."""