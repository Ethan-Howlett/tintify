#!/usr/bin/env bash
# Start a release: bump the version, run checks, then commit, tag, and push.
# Pushing the tag triggers .github/workflows/release.yml, which publishes to
# TestPyPI, tests the install, publishes to PyPI, and creates a GitHub Release.
#
# Usage: scripts/release.sh <patch|minor|major|X.Y.Z>
#
#   patch   0.2.1 -> 0.2.2   bug fixes
#   minor   0.2.1 -> 0.3.0   new features (or breaking changes before 1.0)
#   major   0.2.1 -> 1.0.0   breaking changes after 1.0
#   X.Y.Z   set an exact version
set -euo pipefail
cd "$(dirname "$0")/.."

step() { printf '\n\033[1;36m==> %s\033[0m\n' "$*"; }
fail() { printf '\n\033[1;31mERROR: %s\033[0m\n' "$*" >&2; exit 1; }
confirm() {
    local answer
    read -rp "$1 [y/N] " answer
    [[ "$answer" == [yY] || "$answer" == [yY][eE][sS] ]]
}

# --- 0. Preflight ---------------------------------------------------------

[[ $# -eq 1 ]] || fail "Usage: scripts/release.sh <patch|minor|major|X.Y.Z>"
bump="$1"

step "Preflight"
[[ "$(git branch --show-current)" == "main" ]] || fail "Switch to the main branch first."
[[ -z "$(git status --porcelain)" ]] || fail "Commit or stash your changes first (git status)."
git fetch --quiet --tags origin
[[ "$(git rev-parse HEAD)" == "$(git rev-parse origin/main)" ]] \
    || fail "main is not in sync with origin/main. Pull or push first."
echo "On main, clean, and in sync with GitHub."

# --- 1. Bump version --------------------------------------------------------

old=$(uv version --short)
if [[ "$bump" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    uv version --quiet "$bump"
elif [[ "$bump" =~ ^(patch|minor|major)$ ]]; then
    uv version --quiet --bump "$bump"
else
    fail "Unknown version '$bump'. Use patch, minor, major, or X.Y.Z."
fi
new=$(uv version --short)

# Until the release is committed, undo the version bump if anything fails or you stop.
committed=false
restore() {
    if [[ "$committed" == false ]]; then
        git checkout --quiet -- pyproject.toml uv.lock
        uv sync --quiet
        printf '\nStopped. Version restored to %s.\n' "$old" >&2
    fi
}
trap restore EXIT

git rev-parse --quiet --verify "refs/tags/v$new" >/dev/null && fail "Tag v$new already exists."
echo "Version: $old -> $new"

# --- 2. Check ---------------------------------------------------------------

scripts/check.sh

# --- 3. Commit, tag, and push -------------------------------------------------

step "Release v$new"
echo "Pushing the tag starts the release workflow on GitHub, which publishes"
echo "to TestPyPI and then PyPI. A version on PyPI can never be replaced."
confirm "Release v$new?" || exit 1

git commit --quiet -am "Release v$new"
git tag -a "v$new" -m "v$new"
committed=true
git push --quiet --atomic origin main "v$new"

printf '\n\033[1;32mPushed v%s. GitHub is publishing it now.\033[0m\n' "$new"
echo "  Progress: https://github.com/Ethan-Howlett/tintify/actions/workflows/release.yml"
echo "  When done: https://pypi.org/project/tintify/$new/"

if command -v gh >/dev/null && confirm "Watch the release workflow here?"; then
    sleep 5  # give GitHub a moment to start the run
    run_id=$(gh run list --workflow release.yml --branch "v$new" --limit 1 --json databaseId --jq '.[0].databaseId')
    [[ -n "$run_id" ]] || fail "Couldn't find the workflow run yet. Check the Progress link above."
    gh run watch "$run_id" --exit-status
fi
