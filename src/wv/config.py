"""Application configuration via environment variables (pydantic-settings)."""

from typing import NewType

from pydantic import field_validator
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

from wv.exceptions import InvalidConfigError

ModelName = NewType("ModelName", str)
DataUri = NewType("DataUri", str)


class Settings(BaseSettings):
    """Load and validate application settings from ``.env``.

    Uses ``pydantic-settings`` to read environment variables
    (or a ``.env`` file) and validate types. The ``model_config``
    attribute enforces that unknown variables raise an error
    (``extra="forbid"``).

    Attributes
    ----------
    openrouter_api_key : str
        OpenRouter API key; must be non-empty and start with
        ``sk-or-``. Validated by ``_validate_key``.
    model_name : ModelName
        Model identifier on OpenRouter (e.g.
        ``openai/gpt-4o`` or ``google/gemini-2.0-flash``). Must be provided via the
        ``MODEL_NAME`` environment variable; no default value.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="forbid",
    )

    openrouter_api_key: str
    model_name: ModelName

    @field_validator("openrouter_api_key")
    @classmethod
    def _validate_key(cls, v: str) -> str:
        """Validate a raw OpenRouter API key.

        Parameters
        ----------
        v : str
            Value read from ``.env`` or environment.

        Returns
        -------
        str
            Trimmed key.

        Raises
        ------
        InvalidConfigError
            If the key is not a string, is empty, or does not start with ``sk-or-``.
        """
        if not isinstance(v, str):
            raise InvalidConfigError(
                "openrouter_api_key", v, f"Expected str, got {type(v).__name__}"
            )

        stripped = v.strip()

        if not stripped:
            raise InvalidConfigError("openrouter_api_key", v, "cannot be empty")

        if not stripped.startswith("sk-or-"):
            raise InvalidConfigError(
                "openrouter_api_key",
                stripped[:10],
                f"must start with 'sk-or-'; got {stripped[:10]!r}...",
            )

        return stripped
