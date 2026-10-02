"""Core logic for tintify: turning text + style options into ANSI escape codes."""

from __future__ import annotations

import os
import sys
from typing import TextIO, Union

ESC = "\033["
RESET = f"{ESC}0m"

# The 8 standard ANSI colors. Foreground = 30 + offset, background = 40 + offset.
# "bright_" versions use 90 / 100 instead.
_ANSI_COLORS: dict[str, int] = {
    "black": 0, "red": 1, "green": 2, "yellow": 3,
    "blue": 4, "magenta": 5, "cyan": 6, "white": 7,
}

# Named colors from the xterm 256-color palette (indices 16-255).
# Any index can also be used directly, e.g. tint("hi", 208).
_256_COLORS: dict[str, int] = {
    # reds / pinks
    "maroon": 88, "crimson": 161, "salmon": 210, "coral": 209,
    "rose": 211, "pink": 218, "hot_pink": 205,
    # oranges / browns / yellows
    "orange": 208, "dark_orange": 166, "brown": 130, "chocolate": 94,
    "tan": 180, "peach": 223, "beige": 230, "gold": 220, "khaki": 186,
    # greens
    "olive": 100, "lime": 154, "mint": 121, "forest_green": 28, "sea_green": 36,
    # cyans / blues
    "teal": 30, "turquoise": 44, "sky_blue": 117, "light_blue": 153,
    "steel_blue": 67, "navy": 17, "slate": 60,
    # purples
    "indigo": 54, "purple": 129, "violet": 177, "lavender": 183, "plum": 96,
    # grays
    "silver": 250, "gray": 244, "dark_gray": 240,
}

_STYLES = {'bold': 1, 'dim': 2, 'italic': 3, 'underline': 4,
           'blink': 5, 'reverse': 7, 'strike': 9}

# "red", "bright_red", "sky_blue", 208, "#ff8800", or (255, 136, 0)
Color = Union[str, int, tuple[int, int, int]]

# User-registered colors (see register_color), emitted as 24-bit RGB.
_CUSTOM_RGB: dict[str, tuple[int, int, int]] = {}


def _normalize(name: str) -> str:
    '''"Sky Blue", "sky-blue" and "sky_blue" all become "sky_blue".'''
    return name.strip().lower().replace(' ', '_').replace('-', '_')


def _is_builtin(key: str) -> bool:
    return key in _256_COLORS or key.removeprefix('bright_') in _ANSI_COLORS


def register_color(name: str, value: Color) -> None:
    '''Add (or override) a custom named color, e.g. register_color('brand', '#5a2ee0').'''
    if isinstance(value, str):
        value = _parse_hex(value)
    elif isinstance(value, int):
        raise TypeError('register_color() takes a hex string or an (r, g, b) tuple.')
    _check_rgb(value)
    key = _normalize(name)
    if _is_builtin(key):
        raise ValueError(f'{name!r} is a built-in color and cannot be overridden.')
    _CUSTOM_RGB[key] = value


def available_colors() -> list[str]:
    '''Return a list of all color names tint() accepts.'''
    basic = list(_ANSI_COLORS) + [f'bright_{n}' for n in _ANSI_COLORS]
    return basic + sorted(_256_COLORS) + sorted(_CUSTOM_RGB)


def _check_rgb(rgb: tuple[int, int, int]) -> None:
    if len(rgb) != 3 or not all(isinstance(c, int) and 0 <= c <= 255 for c in rgb):
        raise ValueError(f'RGB values must be three ints 0-255: {rgb}')


def _parse_hex(value: str) -> tuple[int, int, int]:
    h = value.lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    if len(h) != 6:
        raise ValueError(f'Invalid hex color: {value}')
    try:
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    except ValueError:
        raise ValueError(f'Invalid hex color: {value}') from None


def _color_code(color: Color, background: bool) -> str:
    '''Return the ANSI parameter string for a color.'''
    if isinstance(color, bool):
        raise TypeError(f'Invalid color: {color!r}')

    if isinstance(color, int):
        if not 0 <= color <= 255:
            raise ValueError(f'256-color index must be 0-255: {color}')
        return f"{48 if background else 38};5;{color}"

    if isinstance(color, tuple):
        _check_rgb(color)
        r, g, b = color
        return f"{48 if background else 38};2;{r};{g};{b}"

    if color.startswith('#'):
        return _color_code(_parse_hex(color), background)

    name = _normalize(color)
    if name in _CUSTOM_RGB:
        return _color_code(_CUSTOM_RGB[name], background)
    if name in _256_COLORS:
        return _color_code(_256_COLORS[name], background)

    bright = name.startswith('bright_')
    if bright:
        name = name.removeprefix('bright_')
    if name not in _ANSI_COLORS:
        raise ValueError(f'Unknown color name: {color}')

    base = (100 if bright else 40) if background else (90 if bright else 30)
    return str(base + _ANSI_COLORS[name])


def colors_enabled(stream: TextIO | None = None) -> bool:
    """Decide whether to emit color, following common conventions.

    - NO_COLOR set (any value)    -> off   (https://no-color.org)
    - FORCE_COLOR set (any value) -> on
    - otherwise                   -> on only if the stream is a real terminal
    """
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    stream = stream or sys.stdout
    return hasattr(stream, "isatty") and stream.isatty() if stream else False


def tint(
        text: str,
        fg: Color | None = None,
        bg: Color | None = None,
        *,
        bold: bool = False,
        dim: bool = False,
        italic: bool = False,
        underline: bool = False,
        strike: bool = False,
        force: bool | None = None,
) -> str:
    """Wrap text in ANSI codes.

    >>> tint("hello", "red", bold=True, force=True)
    '\\x1b[1;31mhello\\x1b[0m'

    force=True always colors, force=False never does,
    and None (default) auto-detects with colors_enabled().
    """
    enabled = colors_enabled() if force is None else force
    if not enabled:
        return text

    codes: list[str] = []
    flags = {'bold': bold, 'dim': dim, 'italic': italic, 'underline': underline, 'strike': strike}
    codes += [str(_STYLES[name]) for name, on in flags.items() if on]

    if fg is not None:
        codes.append(_color_code(fg, background=False))
    if bg is not None:
        codes.append(_color_code(bg, background=True))

    if not codes:
        return text
    return f"{ESC}{';'.join(codes)}m{text}{RESET}"
