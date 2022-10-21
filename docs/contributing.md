# Contributing

## Pull Requests

- Limit each pull request to *one* change only.
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
- Depenedencies are managed with [poetry](https://python-poetry.org/). Install the project with
  `poetry install`.
- Tests can be run with `python -m pytest`.
- Docs can be built with `mkdocs build` (or, rebuilt continuously with a development server with
  `mkdocs serve`).
- Formatting should be done with [black](https://github.com/psf/black) and
  [isort](https://github.com/PyCQA/isort). There's a Makefile target to do both with `make format`.
- Code should yield no [mypy](https://mypy.readthedocs.io/en/stable/) or
  [flake8](https://flake8.pycqa.org/en/latest/) errors. Run `make check` to check for that.
- You can run [pre-commit](https://pre-commit.com/) checks by install the hook with `pre-commit
  install`.


## Releasing

1. Bump the version in the `pyproject.toml`. It can be done manually or with Poetry's `version`
   command:

    ```bash
    # for example, to bump the patch part...
    poetry version patch
    ```

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
