# Run Pytest Action

A composite GitHub Action that sets up Python, installs project dependencies from `pyproject.toml`, and runs pytest with optional customization.

## Overview

This action simplifies running pytest in your CI/CD workflows by handling:

- Python environment setup
- Dependency installation from `pyproject.toml`
- Running pytest with optional custom arguments

Perfect for use with matrix strategies to test across multiple Python versions.

## Inputs

| Input                  | Required | Default | Description                                                                                                                                      |
| ---------------------- | -------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| `python-version`       | Yes      | —       | Python version to use (e.g., `3.9`, `3.10`, `3.11`)                                                                                              |
| `pytest-args`          | No       | ``      | Additional arguments to pass to pytest (e.g., `-v --cov`)                                                                                        |
| `cache-pip`            | No       | `true`  | Enable pip caching for faster installations                                                                                                      |
| `extras`               | No       | `dev`   | Extras to install from pyproject.toml (e.g., `dev,test`)                                                                                         |
| `nexus-username`       | No       | ``      | Nexus username for resolving private packages                                                                                                    |
| `nexus-password`       | No       | ``      | Nexus password for resolving private packages                                                                                                    |
| `nexus-repository-url` | No       | ``      | Nexus base URL (e.g., `https://host/repository/wheels/`). When set, packages are also resolved via `--extra-index-url` pointing to `.../simple/` |

## Outputs

This action has no outputs.

## Usage

### Basic Example with Matrix

```yaml
name: Test Matrix

on: [push, pull_request]

jobs:
  extract-versions:
    runs-on: ubuntu-latest
    outputs:
      python-versions: ${{ steps.versions.outputs.versions-json }}
    steps:
      - uses: actions/checkout@v4

      - name: Extract Python versions
        uses: m4nh/shared-cicd/actions/python/extract-python-versions@main
        id: versions

  run-tests:
    name: Run Tests (Python ${{ matrix.python-version }})
    runs-on: ubuntu-latest
    needs: extract-versions
    strategy:
      fail-fast: false
      matrix:
        python-version: ${{ fromJson(needs.extract-versions.outputs.python-versions) }}
    steps:
      - uses: actions/checkout@v4

      - name: Run pytest
        uses: m4nh/shared-cicd/actions/python/run-pytest@main
        with:
          python-version: ${{ matrix.python-version }}
```

### With Custom Pytest Arguments

```yaml
- name: Run pytest with coverage
  uses: m4nh/shared-cicd/actions/python/run-pytest@main
  with:
    python-version: "3.11"
    pytest-args: "-v --cov=src --cov-report=xml"
```

### With Custom Extras

```yaml
- name: Run tests with all extras
  uses: m4nh/shared-cicd/actions/python/run-pytest@main
  with:
    python-version: "3.10"
    extras: "dev,test,typing"
```

### Disable Caching

```yaml
- name: Run tests without cache
  uses: m4nh/shared-cicd/actions/python/run-pytest@main
  with:
    python-version: "3.9"
    cache-pip: "false"
```

### With Nexus Private Package Registry

```yaml
- name: Run pytest (with private Nexus packages)
  uses: m4nh/shared-cicd/actions/python/run-pytest@main
  with:
    python-version: "3.11"
    nexus-username: ${{ secrets.NEXUS_USERNAME }}
    nexus-password: ${{ secrets.NEXUS_PASSWORD }}
    nexus-repository-url: ${{ secrets.NEXUS_REPOSITORY_URL }}
```

## What This Action Does

1. **Sets up Python** - Uses `actions/setup-python@v5` to install the specified Python version
2. **Enables pip caching** - Caches pip packages to speed up subsequent runs (configurable)
3. **Upgrades pip** - Ensures the latest pip version is installed
4. **Installs dependencies** - Installs the project with dev extras from `pyproject.toml`
5. **Runs pytest** - Executes pytest with any additional arguments provided

## Prerequisites

Your project must have:

- A `pyproject.toml` file in the repository root
- A `[project.optional-dependencies]` or `[tool.poetry.group.dev.dependencies]` section with a `dev` group (or custom extras)
- Pytest configured in your project

Example `pyproject.toml` structure:

```toml
[project]
name = "my-project"
version = "1.0.0"

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov",
    "pytest-mock",
]
```

## Complete Workflow Example

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  extract-versions:
    runs-on: ubuntu-latest
    outputs:
      python-versions: ${{ steps.versions.outputs.versions-json }}
      min-version: ${{ steps.versions.outputs.min-version }}
    steps:
      - uses: actions/checkout@v4

      - name: Extract Python versions
        uses: m4nh/shared-cicd/actions/python/extract-python-versions@main
        id: versions

  test:
    name: Test (Python ${{ matrix.python-version }})
    runs-on: ubuntu-latest
    needs: extract-versions
    strategy:
      fail-fast: false
      matrix:
        python-version: ${{ fromJson(needs.extract-versions.outputs.python-versions) }}
    steps:
      - uses: actions/checkout@v4

      - name: Run tests
        uses: m4nh/shared-cicd/actions/python/run-pytest@main
        with:
          python-version: ${{ matrix.python-version }}
          pytest-args: "-v --cov=src"

  lint:
    runs-on: ubuntu-latest
    needs: extract-versions
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ needs.extract-versions.outputs.min-version }}

      - name: Run linting
        run: |
          pip install ruff
          ruff check .
```

## Error Handling

The action will fail if:

- Python setup fails for the specified version
- `pyproject.toml` is missing or invalid
- Dependency installation fails
- Pytest execution fails (test failures)

All output from pip and pytest will be visible in the Action logs for debugging.

## Tips

- **Combine with extract-python-versions**: Use the `extract-python-versions` action to dynamically generate the matrix from your `pyproject.toml` `requires-python` field
- **Speed up CI**: Enable caching by default (`cache-pip: "true"`) for faster test runs
- **Parallel testing**: Use `pytest -n auto` with pytest-xdist for parallel test execution (add to `pytest-args`)
- **Coverage reports**: Use `--cov` arguments to generate coverage reports for upload to coverage services

## Related Actions

- **extract-python-versions** - Automatically extract Python versions from `pyproject.toml`
