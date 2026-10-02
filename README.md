# tintify

Easy terminal text colors for Python. No dependencies.

```python
from tintify import tint, Tint

print(tint("Success!", "green", bold=True))
print(Tint.RED + "Error:" + Tint.RESET + " something went wrong")
```

- 16 standard colors, 36 named colors from the 256-color palette, any palette index, hex, and RGB
- Bold, dim, italic, underline, and strikethrough
- Respects [`NO_COLOR`](https://no-color.org) and `FORCE_COLOR`, and turns color off automatically when output isn't a terminal
- Fully typed

## Installation

```sh
pip install tintify
```

Requires Python 3.9 or newer.

## Two ways to color text

### `tint()`: color a piece of text

```python
from tintify import tint

print(tint("hello", "red"))
print(tint("hello", "sky_blue", bg="navy"))
print(tint("hello", "#ff8800", bold=True, underline=True))
print(tint("hello", (255, 136, 0)))   # RGB
print(tint("hello", 208))             # 256-color palette index
```

`tint()` wraps the text and resets the style at the end, so colors never leak
into the rest of your output. It also checks whether color should be shown at
all (see [Turning color off](#turning-color-off)).

```python
tint(
    text,
    fg=None,          # text color
    bg=None,          # background color
    *,
    bold=False,
    dim=False,
    italic=False,
    underline=False,
    strike=False,
    force=None,       # True = always color, False = never, None = auto-detect
)
```

### `Tint`: constants you can drop in anywhere

If you already build strings with `+` or f-strings, use the `Tint` constants
instead. No function call needed:

```python
from tintify import Tint

print(Tint.RED + "Hello" + Tint.RESET)
print(f"{Tint.BOLD}{Tint.BG_NAVY}{Tint.GOLD} Warning {Tint.RESET}")
```

| Kind        | Examples                                                        |
|-------------|-----------------------------------------------------------------|
| Text color  | `Tint.RED`, `Tint.BRIGHT_CYAN`, `Tint.ORANGE`, `Tint.LAVENDER`  |
| Background  | `Tint.BG_RED`, `Tint.BG_BRIGHT_CYAN`, `Tint.BG_NAVY`            |
| Styles      | `Tint.BOLD`, `Tint.DIM`, `Tint.ITALIC`, `Tint.UNDERLINE`, `Tint.BLINK`, `Tint.REVERSE`, `Tint.STRIKE` |
| Reset       | `Tint.RESET`                                                    |
| Any color   | `Tint.fg(208)`, `Tint.fg("#ff8800")`, `Tint.bg((0, 0, 95))`     |

Every color name below has a `Tint.NAME` and a `Tint.BG_NAME` constant.

> **Note:** `Tint` constants are plain strings, so they are **always** output,
> even when `NO_COLOR` is set or output is redirected to a file. Always end
> with `Tint.RESET`. If you want automatic detection, use `tint()`.

## Colors

**Standard colors:** `black`, `red`, `green`, `yellow`, `blue`, `magenta`,
`cyan`, `white`, plus a `bright_` version of each (e.g. `bright_red`). These
follow your terminal's theme.

**Named 256-palette colors:**

| Reds & pinks | Oranges & browns | Greens         | Blues & cyans | Purples    | Grays       |
|--------------|------------------|----------------|---------------|------------|-------------|
| `maroon`     | `orange`         | `olive`        | `teal`        | `indigo`   | `silver`    |
| `crimson`    | `dark_orange`    | `lime`         | `turquoise`   | `purple`   | `gray`      |
| `salmon`     | `brown`          | `mint`         | `sky_blue`    | `violet`   | `dark_gray` |
| `coral`      | `chocolate`      | `forest_green` | `light_blue`  | `lavender` |             |
| `rose`       | `tan`            | `sea_green`    | `steel_blue`  | `plum`     |             |
| `pink`       | `peach`          |                | `navy`        |            |             |
| `hot_pink`   | `beige`          |                | `slate`       |            |             |
|              | `gold`           |                |               |            |             |
|              | `khaki`          |                |               |            |             |

Color names ignore case, spaces, and hyphens: `"Sky Blue"`, `"sky-blue"`, and
`"sky_blue"` all work.

**Anything else:**

- A palette index from `0` to `255`, e.g. `tint("hi", 208)`
- A hex string, e.g. `"#ff8800"` or `"#f80"`
- An RGB tuple, e.g. `(255, 136, 0)`

See every named color in your own terminal:

```sh
python -m tintify
```

Or get the list in code:

```python
from tintify import available_colors
print(available_colors())
```

## Custom colors

Register your own names (for example, your brand colors) and use them like any
built-in color:

```python
from tintify import register_color, tint, Tint

register_color("brand", "#5a2ee0")
register_color("brand_light", (180, 160, 255))

print(tint("Acme CLI", "brand", bold=True))
print(Tint.fg("brand") + "also works here" + Tint.RESET)
```

Built-in names can't be overridden.

## Turning color off

`tint()` decides whether to output color using these rules, in order:

1. `force=True` / `force=False` passed to `tint()`: always or never.
2. `NO_COLOR` environment variable is set: no color.
3. `FORCE_COLOR` environment variable is set: color.
4. Otherwise: color only if output is going to a terminal (not a file or pipe).

You can check this yourself with `colors_enabled()`:

```python
import sys
from tintify import colors_enabled

if colors_enabled(sys.stderr):
    ...
```

## Terminal support

- The 16 standard colors and the styles work in almost every terminal.
- The 256-palette colors and palette indexes work in nearly all modern
  terminals, including macOS Terminal, iTerm2, Windows Terminal, VS Code, and
  most Linux terminals.
- Hex and RGB values use 24-bit "truecolor", which most modern terminals
  support. Older terminals may show a close match or ignore the color.

## License

MIT
