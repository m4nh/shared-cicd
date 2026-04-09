# Extract Python Versions Action

Automatically extract Python version constraints from a `pyproject.toml` file and output them in multiple formats for use in GitHub Actions workflows.

## Overview

This action parses the `requires-python` field from your `pyproject.toml` and generates:

- A comma-separated version list for direct use in matrix strategies
- A JSON array for programmatic access
- Minimum and maximum version numbers

## Inputs

This action has no inputs. It automatically looks for `pyproject.toml` in the repository root.

## Outputs

| Output            | Description                                         | Example                        |
| ----------------- | --------------------------------------------------- | ------------------------------ |
| `versions-matrix` | Comma-separated Python versions                     | `3.9,3.10,3.11,3.12`           |
| `versions-json`   | JSON array of Python versions (backward compatible) | `["3.9","3.10","3.11","3.12"]` |
| `min-version`     | Minimum Python version                              | `3.9`                          |
| `max-version`     | Maximum Python version                              | `3.12`                         |

## Usage

### Basic Example

```yaml
- name: Extract Python versions
  uses: m4nh/shared-cicd/actions/python/extract-python-versions@main
  id: versions

- name: Test with multiple Python versions
  strategy:
    matrix:
      python: ${{ fromJson(steps.versions.outputs.versions-json) }}
  run: |
    python -m pytest
```

### Using Direct Matrix Output

```yaml
- name: Extract Python versions
  uses: m4nh/shared-cicd/actions/python/extract-python-versions@main
  id: versions

- name: Show available versions
  run: echo "Testing versions: ${{ steps.versions.outputs.versions-matrix }}"
```

### Using Min/Max Versions

```yaml
- name: Extract Python versions
  uses: m4nh/shared-cicd/actions/python/extract-python-versions@main
  id: versions

- name: Setup Python
  uses: actions/setup-python@v4
  with:
    python-version: ${{ steps.versions.outputs.min-version }}

- name: Display version range
  run: |
    echo "Python range: ${{ steps.versions.outputs.min-version }} to ${{ steps.versions.outputs.max-version }}"
```

## PyProject.toml Format

The action expects a `requires-python` field in your `pyproject.toml`:

### Supported Formats

```toml
# Standard format (recommended)
requires-python = ">=3.9,<3.13"

# With spaces
requires-python = ">= 3.9, < 3.13"

# Single quotes
requires-python = '>=3.9,<3.13'

# Greater than / less than variation
requires-python = ">3.8,<3.13"
requires-python = ">=3.9,<=3.12"
```

### Version Range Behavior

- **Single major version**: Generates all minor versions between min and max

  - `requires-python = ">=3.9,<3.13"` → `3.9, 3.10, 3.11, 3.12`

- **Multiple major versions**: Generates versions across major versions
  - `requires-python = ">=3.9,<4.2"` → `3.9, 3.10, ..., 4.0, 4.1`

## Error Handling

If the action encounters an error:

- **Missing `pyproject.toml`**: All outputs will be empty, and an error is logged
- **Invalid version specifier**: Outputs will be empty with a warning message
- **No `requires-python` field**: All outputs will be empty

Errors are logged to stderr but do not cause the workflow to fail.

## Examples in Different Workflows

### Combined with setup-python

```yaml
name: Test Matrix

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Extract Python versions
        uses: m4nh/shared-cicd/actions/python/extract-python-versions@main
        id: versions

      - name: Set up Python matrix
        uses: actions/setup-python@v4
        with:
          python-version: |
            ${{ steps.versions.outputs.versions-json }}

      - name: Run tests
        run: pytest
```

### Conditional Steps Based on Version Range

```yaml
- name: Extract Python versions
  uses: m4nh/shared-cicd/actions/python/extract-python-versions@main
  id: versions

- name: Display supported versions
  run: |
    echo "Package supports Python ${{ steps.versions.outputs.min-version }} to ${{ steps.versions.outputs.max-version }}"
```

## Implementation Details

The action uses:

- Pure Python 3 with only standard library dependencies
- Regex-based parsing for robustness
- Support for flexible spacing and quote styles
- Proper version comparison for generating version lists

## Limitations

- Currently assumes minor versions don't exceed 20 (common for Python)
- Requires `pyproject.toml` to exist in the repository root
- Only supports standard `>=X.Y,<Z.W` style version constraints
