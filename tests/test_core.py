import pytest

from tintify import Tint, available_colors, colors_enabled, register_color, tint


def test_basic_color():
    assert tint("hi", "red", force=True) == "\033[31mhi\033[0m"


def test_bright_and_background():
    assert tint("hi", "bright_green", bg="blue", force=True) == "\033[92;44mhi\033[0m"


def test_styles_combine():
    assert tint("hi", "cyan", bold=True, underline=True, force=True) == "\033[1;4;36mhi\033[0m"


def test_rgb_and_hex_match():
    assert tint("hi", (255, 136, 0), force=True) == tint("hi", "#ff8800", force=True)
    assert tint("hi", "#f80", force=True) == "\033[38;2;255;136;0mhi\033[0m"


def test_force_false_returns_plain_text():
    assert tint("hi", "red", force=False) == "hi"


def test_no_options_returns_plain_text():
    assert tint("hi", force=True) == "hi"


def test_invalid_color_raises():
    with pytest.raises(ValueError):
        tint("hi", "purpleish", force=True)


def test_no_color_env(monkeypatch):
    monkeypatch.setenv("NO_COLOR", "1")
    assert not colors_enabled()
    assert tint("hi", "red") == "hi"


def test_force_color_env(monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.setenv("FORCE_COLOR", "1")
    assert colors_enabled()

def test_256_index_and_name():
    assert tint("hi", 208, force=True) == "\033[38;5;208mhi\033[0m"
    assert tint("hi", "orange", force=True) == tint("hi", 208, force=True)
    assert tint("hi", bg="Sky Blue", force=True) == "\033[48;5;117mhi\033[0m"


def test_invalid_256_index_raises():
    with pytest.raises(ValueError):
        tint("hi", 256, force=True)


def test_register_color():
    register_color("brand", "#5a2ee0")
    assert tint("hi", "brand", force=True) == "\033[38;2;90;46;224mhi\033[0m"
    with pytest.raises(ValueError):
        register_color("red", "#ff0000")


def test_tint_constants():
    assert Tint.RED + "hi" + Tint.RESET == tint("hi", "red", force=True)
    assert Tint.BG_BRIGHT_BLUE == "\033[104m"
    assert Tint.BOLD == "\033[1m"
    assert Tint.ORANGE == Tint.fg(208)
    assert Tint.fg("#ff8800") == "\033[38;2;255;136;0m"


def test_every_color_has_constants():
    for name in available_colors():
        if name == "brand":  # registered in another test
            continue
        assert hasattr(Tint, name.upper()), name
        assert hasattr(Tint, f"BG_{name.upper()}"), name
