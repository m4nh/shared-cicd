# Python Lint Action

A flexible GitHub Action for Python linting with support for multiple linters (ruff, flake8, pylint, black) and optional auto-fixing.

## Overview

This action simplifies Python linting by:

- Supporting multiple linting tools
- Allowing custom linter arguments
- Optional auto-fixing of issues
- Single configurable interface

## Inputs

| Input            | Required | Default | Description                                 |
| ---------------- | -------- | ------- | ------------------------------------------- |
| `python-version` | No       | `3.11`  | Python version to use                       |
| `linter`         | No       | `ruff`  | Linter to use (ruff, flake8, pylint, black) |
| `linter-args`    | No       | ``      | Additional arguments for the linter         |
| `path`           | No       | `.`     | Path to lint                                |
| `fix`            | No       | `false` | Auto-fix issues if supported                |

## Outputs

This action has no outputs.

## Supported Linters

### Ruff (Recommended)

Fast Python linter written in Rust.

```yaml
- uses: m4nh/shared-cicd/actions/python/python-lint@main
  with:
    linter: "ruff"
    linter-args: "--select E,W,F"
```

### Flake8

Classic Python style guide enforcement.

```yaml
- uses: m4nh/shared-cicd/actions/python/python-lint@main
  with:
    linter: "flake8"
    linter-args: "--max-line-length=120"
```

### Pylint

Comprehensive Python code analysis.

```yaml
- uses: m4nh/shared-cicd/actions/python/python-lint@main
  with:
    linter: "pylint"
    linter-args: "--disable=missing-docstring"
```

### Black

Code formatter (opinionated Python formatting).

```yaml
- uses: m4nh/shared-cicd/actions/python/python-lint@main
  with:
    linter: "black"
    linter-args: "--line-length=100"
```

## Usage

### Basic Ruff Linting

```yaml
- uses: m4nh/shared-cicd/actions/python/python-lint@main
```

### Lint Specific Directory

```yaml
- uses: m4nh/shared-cicd/actions/python/python-lint@main
  with:
    path: "src/"
```

### Auto-fix with Ruff

```yaml
- uses: m4nh/shared-cicd/actions/python/python-lint@main
  with:
    linter: "ruff"
    fix: "true"
```

### Format with Black

```yaml
- uses: m4nh/shared-cicd/actions/python/python-lint@main
  with:
    linter: "black"
    fix: "true"
```

### Custom Ruff Rules

```yaml
- uses: m4nh/shared-cicd/actions/python/python-lint@main
  with:
    linter: "ruff"
    linter-args: "--select E,W,F --ignore E501"
```

### Flake8 with Custom Config

```yaml
- uses: m4nh/shared-cicd/actions/python/python-lint@main
  with:
    linter: "flake8"
    linter-args: "--config .flake8"
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
    steps:
      - uses: actions/checkout@v4

      - name: Extract Python versions
        uses: m4nh/shared-cicd/actions/python/extract-python-versions@main
        id: versions

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Lint with Ruff
        uses: m4nh/shared-cicd/actions/python/python-lint@main
        with:
          linter: "ruff"
          path: "src/ tests/"

  test:
    name: Test (Python ${{ matrix.python-version }})
    runs-on: ubuntu-latest
    needs: [extract-versions, lint]
    strategy:
      fail-fast: false
      matrix:
        python-version: ${{ fromJson(needs.extract-versions.outputs.python-versions) }}
    steps:
      - uses: actions/checkout@v4

      - uses: m4nh/shared-cicd/actions/python/run-pytest@main
        with:
          python-version: ${{ matrix.python-version }}
```

## Linter-Specific Notes

### Ruff

- **Fast**: Extremely fast Python linter (written in Rust)
- **Modern**: Replaces flake8, isort, and black checker
- **Auto-fix**: Supports `--fix` for automatic corrections
- **Recommended default**

### Flake8

- **Classic**: Long-standing linter with wide adoption
- **Plugins**: Supports many configuration options
- **No auto-fix**: Does not support automatic fixing

### Pylint

- **Comprehensive**: Deep code analysis
- **Slow**: Can be slower than Ruff
- **Plugin system**: Extensible with plugins
- **No auto-fix**: Does not support automatic fixing

### Black

- **Formatter**: Opinionated code formatting
- **Zero config**: Minimal configuration options
- **Auto-fix**: Can format code with `fix: "true"`
- **Best for**: Enforcing consistent code style

## Auto-fix Support

| Linter | Auto-fix Support |
| ------ | ---------------- |
| ruff   | ✅ Yes           |
| black  | ✅ Yes           |
| flake8 | ❌ No            |
| pylint | ❌ No            |

## Multiple Paths

```yaml
- uses: m4nh/shared-cicd/actions/python/python-lint@main
  with:
    path: "src/ tests/ scripts/"
```

## Custom Linter Arguments

```yaml
# Ruff with multiple options
- uses: m4nh/shared-cicd/actions/python/python-lint@main
  with:
    linter: "ruff"
    linter-args: "--select E,W,F --ignore E501 --max-line-length=120"

# Pylint with config file
- uses: m4nh/shared-cicd/actions/python/python-lint@main
  with:
    linter: "pylint"
    linter-args: "--rcfile=.pylintrc"

# Black with custom line length
- uses: m4nh/shared-cicd/actions/python/python-lint@main
  with:
    linter: "black"
    linter-args: "--line-length=100 --target-version py311"
```

## Configuration Files

Most linters support configuration files in your repository:

- **Ruff**: `pyproject.toml` ([ruff] section) or `.ruff.toml`
- **Flake8**: `.flake8` or `setup.cfg`
- **Pylint**: `.pylintrc` or `pyproject.toml` ([tool.pylint] section)
- **Black**: `pyproject.toml` ([tool.black] section)

## Tips

- **Use Ruff by default**: It's fast, modern, and replaces multiple tools
- **Combine with format**: Use Black for formatting + Ruff for linting
- **Auto-fix in CI**: Consider running with `fix: "true"` to auto-commit fixes
- **Configuration**: Store linter config in `pyproject.toml` for centralized setup
- **Pre-commit hooks**: Use linters locally before pushing

## Related Actions

- **run-pytest** - Run tests across Python versions
- **run-security-scan** - Security code analysis
- **extract-python-versions** - Extract test versions from `pyproject.toml`
