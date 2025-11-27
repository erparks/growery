"""Custom exceptions for the application."""


class PlantNotFoundError(Exception):
    """Raised when a plant is not found."""
    pass


class PhotoHistoryNotFoundError(Exception):
    """Raised when a photo history is not found."""
    pass


class InvalidFileTypeError(Exception):
    """Raised when an invalid file type is provided."""
    pass


class ValidationError(Exception):
    """Raised when input validation fails."""
    pass

