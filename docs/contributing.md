# Contributing

## Pull Requests

- Limit each pull request to *one* idea only.
- Pull requests branches will be squashed and rebased on top of `master`.
- *Always* add tests and docs for your code.
- No contribution is too small! Please submit as many fixes for typos and grammar bloopers as you
  can!
- Make sure your changes pass the
  [CI checks](https://github.com/t-mart/wap/blob/master/.github/workflows/ci.yml).
- Once you've addressed review feedback, make sure to bump the pull request with a short note.

## Developer Setup

A few nuggets of information about the project:

- This is a [Python](https://www.python.org/downloads/) project.
- Depenedencies are managed with [uv](https://docs.astral.sh/uv/). Install the project with
  `uv sync`.
- Tests can be run with `uv run pytest`.
- Docs can be built with `uv run mkdocs build` (or, rebuilt continuously with a development server with
  `mkdocs serve`).
- Linting and formatting should be done with
  [ruff](https://docs.astral.sh/ruff/). That is, `uv run ruff check` and `uv run
  ruff format`, respectively.


## Releasing

1. Bump the version in the `pyproject.toml`.

2. Create a git tag for that version, **prefixing the version with a `v` character**:

    ```bash
    git tag -a "v1.2.3" -m "Release v1.2.3"
    ```

3. Push the tag to GitHub and let the
   [CI workflow](https://github.com/t-mart/wap/blob/master/.github/workflows/ci.yml) do the rest:

    ```bash
    git push
    ```

    !!! note

        The `v` version prefix signals to the CI script that this push should also be published to
        PyPI.
