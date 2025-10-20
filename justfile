default:
    @just --list

# Run tests with pytest
test:
    uv run pytest

# Run linter (ruff check)
lint:
    uv run ruff check .

# Format code with ruff
format:
    uv run ruff format .

# Run type checker (mypy)
type-check:
    uv run mypy src/

# Run all checks (lint, type-check, test)
check: lint type-check test

# Fix linting issues automatically
fix:
    uv run ruff check --fix .

# Install dependencies
install:
    uv sync

# Clean build artifacts and cache
clean:
    rm -rf .pytest_cache
    rm -rf .ruff_cache
    rm -rf .mypy_cache
    rm -rf dist
    rm -rf build
    rm -rf *.egg-info
    find . -type d -name __pycache__ -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete

# Build the package
build:
    uv build

# Publish package to PyPI
publish:
    uv run twine upload dist/*

# Run the application
run *args:
    uv run nvr {{ args }}

# upgrade all dependencies
upgrade:
    uv sync --all-groups -U
