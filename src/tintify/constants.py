"""Ready-made ANSI escape strings, for use without calling tint().

    print(Tint.RED + "Hello" + Tint.RESET)
    print(f"{Tint.BOLD}{Tint.BG_NAVY}{Tint.GOLD}Warning{Tint.RESET}")

Unlike tint(), these are plain strings and are always emitted, regardless of
NO_COLOR or whether output is a terminal.
"""

from __future__ import annotations

from .core import ESC, RESET, _STYLES, Color, _color_code


def _fg(color: Color) -> str:
    return f"{ESC}{_color_code(color, background=False)}m"


def _bg(color: Color) -> str:
    return f"{ESC}{_color_code(color, background=True)}m"


def _style(name: str) -> str:
    return f"{ESC}{_STYLES[name]}m"


class Tint:
    """Namespace of ANSI escape strings. Always end colored text with Tint.RESET."""

    RESET = RESET

    # --- styles ---
    BOLD = _style("bold")
    DIM = _style("dim")
    ITALIC = _style("italic")
    UNDERLINE = _style("underline")
    BLINK = _style("blink")
    REVERSE = _style("reverse")
    STRIKE = _style("strike")

    # --- standard foreground ---
    BLACK = _fg("black")
    RED = _fg("red")
    GREEN = _fg("green")
    YELLOW = _fg("yellow")
    BLUE = _fg("blue")
    MAGENTA = _fg("magenta")
    CYAN = _fg("cyan")
    WHITE = _fg("white")

    BRIGHT_BLACK = _fg("bright_black")
    BRIGHT_RED = _fg("bright_red")
    BRIGHT_GREEN = _fg("bright_green")
    BRIGHT_YELLOW = _fg("bright_yellow")
    BRIGHT_BLUE = _fg("bright_blue")
    BRIGHT_MAGENTA = _fg("bright_magenta")
    BRIGHT_CYAN = _fg("bright_cyan")
    BRIGHT_WHITE = _fg("bright_white")

    # --- 256-color foreground ---
    MAROON = _fg("maroon")
    CRIMSON = _fg("crimson")
    SALMON = _fg("salmon")
    CORAL = _fg("coral")
    ROSE = _fg("rose")
    PINK = _fg("pink")
    HOT_PINK = _fg("hot_pink")
    ORANGE = _fg("orange")
    DARK_ORANGE = _fg("dark_orange")
    BROWN = _fg("brown")
    CHOCOLATE = _fg("chocolate")
    TAN = _fg("tan")
    PEACH = _fg("peach")
    BEIGE = _fg("beige")
    GOLD = _fg("gold")
    KHAKI = _fg("khaki")
    OLIVE = _fg("olive")
    LIME = _fg("lime")
    MINT = _fg("mint")
    FOREST_GREEN = _fg("forest_green")
    SEA_GREEN = _fg("sea_green")
    TEAL = _fg("teal")
    TURQUOISE = _fg("turquoise")
    SKY_BLUE = _fg("sky_blue")
    LIGHT_BLUE = _fg("light_blue")
    STEEL_BLUE = _fg("steel_blue")
    NAVY = _fg("navy")
    SLATE = _fg("slate")
    INDIGO = _fg("indigo")
    PURPLE = _fg("purple")
    VIOLET = _fg("violet")
    LAVENDER = _fg("lavender")
    PLUM = _fg("plum")
    SILVER = _fg("silver")
    GRAY = _fg("gray")
    DARK_GRAY = _fg("dark_gray")

    # --- standard background ---
    BG_BLACK = _bg("black")
    BG_RED = _bg("red")
    BG_GREEN = _bg("green")
    BG_YELLOW = _bg("yellow")
    BG_BLUE = _bg("blue")
    BG_MAGENTA = _bg("magenta")
    BG_CYAN = _bg("cyan")
    BG_WHITE = _bg("white")

    BG_BRIGHT_BLACK = _bg("bright_black")
    BG_BRIGHT_RED = _bg("bright_red")
    BG_BRIGHT_GREEN = _bg("bright_green")
    BG_BRIGHT_YELLOW = _bg("bright_yellow")
    BG_BRIGHT_BLUE = _bg("bright_blue")
    BG_BRIGHT_MAGENTA = _bg("bright_magenta")
    BG_BRIGHT_CYAN = _bg("bright_cyan")
    BG_BRIGHT_WHITE = _bg("bright_white")

    # --- 256-color background ---
    BG_MAROON = _bg("maroon")
    BG_CRIMSON = _bg("crimson")
    BG_SALMON = _bg("salmon")
    BG_CORAL = _bg("coral")
    BG_ROSE = _bg("rose")
    BG_PINK = _bg("pink")
    BG_HOT_PINK = _bg("hot_pink")
    BG_ORANGE = _bg("orange")
    BG_DARK_ORANGE = _bg("dark_orange")
    BG_BROWN = _bg("brown")
    BG_CHOCOLATE = _bg("chocolate")
    BG_TAN = _bg("tan")
    BG_PEACH = _bg("peach")
    BG_BEIGE = _bg("beige")
    BG_GOLD = _bg("gold")
    BG_KHAKI = _bg("khaki")
    BG_OLIVE = _bg("olive")
    BG_LIME = _bg("lime")
    BG_MINT = _bg("mint")
    BG_FOREST_GREEN = _bg("forest_green")
    BG_SEA_GREEN = _bg("sea_green")
    BG_TEAL = _bg("teal")
    BG_TURQUOISE = _bg("turquoise")
    BG_SKY_BLUE = _bg("sky_blue")
    BG_LIGHT_BLUE = _bg("light_blue")
    BG_STEEL_BLUE = _bg("steel_blue")
    BG_NAVY = _bg("navy")
    BG_SLATE = _bg("slate")
    BG_INDIGO = _bg("indigo")
    BG_PURPLE = _bg("purple")
    BG_VIOLET = _bg("violet")
    BG_LAVENDER = _bg("lavender")
    BG_PLUM = _bg("plum")
    BG_SILVER = _bg("silver")
    BG_GRAY = _bg("gray")
    BG_DARK_GRAY = _bg("dark_gray")

    # --- anything else: 256-color index, hex, (r, g, b), or a registered name ---
    @staticmethod
    def fg(color: Color) -> str:
        """Tint.fg(208), Tint.fg("#ff8800"), Tint.fg((255, 136, 0))"""
        return _fg(color)

    @staticmethod
    def bg(color: Color) -> str:
        """Tint.bg(17), Tint.bg("#00005f"), Tint.bg((0, 0, 95))"""
        return _bg(color)
