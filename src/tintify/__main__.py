"""Preview every named color: python -m tintify"""

from .core import available_colors, tint

for name in available_colors():
    print(tint(f"{name:<16}", name, force=True), tint("  " * 8, bg=name, force=True))
