# Snapshot Version (PEP 440) Action

A composite GitHub Action that computes the next snapshot dev version using conventional commits and [PEP 440](https://peps.python.org/pep-0440/) format. Designed for Python projects.

## Overview

This action:

- Reads the latest semantic version tag from git
- Parses all conventional commits since that tag to determine the required bump (`major`, `minor`, or `patch`)
- Outputs a PEP 440-compliant dev version for use in Python packaging tools (`pip`, `twine`, `setuptools-scm`)
- Also outputs a Docker-compatible variant (replaces `+` with `-` since Docker Hub rejects the `+` character in tags)

### Bump rules

| Commit type     | Example                                     | Bump    |
| --------------- | ------------------------------------------- | ------- |
| Breaking change | `feat!: drop X` / `BREAKING CHANGE` in body | `major` |
| Feature         | `feat: add Y`                               | `minor` |
| Anything else   | `fix:`, `chore:`, `refactor:`, …            | `patch` |

The **highest** bump found across all commits since the last tag wins.

### Version format

| Output           | Format           | Example              |
| ---------------- | ---------------- | -------------------- |
| `version`        | `X.Y.Z.devN+sha` | `0.5.0.dev5+abc1234` |
| `docker-version` | `X.Y.Z.devN-sha` | `0.5.0.dev5-abc1234` |

## Inputs

| Input              | Required | Default | Description                                               |
| ------------------ | -------- | ------- | --------------------------------------------------------- |
| `tag-prefix`       | No       | `v`     | Prefix for semantic version tags (e.g., `v` for `v1.0.0`) |
| `fallback-version` | No       | `0.0.0` | Version to use when no matching tags are found            |

## Outputs

| Output           | Description                                     | Example              |
| ---------------- | ----------------------------------------------- | -------------------- |
| `version`        | PEP 440 dev version                             | `0.5.0.dev5+abc1234` |
| `docker-version` | Docker-compatible version (`+` replaced by `-`) | `0.5.0.dev5-abc1234` |

## Usage

### Basic Example

```yaml
jobs:
  compute-version:
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.snapshot.outputs.version }}
      docker-version: ${{ steps.snapshot.outputs.docker-version }}
    steps:
      - name: Compute snapshot version
        id: snapshot
        uses: m4nh/shared-cicd/actions/git/snapshot-version-pep440@main

      - name: Print version
        run: echo "${{ steps.snapshot.outputs.version }}"
```

### With Custom Tag Prefix

```yaml
- name: Compute snapshot version
  id: snapshot
  uses: m4nh/shared-cicd/actions/git/snapshot-version-pep440@main
  with:
    tag-prefix: "release-"
```

### With Fallback Version

```yaml
- name: Compute snapshot version
  id: snapshot
  uses: m4nh/shared-cicd/actions/git/snapshot-version-pep440@main
  with:
    fallback-version: "0.1.0"
```

### Full Snapshot Workflow Example

```yaml
name: Snapshot

on:
  push:
    branches: [develop]

jobs:
  compute-version:
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.snapshot.outputs.version }}
      docker-version: ${{ steps.snapshot.outputs.docker-version }}
    steps:
      - name: Compute snapshot version
        id: snapshot
        uses: m4nh/shared-cicd/actions/git/snapshot-version-pep440@main

  build:
    runs-on: ubuntu-latest
    needs: compute-version
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Build wheel
        uses: m4nh/shared-cicd/actions/python/build-wheel@main
        with:
          version: ${{ needs.compute-version.outputs.version }}
```
