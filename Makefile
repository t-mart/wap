paths := src tests docs

all: format check

.PHONY: format check
format:
	isort $(paths)
	black $(paths)

check:
	mypy $(paths)
	flake8 $(paths)
