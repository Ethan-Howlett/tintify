"""tintify: simple terminal text colors."""

from .constants import Tint
from .core import available_colors, colors_enabled, register_color, tint

__all__ = ["Tint", "tint", "colors_enabled", "register_color", "available_colors"]
__version__ = "0.2.1"
