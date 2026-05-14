# Makefile

.PHONY: dev tests lint format clean release

dev:
	pip install -e ".[dev]"

tests:
	robot tests/system

lint:
	ruff check .
	black --check .

format:
	black .

clean:
	rm -rf build
	find . -type f -name "*.pyc" -delete

release:
	rm -rf build dist
	python -m build
	python -m twine upload dist/*

.PHONY: help
help:
	@echo "Makefile commands:"
	@echo "  dev 		  - Install development version of the package with all dependencies"
	@echo "  tests		  - Run system tests with Robot Framework"
	@echo "  lint         - Check code style with ruff and black"
	@echo "  format       - Format code with black"
	@echo "  clean        - Clean build artifacts and Python bytecode"
	@echo "  release      - Build and upload the package to PyPI"
