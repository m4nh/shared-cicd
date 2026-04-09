# Build Python Wheel Action

A simple, focused GitHub Action that builds a Python wheel and outputs the path for use in downstream actions like uploading to artifact storage or package registries.

## Overview

This action does one thing well:

- Builds a Python wheel (binary distribution only)
- Outputs the path to the built wheel
- Simple, minimal configuration

Perfect for release workflows or any pipeline that needs to build and upload wheels.

## Inputs

| Input            | Required | Default           | Description                            |
| ---------------- | -------- | ----------------- | -------------------------------------- |
| `python-version` | No       | `3.11`            | Python version to use                  |
| `build-tools`    | No       | `build hatch-vcs` | Build tools to install                 |
| `version`        | No       | ``                | Override package version for the build |

## Outputs

| Output        | Description                              | Example                                                                     |
| ------------- | ---------------------------------------- | --------------------------------------------------------------------------- |
| `wheel-path`  | Path to the first built wheel            | `dist/my_pkg-1.0.0-py3-none-any.whl`                                        |
| `wheel-paths` | Space-separated list of all wheels built | `dist/my_pkg-1.0.0-py3-none-any.whl dist/my_pkg-1.0.0-py2.py3-none-any.whl` |

## Usage

### Basic: Build and Check

```yaml
- uses: m4nh/shared-cicd/actions/python/build-wheel@main
```

### Upload to GitHub Artifacts

```yaml
- name: Build wheel
  uses: m4nh/shared-cicd/actions/python/build-wheel@main
  id: build

- name: Upload artifact
  uses: actions/upload-artifact@v4
  with:
    name: dist
    path: dist/
```

### With Version from Another Job

```yaml
- name: Build wheel
  uses: m4nh/shared-cicd/actions/python/build-wheel@main
  with:
    version: ${{ needs.release.outputs.version }}
  id: build

- name: Upload to PyPI
  uses: pypa/gh-action-pypi-publish@release/v1
  with:
    packages-dir: dist/
```

### Custom Build Tools

```yaml
- name: Build with Poetry
  uses: m4nh/shared-cicd/actions/python/build-wheel@main
  with:
    build-tools: "poetry-core"
```

## Complete Release Workflow Example

```yaml
name: Release

on:
  push:
    tags:
      - "v*"

jobs:
  extract-version:
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.version.outputs.version }}
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Get version from tag
        id: version
        run: echo "version=${GITHUB_REF#refs/tags/v}" >> $GITHUB_OUTPUT

  build:
    name: Build Wheel
    runs-on: ubuntu-latest
    needs: extract-version
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Build wheel
        uses: m4nh/shared-cicd/actions/python/build-wheel@main
        with:
          version: ${{ needs.extract-version.outputs.version }}
        id: build

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/

      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          packages-dir: dist/
          password: ${{ secrets.PYPI_API_TOKEN }}

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          files: ${{ steps.build.outputs.wheel-path }}
```

## Using Outputs in Scripts

```yaml
- name: Build wheel
  uses: m4nh/shared-cicd/actions/python/build-wheel@main
  id: build

- name: Inspect wheel
  run: |
    echo "Wheel: ${{ steps.build.outputs.wheel-path }}"
    unzip -l "${{ steps.build.outputs.wheel-path }}" | head -20
```

## Typical Workflow

```yaml
job:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build wheel
        uses: m4nh/shared-cicd/actions/python/build-wheel@main
        id: build
        with:
    version: "1.2.3"
            https://your-artifact-server.com/upload
```

## Prerequisites

Your project must have:

- `pyproject.toml` with build system configuration

Example minimal `pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=45", "wheel", "setuptools_scm[toml]>=6.2"]
build-backend = "setuptools.build_meta"

[project]
name = "my-package"
version = "1.0.0"
```

## Tips

- **Single responsibility**: This action only builds wheels, keeping things simple
- **Multiple wheels**: Use `wheel-paths` output if your project builds multiple wheels (e.g., universal wheels)
- **Version handling**: Pass `version` from another job to control versioning
- **CI integration**: Combine with test actions to verify before building
- **Small and fast**: Minimal overhead, caches pip for speed

## Related Actions

- **extract-python-versions** - Extract test versions from `pyproject.toml`
- **run-pytest** - Run tests before building
- **run-security-scan** - Security check before release
