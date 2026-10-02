#!/usr/bin/env bash
# Run every pre-release check: tests, build, and package validation.
# Leaves a fresh, verified build in dist/.
#
# Usage: scripts/check.sh
set -euo pipefail
cd "$(dirname "$0")/.."

OLDEST_PYTHON="3.9"  # keep in sync with requires-python in pyproject.toml

step() { printf '\n\033[1;36m==> %s\033[0m\n' "$*"; }
fail() { printf '\n\033[1;31mERROR: %s\033[0m\n' "$*" >&2; exit 1; }

version=$(uv version --short)

step "Tests (default Python)"
uv run pytest -q

step "Tests (Python $OLDEST_PYTHON, oldest supported)"
uv run --isolated --python "$OLDEST_PYTHON" --with pytest pytest -q

step "Build v$version"
rm -rf dist
uv build --no-sources

step "Validate metadata and README"
uvx twine check --strict dist/*

step "Check for accidental dependencies"
deps=$(unzip -p dist/*.whl '*/METADATA' | grep '^Requires-Dist' || true)
if [[ -n "$deps" ]]; then
    fail "The package has runtime dependencies, but tintify should have none:
$deps
If this is a dev tool, fix it with: uv remove <name> && uv add --dev <name>"
fi
echo "None."

step "Install the built wheel in a clean environment"
uv run --isolated --no-project --with dist/*.whl -- python -c "
import sys, tintify
assert tintify.__version__ == sys.argv[1], f'version is {tintify.__version__}, expected {sys.argv[1]}'
print(tintify.tint(f'tintify {tintify.__version__} works', 'green', force=True))
" "$version"

printf '\n\033[1;32mAll checks passed for v%s.\033[0m\n' "$version"
