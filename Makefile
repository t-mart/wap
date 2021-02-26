pre-commit: fix check test

fix: isort-fix black-fix

check: mypy-check twine-check

sphinx-autobuild:
	sphinx-autobuild docs docs/_build/html

mypy-check:
	poetry run mypy

isort-fix:
	poetry run isort wap tests docs/conf.py

black-fix:
	poetry run black wap tests docs/conf.py

twine-check:
	poetry build
	poetry run twine check dist/*

test:
	poetry run pytest tests --cov=wap --cov-report=xml

.PHONY: autobuild check mypy-check isort-fix black-fix twine-check
