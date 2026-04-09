# CI Python Workflow

A reusable GitHub Actions workflow for Python projects that orchestrates all the shared CI/CD actions.

## Overview

This workflow provides a complete CI/CD pipeline for Python projects including:

- Python version extraction from `pyproject.toml`
- Code linting (configurable linter)
- Testing across multiple Python versions
- Security scanning
- Wheel building
- Docker image building (optional)

## Features

- ✅ Reusable across multiple repositories
- ✅ Fully configurable behavior via inputs
- ✅ Supports multiple linters and versions
- ✅ Parallel execution for speed
- ✅ Optional features (security, Docker, etc.)

## Using This Workflow

### In Another Repository

Create a workflow file in your repo at `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  pull_request:
    branches: [develop, main]
  push:
    branches: [main]

jobs:
  ci:
    uses: m4nh/shared-cicd/.github/workflows/ci-python.yml@main
```

### With Default Configuration

Uses all defaults:

- Python 3.11 for non-matrix jobs
- Ruff for linting
- Tests run on all versions from `pyproject.toml`
- Security scanning enabled
- Wheel building enabled
- Docker disabled (unless you provide docker-tags)

### Custom Configuration

```yaml
jobs:
  ci:
    uses: m4nh/shared-cicd/.github/workflows/ci-python.yml@main
    with:
      runner: "ubuntu-latest"
      python-version: "3.11"
      linter: "black"
      lint-path: "src/"
      tests-enabled: true
      security-enabled: true
      build-wheel-enabled: true
      build-docker-enabled: true
      docker-tags: "myimage:latest,myimage:${{ github.sha }}"
```

## Inputs

### General

| Input            | Type   | Default         | Description                                |
| ---------------- | ------ | --------------- | ------------------------------------------ |
| `runner`         | string | `ubuntu-latest` | GitHub runner to use                       |
| `python-version` | string | `3.11`          | Default Python version for non-matrix jobs |

### Linting

| Input          | Type    | Default | Description                          |
| -------------- | ------- | ------- | ------------------------------------ |
| `lint-enabled` | boolean | `true`  | Enable linting                       |
| `linter`       | string  | `ruff`  | Linter (ruff, flake8, pylint, black) |
| `linter-args`  | string  | ``      | Additional linter arguments          |
| `lint-path`    | string  | `.`     | Path to lint                         |

### Testing

| Input           | Type    | Default | Description    |
| --------------- | ------- | ------- | -------------- |
| `tests-enabled` | boolean | `true`  | Enable testing |

### Security

| Input                  | Type    | Default | Description              |
| ---------------------- | ------- | ------- | ------------------------ |
| `security-enabled`     | boolean | `true`  | Enable security scanning |
| `security-source-path` | string  | `src/`  | Path for bandit analysis |

### Building

| Input                  | Type    | Default | Description            |
| ---------------------- | ------- | ------- | ---------------------- |
| `build-wheel-enabled`  | boolean | `true`  | Enable wheel building  |
| `build-docker-enabled` | boolean | `false` | Enable Docker building |
| `docker-tags`          | string  | ``      | Docker image tags      |
| `docker-build-args`    | string  | ``      | Docker build arguments |

## Complete Examples

### Basic Python Project

```yaml
name: CI

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  ci:
    uses: m4nh/shared-cicd/.github/workflows/ci-python.yml@main
```

### With Custom Linter (Black)

```yaml
jobs:
  ci:
    uses: m4nh/shared-cicd/.github/workflows/ci-python.yml@main
    with:
      linter: "black"
      linter-args: "--line-length=100"
```

### Disable Security but Keep Everything Else

```yaml
jobs:
  ci:
    uses: m4nh/shared-cicd/.github/workflows/ci-python.yml@main
    with:
      security-enabled: false
```

### With Docker Building

```yaml
jobs:
  ci:
    uses: m4nh/shared-cicd/.github/workflows/ci-python.yml@main
    with:
      build-docker-enabled: true
      docker-tags: "ghcr.io/${{ github.repository }}:latest,ghcr.io/${{ github.repository }}:${{ github.sha }}"
      docker-build-args: "--build-arg VERSION=${{ github.ref_name }}"
```

### Minimal Configuration (Lint Only)

```yaml
jobs:
  ci:
    uses: m4nh/shared-cicd/.github/workflows/ci-python.yml@main
    with:
      tests-enabled: false
      security-enabled: false
      build-wheel-enabled: false
```

### Full-Featured Pipeline

```yaml
name: CI/CD

on:
  pull_request:
    branches: [develop, main]
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  ci:
    uses: m4nh/shared-cicd/.github/workflows/ci-python.yml@main
    with:
      runner: "ubuntu-latest"
      python-version: "3.11"
      lint-enabled: true
      linter: "ruff"
      linter-args: "--select E,W,F"
      lint-path: "src/ tests/"
      tests-enabled: true
      security-enabled: true
      security-source-path: "src/"
      build-wheel-enabled: true
      build-docker-enabled: true
      docker-tags: "myapp:latest,myapp:${{ github.sha }}"
      docker-build-args: "--build-arg ENV=production"
```

## Workflow Structure

The workflow runs in this order:

1. **Extract Versions** (always runs)

   - Extracts Python versions from source `pyproject.toml`
   - Outputs: `python-versions`, `min-version`, `max-version`

2. **Lint** (if enabled)

   - Runs configured linter on specified path
   - Uses Python 3.11

3. **Test** (if enabled)

   - Runs pytest on all Python versions from step 1
   - Matrix strategy for parallel execution

4. **Security** (if enabled)

   - Runs pip-audit and bandit
   - Uses Python 3.11

5. **Build Wheel** (if enabled)

   - Builds Python wheel
   - Uses Python 3.11

6. **Build Docker** (if enabled)
   - Builds Docker image
   - Requires `docker-tags` to be set

## Prerequisites in Your Repository

Your project must have:

- `pyproject.toml` with `requires-python` field (for version extraction)
- `pyproject.toml` with test configuration (for pytest)
- Linter configuration in `pyproject.toml` or defaults

Example `pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=45", "wheel", "setuptools_scm[toml]>=6.2"]
build-backend = "setuptools.build_meta"

[project]
name = "my-package"
version = "1.0.0"
requires-python = ">=3.9,<3.13"

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov",
    "ruff",
]

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.ruff]
line-length = 100
target-version = "py39"
```

## Security Considerations

Secrets are not needed for this workflow unless you're pushing to registries or other external services. The workflow runs on pull requests and commits safely by default.

## Troubleshooting

### Tests not running

- Check `requires-python` field in `pyproject.toml`
- Ensure `pyproject.toml` exists in repository root

### Linting fails

- Check linter configuration in `pyproject.toml`
- Verify `lint-path` points to correct directory

### Python versions not extracted

- Ensure `pyproject.toml` has `requires-python` field
- Format must be: `requires-python = ">=X.Y,<Z.W"`

### Docker build fails

- Verify `Dockerfile` exists in repository root
- Check `docker-tags` input is provided
- Ensure Docker build context is correct

## Tips

- **Use per-branch configuration**: Different configs for main vs develop
- **Reuse across projects**: Save as template and customize inputs
- **Disable features as needed**: Not every project needs Docker or security scans
- **Group similar settings**: Keep related inputs together
- **Use GitHub environments**: Different settings for different environments

## Related Resources

- [extract-python-versions](../actions/python/extract-python-versions/docs.md)
- [python-lint](../actions/python/python-lint/docs.md)
- [run-pytest](../actions/python/run-pytest/docs.md)
- [run-security-scan](../actions/python/run-security-scan/docs.md)
- [build-wheel](../actions/python/build-wheel/docs.md)
- [build-docker-image](../actions/docker/build-docker-image/docs.md)
