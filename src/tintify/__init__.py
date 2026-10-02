"""tintify: simple terminal text colors."""

from importlib.metadata import PackageNotFoundError, version

from .constants import Tint
from .core import available_colors, colors_enabled, register_color, tint

__all__ = ["Tint", "tint", "colors_enabled", "register_color", "available_colors"]

try:
    __version__ = version("tintify")  # single source of truth: pyproject.toml
except PackageNotFoundError:  # running from source without installing
    __version__ = "0.0.0+unknown"
