# Developing & releasing tintify

Notes for maintainers. Users of the library should read [README.md](README.md).

All commands are run from the project root and use [uv](https://docs.astral.sh/uv/).

## Quick reference

```sh
uv run pytest                 # run the tests
scripts/check.sh              # every pre-release check (tests, build, validation)
scripts/release.sh patch      # release a new version (or: minor, major, X.Y.Z)
```

`scripts/release.sh` (on your machine):

1. Checks that you're on `main` with no uncommitted changes and in sync with GitHub.
2. Bumps the version in `pyproject.toml`.
3. Runs `scripts/check.sh`.
4. Asks, then commits `Release vX.Y.Z`, tags it `vX.Y.Z`, and pushes both.
5. Optionally shows the GitHub workflow's progress in your terminal (`gh run watch`).

If anything fails or you answer "no", the version bump is undone and nothing is
committed. Commit your code changes **before** running it. The release commit
should only contain the version bump.

Pushing the tag starts **`.github/workflows/release.yml`** on GitHub:

```
build + check -> TestPyPI -> install from TestPyPI -> PyPI -> GitHub Release
```

Each step only runs if the one before it succeeded. If you set up a required
reviewer (see below), GitHub waits for you to click **Approve** before the PyPI
step. The GitHub Release has auto-generated notes and the built files attached.

**`.github/workflows/ci.yml`** runs the tests on Python 3.9–3.14 (plus macOS
and Windows) and `scripts/check.sh` on every push to `main` and every pull
request.

If a release fails after the tag is pushed, the tag and release commit are
already on GitHub. Fix the problem and release the next version. If it failed
before reaching TestPyPI, you can delete the tag and try again:
`git push --delete origin vX.Y.Z && git tag -d vX.Y.Z`.

### One-time setup: trusted publishing

The workflow doesn't use API tokens. PyPI trusts uploads that come from this
repo's release workflow, so there are no tokens to store or leak. Set it up
once on each site.

**1. TestPyPI:** go to <https://test.pypi.org/manage/project/tintify/settings/publishing/>
and add a GitHub publisher:

| Field             | Value           |
|-------------------|-----------------|
| Owner             | `Ethan-Howlett` |
| Repository name   | `tintify`       |
| Workflow name     | `release.yml`   |
| Environment name  | `testpypi`      |

**2. PyPI:** same thing at <https://pypi.org/manage/project/tintify/settings/publishing/>,
but with environment name **`pypi`**.

**3. GitHub environments:** in the repo, go to **Settings -> Environments** and
create `testpypi` and `pypi`. On `pypi`, enable **Required reviewers** and add
yourself. Every PyPI upload then waits for your approval on the workflow run
page. This is optional but recommended.

**4. Remove the old tokens.** Once a release has gone through, delete your API
tokens at <https://pypi.org/manage/account/token/> and
<https://test.pypi.org/manage/account/token/>, and remove the
`export TEST_PYPI_TOKEN=...` line from `~/.zshrc`. Keep them only if you want
to upload by hand (steps 6–7 below).

The rest of this document explains each step and how to do it by hand.

## 1. Setup

```sh
uv sync
```

This creates `.venv/`, installs tintify in editable mode, and installs the
dev tools (pytest). You only need to do it once. `uv run` also keeps the
environment in sync automatically.

## 2. Test

```sh
uv run pytest          # run all tests
uv run pytest -v       # one line per test
uv run pytest -k hex   # only tests whose name contains "hex"
```

Don't run test files directly (`python tests/test_core.py`). They're plain
functions that pytest finds and runs, and outside `uv run` Python can't find
the `tintify` package.

### Test against the oldest supported Python

`pyproject.toml` says `requires-python = ">=3.9"`, so check that version too
(uv downloads it if needed):

```sh
uv run --isolated --python 3.9 --with pytest pytest -q
```

## 3. Validate by eye

Tests check the escape codes, but only a real terminal shows whether the colors
look right.

```sh
uv run python -m tintify                       # every named color, fg + bg
NO_COLOR=1 uv run python -c "from tintify import tint; print(tint('plain?', 'red'))"
uv run python -c "from tintify import tint; print(tint('plain?', 'red'))" | cat
```

The last two should print uncolored text: one because `NO_COLOR` is set, the
other because output is piped. Also try at least one terminal you don't usually
use (e.g. macOS Terminal if you use iTerm2).

## 4. Prepare a release

### Version numbers

tintify uses [semantic versioning](https://semver.org): `MAJOR.MINOR.PATCH`.
Before 1.0, bump **minor** for new features or breaking changes and **patch**
for bug fixes.

> Neither TestPyPI nor PyPI ever let you reuse a version number, even after
> deleting it. If an upload is broken, release the next version instead.

The version is set **only** in `pyproject.toml`. `tintify.__version__` reads
it from the installed package.

```sh
uv version --bump minor        # e.g. 0.2.1 -> 0.3.0
uv version                     # print it to confirm
```

### Pre-release checklist

- [ ] `scripts/check.sh` passes
- [ ] `README.md` matches the current API (it becomes the PyPI page)
- [ ] Version bumped in `pyproject.toml`
- [ ] Optional but recommended: add `[project.urls]` (Homepage / Source /
      Issues) and `classifiers` to `pyproject.toml` so the PyPI page links back
      to the repo
- [ ] Changes committed to git

## 5. Build

```sh
rm -rf dist
uv build --no-sources
```

- `rm -rf dist` matters: `uv publish` uploads **everything** in `dist/`, and old
  builds left there will be uploaded too or cause errors.
- `--no-sources` builds the way PyPI users will install it, without any local
  overrides.

This produces two files in `dist/`: a source archive (`.tar.gz`) and a wheel
(`.whl`).

### Check the build

```sh
uvx twine check --strict dist/*
```

This confirms the package metadata is valid and that the README will render on
PyPI. Next, check that the package doesn't pull in any dependencies by accident:

```sh
unzip -p dist/*.whl '*/METADATA' | grep Requires-Dist
```

This should print **nothing**, because tintify has no dependencies. If pytest
(or another dev tool) shows up, it was added with `uv add X` instead of
`uv add --dev X`. Fix it with `uv remove X && uv add --dev X`, then rebuild.

Then check that the built wheel installs and works on its own:

```sh
uv run --isolated --no-project --with dist/*.whl -- python -c \
  "import tintify; print(tintify.__version__); print(tintify.tint('ok', 'green', force=True))"
```

## 6. Publish to TestPyPI first

> Normally the release workflow does steps 6–8. These are the manual steps,
> for when you need to upload by hand.

[TestPyPI](https://test.pypi.org) is a separate practice copy of PyPI. Upload
there first to catch problems where it doesn't matter.

1. Create an API token at <https://test.pypi.org/manage/account/token/>.
   TestPyPI accounts are separate from PyPI accounts.
2. Upload:

   ```sh
   uv publish \
     --publish-url https://test.pypi.org/legacy/ \
     --check-url https://test.pypi.org/simple/ \
     --token pypi-XXXXXXXX
   ```

   (Or `export UV_PUBLISH_TOKEN=pypi-XXXXXXXX` first and drop `--token`.)

3. Install it from TestPyPI in a clean environment, from a folder **outside**
   the project so the local copy isn't used:

   ```sh
   cd /tmp
   uv run --isolated --no-project \
     --default-index https://test.pypi.org/simple/ \
     --refresh-package tintify \
     --with tintify==0.2.0 \
     -- python -c "import tintify; print(tintify.__version__, tintify.Tint.RED + 'hi' + tintify.Tint.RESET)"
   ```

   If it says "there is no version of tintify==…" right after uploading, wait
   a few minutes and try again. TestPyPI and PyPI can serve a cached list of
   versions for up to 10 minutes after an upload.

4. Look at the project page at <https://test.pypi.org/project/tintify/>. Check
   that the README renders properly.

## 7. Publish to PyPI

Once TestPyPI looks right:

1. Create an API token at <https://pypi.org/manage/account/token/>. For the
   very first upload it must be an "Entire account" token, because the project
   doesn't exist yet. After that, replace it with a token scoped to `tintify`.
2. Upload the **same** files from `dist/`:

   ```sh
   uv publish --token pypi-XXXXXXXX
   ```

3. Check: <https://pypi.org/project/tintify/>, then
   `uv run --isolated --no-project --with tintify -- python -m tintify`.

> A PyPI upload can't be undone or replaced. You can "yank" a bad release,
> but its version number is used up for good. That's why TestPyPI comes first.

## 8. After releasing

```sh
git tag -a v0.3.0 -m v0.3.0
git push origin main v0.3.0
```

Tagging each release makes it easy to see exactly what code shipped in each
version.

> **Heads up:** pushing a `v*` tag starts the release workflow. After a manual
> upload, the workflow fails at the TestPyPI step because that version already
> exists there. That's harmless: nothing gets uploaded twice. You can cancel
> the run on the Actions tab.
