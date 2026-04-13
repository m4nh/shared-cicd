# Run Security Scan Action

A composite GitHub Action that performs comprehensive security scanning on Python projects using industry-standard tools: `pip-audit` for dependency vulnerabilities and `bandit` for static code analysis.

## Overview

This action simplifies security scanning by:

- Checking Python dependencies for known vulnerabilities (pip-audit)
- Performing static security analysis on your codebase (bandit)
- Providing flexible configuration for both tools
- Running on a stable Python version (3.11 by default)

Perfect for integrating into CI/CD pipelines to catch security issues early.

## Inputs

| Input                  | Required | Default  | Description                                                                                                                                      |
| ---------------------- | -------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| `python-version`       | No       | `3.11`   | Python version to use for scanning                                                                                                               |
| `scan-source-code`     | No       | `true`   | Enable bandit static security analysis                                                                                                           |
| `source-path`          | No       | `src/`   | Path to scan with bandit (e.g., `src/`, `.`)                                                                                                     |
| `audit-dependencies`   | No       | `true`   | Enable pip-audit dependency scanning                                                                                                             |
| `bandit-args`          | No       | `-ll -q` | Additional arguments for bandit                                                                                                                  |
| `pip-audit-args`       | No       | ``       | Additional arguments for pip-audit                                                                                                               |
| `install-project`      | No       | `false`  | Install the project before scanning                                                                                                              |
| `nexus-username`       | No       | ``       | Nexus username for resolving private packages (used when `install-project` is `true`)                                                            |
| `nexus-password`       | No       | ``       | Nexus password for resolving private packages                                                                                                    |
| `nexus-repository-url` | No       | ``       | Nexus base URL (e.g., `https://host/repository/wheels/`). When set, packages are also resolved via `--extra-index-url` pointing to `.../simple/` |

## Outputs

This action has no outputs.

## Usage

### Basic Example

```yaml
- name: Run security scan
  uses: m4nh/shared-cicd/actions/python/run-security-scan@main
```

### Custom Source Path

```yaml
- name: Run security scan on custom path
  uses: m4nh/shared-cicd/actions/python/run-security-scan@main
  with:
    source-path: "custom_src/ app/"
```

### With Custom Arguments

```yaml
- name: Run verbose security scan
  uses: m4nh/shared-cicd/actions/python/run-security-scan@main
  with:
    bandit-args: "-v"
    pip-audit-args: "--desc"
```

### Skip Specific Scans

```yaml
- name: Only check dependencies
  uses: m4nh/shared-cicd/actions/python/run-security-scan@main
  with:
    scan-source-code: "false"
    audit-dependencies: "true"
```

### With Project Installation

```yaml
- name: Security scan with project installed
  uses: m4nh/shared-cicd/actions/python/run-security-scan@main
  with:
    install-project: "true"
```

## What This Action Does

1. **Sets up Python** - Uses specified Python version (3.11 by default) with pip caching
2. **Installs security tools** - Installs `pip-audit` and `bandit`
3. **Optionally installs project** - Can install your project dependencies if needed
4. **Runs pip-audit** - Scans dependencies for known vulnerabilities
5. **Runs bandit** - Performs static security analysis on your source code

## Security Tools Included

### pip-audit

Audits Python dependencies for known vulnerabilities by checking against public vulnerability databases.

**Default behavior**: Quick scan with minimal output

**Common arguments**:

- `--desc` - Show vulnerability descriptions
- `--fix` - Automatically fix vulnerable dependencies
- `-r requirements.txt` - Scan specific requirements file

### bandit

Scans Python source code for common security issues like hardcoded passwords, SQL injection vulnerabilities, and insecure function usage.

**Default behavior**: Runs with level LOW and higher (`-ll`), quiet mode (`-q`)

**Common arguments**:

- `-v` - Verbose output
- `-ll` / `-lll` / `-llll` - Different severity levels
- `-f json` - Output as JSON
- `-s B101` - Skip specific tests (B101 = assert_used)

## Complete Workflow Example

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  security:
    name: Security Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run security scan
        uses: m4nh/shared-cicd/actions/python/run-security-scan@main
        with:
          python-version: "3.11"
          source-path: "src/"
          bandit-args: "-v"

  test:
    name: Test (Python ${{ matrix.python-version }})
    runs-on: ubuntu-latest
    needs: security
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.9", "3.10", "3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4

      - uses: m4nh/shared-cicd/actions/python/run-pytest@main
        with:
          python-version: ${{ matrix.python-version }}
```

## Configuration Examples

### Strict Security Scanning

```yaml
- name: Strict security scan
  uses: m4nh/shared-cicd/actions/python/run-security-scan@main
  with:
    bandit-args: "-v -ll"
    pip-audit-args: "--desc"
    scan-source-code: "true"
    audit-dependencies: "true"
```

### Scan Multiple Paths

```yaml
- name: Scan all Python code
  uses: m4nh/shared-cicd/actions/python/run-security-scan@main
  with:
    source-path: "src/ app/ tests/"
```

### Custom Python Version

```yaml
- name: Security scan on Python 3.9
  uses: m4nh/shared-cicd/actions/python/run-security-scan@main
  with:
    python-version: "3.9"
```

## Ignoring Issues

### Bandit

To ignore specific bandit issues, add comments in your code:

```python
# This is a deliberate security exception
_ = eval(user_input)  # nosec B307
```

Or create a `.bandit` configuration file:

```yaml
exclude_dirs:
  - "/test"

tests:
  - B201
  - B301

skips:
  - B404
```

### pip-audit

To ignore specific vulnerabilities, create a `pyproject.toml` or `audit.toml`:

```toml
[tool.pip-audit]
ignore-vulns = ["54321"]
ignore-packages = ["package-name"]
```

## Error Handling

The action will fail if:

- Security vulnerabilities are found by pip-audit
- Security issues are found by bandit
- Tool installation fails
- Python setup fails for the specified version

All output from the security tools will be visible in the Action logs for debugging.

## Tips

- **Run on stable version**: Security scanning uses Python 3.11 by default to ensure consistent results
- **Combine with testing**: Use alongside `run-pytest` action in the same workflow
- **Early detection**: Run security scans on every PR to catch issues before merging
- **Gradually fix issues**: Use `scan-source-code: "false"` to focus on dependencies first, then enable source scanning
- **Custom rules**: Create `.bandit` files for project-specific security policies

## Related Actions

- **run-pytest** - Run tests across Python versions
- **extract-python-versions** - Automatically extract test versions from `pyproject.toml`

## Prerequisites

- Python project with `pyproject.toml` (for dependency information)
- Source code in a standard location (e.g., `src/`, `app/`, etc.)
