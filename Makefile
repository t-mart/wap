.PHONY: all
all: pre-commit

.PHONY: pre-commit
pre-commit: fix check test

.PHONY: fix
fix: isort-fix black-fix

.PHONY: check
check: flake8-check mypy-check twine-check

.PHONY: mypy-check
mypy-check:
	poetry run mypy

.PHONY: flake8-check
flake8-check:
	poetry run flake8 wap tests docs

.PHONY: isort-fix
isort-fix:
	poetry run isort wap tests docs

.PHONY: black-fix
black-fix:
	poetry run black wap tests docs

.PHONY: twine-check
twine-check:
	rm -rf dist
	poetry build
	poetry run twine check dist/*

.PHONY: test
test:
	poetry run pytest tests --cov=wap --cov-report=xml

.PHONY: sphinx-autobuild
sphinx-autobuild:
	sphinx-autobuild docs docs/_build/html

.PHONY: clean
clean:
	rm -rf `find . -name __pycache__`
	rm -rf `find . -name .mypy_cache`
	rm -rf `find . -name .pytest_cache`
	rm -f `find . -type f -name '*.py[co]' `
	rm -f .coverage
	rm -f coverage.xml
	make -C docs clean
	rm -rf dist

.PHONY: update-schema
update-schema:
	python scripts/update_schema.py
