# Release Workflow - Python

A reusable GitHub Actions workflow that orchestrates the complete process of creating a new release including semantic versioning, building Docker images, publishing packages, and creating GitHub releases.

## Overview

This workflow automates the full release process:

- **Semantic Versioning**: Automatically determines version based on conventional commits
- **Docker Build & Push**: Builds and pushes Docker image to registry (if enabled)
- **Package Build & Publish**: Builds Python wheel and publishes to Nexus (if enabled)
- **GitHub Release**: Creates GitHub release with metadata from semantic release

## Using This Workflow

### In Another Repository

Create a workflow file in your repo at `.github/workflows/release.yml`:

```yaml
name: Release

on:
  push:
    branches:
      - main

jobs:
  release:
    uses: m4nh/shared-cicd/.github/workflows/release-python.yml@main
    secrets:
      DOCKER_USERNAME: ${{ secrets.DOCKER_USERNAME }}
      DOCKER_PASSWORD: ${{ secrets.DOCKER_PASSWORD }}
      NEXUS_USERNAME: ${{ secrets.NEXUS_USERNAME }}
      NEXUS_PASSWORD: ${{ secrets.NEXUS_PASSWORD }}
      NEXUS_REPOSITORY_URL: ${{ secrets.NEXUS_REPOSITORY_URL }}
    with:
      docker-target-repository: "myorg/myapp"
      docker-registry: "docker.io"
```

### With All Options

```yaml
jobs:
  release:
    uses: m4nh/shared-cicd/.github/workflows/release-python.yml@main
    with:
      runner: "ubuntu-latest"
      docker-enabled: true
      docker-target-repository: "myorg/myapp"
      docker-registry: "docker.io"
      docker-dockerfile: "Dockerfile"
      docker-context: "."
      docker-build-args: "--build-arg ENV=prod"
      publish-package-enabled: true
    secrets:
      DOCKER_USERNAME: ${{ secrets.DOCKER_USERNAME }}
      DOCKER_PASSWORD: ${{ secrets.DOCKER_PASSWORD }}
      NEXUS_USERNAME: ${{ secrets.NEXUS_USERNAME }}
      NEXUS_PASSWORD: ${{ secrets.NEXUS_PASSWORD }}
      NEXUS_REPOSITORY_URL: ${{ secrets.NEXUS_REPOSITORY_URL }}
```

## Workflow Diagram

```
release (semantic versioning, creates tag + GitHub release)
  │
  ├── docker-enabled? ──YES──► docker (build + push)
  │       └──NO──► skipped
  │
  └── publish-enabled? ──YES──► build-and-publish-package
          └──NO──► skipped
```

## Inputs

### General

| Input    | Type   | Default         | Description          |
| -------- | ------ | --------------- | -------------------- |
| `runner` | string | `ubuntu-latest` | GitHub runner to use |

### Docker Configuration

| Input                      | Type    | Default      | Description                               |
| -------------------------- | ------- | ------------ | ----------------------------------------- |
| `docker-enabled`           | boolean | `true`       | Enable Docker image build and push        |
| `docker-target-repository` | string  | ``           | Target repository (e.g., `org/image`)     |
| `docker-registry`          | string  | `docker.io`  | Docker registry URL (e.g., `ghcr.io`)     |
| `docker-dockerfile`        | string  | `Dockerfile` | Path to Dockerfile                        |
| `docker-context`           | string  | `.`          | Docker build context directory            |
| `docker-build-args`        | string  | ``           | Build arguments (e.g., `--build-arg K=V`) |

### Package Configuration

| Input                     | Type    | Default | Description                        |
| ------------------------- | ------- | ------- | ---------------------------------- |
| `publish-package-enabled` | boolean | `true`  | Enable package publishing to Nexus |

## Secrets

| Secret                 | Required           | Description                           |
| ---------------------- | ------------------ | ------------------------------------- |
| `DOCKER_USERNAME`      | If docker-enabled  | Docker registry username              |
| `DOCKER_PASSWORD`      | If docker-enabled  | Docker registry password or token     |
| `NEXUS_USERNAME`       | If publish-enabled | Nexus registry username               |
| `NEXUS_PASSWORD`       | If publish-enabled | Nexus registry password               |
| `NEXUS_REPOSITORY_URL` | If publish-enabled | Nexus repository URL                  |
| `GITHUB_TOKEN`         | Auto (GitHub)      | GitHub API token for release creation |

### release

**Purpose**: Creates semantic version tag and GitHub release using conventional commits

- Analyzes commit history to determine if new version is needed
- Creates version tag and GitHub release if changes warrant it
- If no changes warrant a release, workflow stops (other jobs are skipped)
- **Outputs**: `released` (true/false), `version` (semver), `tag` (git tag)
- **Depends on**: nothing (runs first)

### docker

**Purpose**: Builds and pushes Docker image to configured registry

- Builds Docker image tagged with semantic version
- Authenticates with Docker registry
- Tags and pushes image to target repository
- **Condition**: Only if `docker-enabled=true` AND previous release job released a new version
- **Depends on**: release job

### build-and-publish-package

**Purpose**: Builds Python wheel and publishes it to Nexus

- Extracts supported Python versions from `pyproject.toml`
- Builds wheel with version from semantic release using minimum supported Python version
- Publishes directly to Nexus (no artifact staging)
- **Condition**: Only if `publish-package-enabled=true` AND previous release job released a new version
- **Depends on**: release job

## Required Files

- `pyproject.toml`: Must contain Python version requirements and semantic release configuration
- `Dockerfile`: For Docker image builds (if docker-enabled=true)

## Environment Setup

### Semantic Release Configuration

Configure Python Semantic Release in your `pyproject.toml`:

```toml
[tool.semantic_release]
tag_format = "v{version}"
version_pattern = "v(?P<version>.*)"
```

### Required Secrets

Set these in your GitHub repository settings:

```
DOCKER_USERNAME      # Docker registry username
DOCKER_PASSWORD      # Docker registry password or token
NEXUS_USERNAME       # Nexus registry username
NEXUS_PASSWORD       # Nexus registry password
NEXUS_REPOSITORY_URL # e.g., https://nexus.example.com/repository/wheels/
```

## Example Flow

```
Push commit with conventional message to main
    ↓
Trigger workflow
    ↓
Release job:
  - Semantic Release analyzes commits
  - No semver bump needed? → Workflow stops (docker and build-and-publish-package are skipped)
  - New version needed? → Creates tag v1.2.3 and GitHub release
    ↓
Parallel execution (if released):
  ├─ Build Docker image (1.2.3) → Push to registry    [if docker-enabled]
  │
  └─ Extract Python versions from pyproject.toml
     Build Python wheel (1.2.3) → Publish to Nexus     [if publish-package-enabled]
    ↓
Done ✅
```

**Key points**:

- If no version bump is needed, the workflow exits early (docker and build-and-publish-package are skipped)
- Docker build and push happen on **same runner** (no image loss)
- Python build and publish happen together in **one job** (no artifacts needed)

## Security Best Practices

- Store all credentials as [GitHub Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- Never hardcode credentials or repository URLs in workflows
- Use repository-scoped secrets when possible
- Rotate access tokens regularly
- Consider using fine-grained personal access tokens instead of main account credentials

## Notes

- Concurrency group `release` ensures only one release runs at a time
- All version information flows from semantic release throughout the pipeline
- Docker Hub image is tagged with `docker.io` registry by default
- Wheel artifacts are kept for 90 days on GitHub (configurable)
- Release notes are auto-generated from commits using GitHub's format
- **Docker job advantage**: Build and push happen on same runner, avoiding "image not found" errors
- **Build/publish separation**: Allows building on one runner and publishing on another, prevents secrets exposure in artifacts
