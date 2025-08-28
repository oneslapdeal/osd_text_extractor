.PHONY: install lint type test build check dist publish clean help

help:
	@echo "Available targets:"
	@echo "  install  - install project dependencies with uv"
	@echo "  lint     - run ruff checks"
	@echo "  type     - run mypy (strict)"
	@echo "  test     - run pytest with coverage"
	@echo "  build    - build sdist and wheel"
	@echo "  check    - run twine check on dist artifacts"
	@echo "  dist     - build and check"
	@echo "  publish  - upload to PyPI via twine"
	@echo "  clean    - remove build/test caches"

install:
	uv sync

lint:
	uv run ruff check src/ tests/

type:
	uv run mypy

test:
	uv run pytest -q

build:
	uv run python -m build

check:
	uv run twine check dist/*

dist: build check

publish:
	uv run twine upload dist/*

clean:
	rm -rf build dist *.egg-info htmlcov .pytest_cache .mypy_cache
