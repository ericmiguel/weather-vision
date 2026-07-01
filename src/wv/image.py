"""Image file encoding into Data URIs (base64)."""

import base64
from pathlib import Path

from wv.config import DataUri
from wv.exceptions import InvalidImageError

_EXT_TO_MIME: dict[str, str] = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
}

_MB = 1024 * 1024
_MAX_IMAGE_SIZE_BYTES = 20 * _MB


def encode_image(path: Path) -> DataUri:
    """Read an image file, validate the format, and return a Data URI.

    Parameters
    ----------
    path : Path
        Filesystem path pointing to the image.
        The file must exist, be a regular file, and have a ``.png``,
        ``.jpg`` or ``.jpeg`` extension.

    Returns
    -------
    DataUri
        String in ``data:<mime>;base64,<payload>`` format ready to
        be passed to PydanticAI as a multimodal part.

    Raises
    ------
    FileNotFoundError
        If ``path`` does not exist on the filesystem.
    InvalidImageError
        If ``path`` is not a regular file, the extension is not
        supported, or the image exceeds the 20 MB size limit.
    """
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if not path.is_file():
        raise InvalidImageError(path, "Path does not point to a file")

    suffix = path.suffix.lower()

    if suffix not in _EXT_TO_MIME:
        allowed = ", ".join(sorted(_EXT_TO_MIME))
        raise InvalidImageError(
            path,
            f"Unsupported format '{suffix or '(no extension)'}'. Accepted: {allowed}.",
        )

    mime_type = _EXT_TO_MIME[suffix]
    raw = path.read_bytes()

    if len(raw) > _MAX_IMAGE_SIZE_BYTES:
        raise InvalidImageError(
            path,
            f"Image size {len(raw) / (1024 * 1024):.1f} MB exceeds "
            f"the recommended limit of 20 MB.",
        )

    encoded = base64.b64encode(raw).decode("ascii")
    return DataUri(f"data:{mime_type};base64,{encoded}")
