"""Domain-specific exceptions for Weather Vision."""

from pathlib import Path


class WeatherVisionError(Exception):
    """Base for all domain exceptions."""


class InvalidImageError(WeatherVisionError):
    """Image validation failure."""

    def __init__(self, path: Path, reason: str):
        self.path = path
        self.reason = reason
        super().__init__(f"Invalid image '{path}': {reason}")


class InvalidConfigError(WeatherVisionError):
    """Configuration validation failure."""

    def __init__(self, field: str, value: str, detail: str):
        self.field = field
        self.value = value
        self.detail = detail
        super().__init__(f"Invalid config {field}={value!r}: {detail}")
