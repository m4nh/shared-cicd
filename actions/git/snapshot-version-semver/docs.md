# Snapshot Version (SemVer) Action

A composite GitHub Action that computes the next snapshot dev version using conventional commits and [SemVer](https://semver.org/) pre-release format. Designed for JavaScript / Node.js projects (npm, yarn).

## Overview

This action:

- Reads the latest semantic version tag from git
- Parses all conventional commits since that tag to determine the required bump (`major`, `minor`, or `patch`)
- Outputs a SemVer pre-release dev version for use in npm/yarn compatible registries
- Also outputs a Docker-compatible variant (replaces `+` with `-` since Docker Hub rejects the `+` character in tags)

### Bump rules

| Commit type     | Example                                     | Bump    |
| --------------- | ------------------------------------------- | ------- |
| Breaking change | `feat!: drop X` / `BREAKING CHANGE` in body | `major` |
| Feature         | `feat: add Y`                               | `minor` |
| Anything else   | `fix:`, `chore:`, `refactor:`, …            | `patch` |

The **highest** bump found across all commits since the last tag wins.

### Version format

| Output           | Format            | Example               |
| ---------------- | ----------------- | --------------------- |
| `version`        | `X.Y.Z-dev.N+sha` | `0.5.0-dev.5+abc1234` |
| `docker-version` | `X.Y.Z-dev.N-sha` | `0.5.0-dev.5-abc1234` |

## Inputs

| Input              | Required | Default | Description                                               |
| ------------------ | -------- | ------- | --------------------------------------------------------- |
| `tag-prefix`       | No       | `v`     | Prefix for semantic version tags (e.g., `v` for `v1.0.0`) |
| `fallback-version` | No       | `0.0.0` | Version to use when no matching tags are found            |

## Outputs

| Output           | Description                                     | Example               |
| ---------------- | ----------------------------------------------- | --------------------- |
| `version`        | SemVer pre-release dev version                  | `0.5.0-dev.5+abc1234` |
| `docker-version` | Docker-compatible version (`+` replaced by `-`) | `0.5.0-dev.5-abc1234` |

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
        uses: m4nh/shared-cicd/actions/git/snapshot-version-semver@main

      - name: Print version
        run: echo "${{ steps.snapshot.outputs.version }}"
```

### With Custom Tag Prefix

```yaml
- name: Compute snapshot version
  id: snapshot
  uses: m4nh/shared-cicd/actions/git/snapshot-version-semver@main
  with:
    tag-prefix: "release-"
```

### With Fallback Version

```yaml
- name: Compute snapshot version
  id: snapshot
  uses: m4nh/shared-cicd/actions/git/snapshot-version-semver@main
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
        uses: m4nh/shared-cicd/actions/git/snapshot-version-semver@main

  build:
    runs-on: ubuntu-latest
    needs: compute-version
    steps:
      - uses: actions/checkout@v4

      - name: Build package
        uses: m4nh/shared-cicd/actions/yarn/build-package@main
        with:
          version: ${{ needs.compute-version.outputs.version }}
```
