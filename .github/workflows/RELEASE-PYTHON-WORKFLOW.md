# Release Workflow - Python

A reusable GitHub Actions workflow that orchestrates the complete process of creating a new release including semantic versioning, building, publishing, and pushing to multiple registries.

## Overview

This workflow automates the full release process:

- **Semantic Versioning**: Automatically determines version based on conventional commits
- **Version Extraction**: Gets Python version requirements from `pyproject.toml`
- **Docker Build & Push**: Builds and pushes Docker image to Docker Hub
- **Package Build & Publish**: Builds Python wheel and publishes to Nexus
- **GitHub Release**: Creates GitHub release with built artifacts

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
release ─────────────────── extract-versions
    │  (run in parallel)           │
    │                              │
    ▼ (needs: release)             │
  docker                           │
  (build + push, same runner)      │
                                   │
                    ▼ (needs: release + extract-versions)
                 build-package
                      │
                      ▼ (needs: build-package)
               publish-package (if publish-package-enabled)

    ▼ (needs: release + build-package)
github-release
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
- **Outputs**: `released` (true/false), `version` (semver), `tag` (git tag)

- Runs on any push to `main` branch

### extract-versions

**Purpose**: Determines Python version requirements from project config

- Extracts supported Python versions from `pyproject.toml`
- **Outputs**: `min-version`, `max-version`, `python-versions` (JSON array)

### docker

**Purpose**: Builds and pushes Docker image to configured registry in a single job

- Builds Docker image tagged with semantic version
- Authenticates with Docker registry
- Tags and pushes image to target repository
- Uses constant internal image name `release-image` before retagging
- **Both steps run on the same runner**, so no image transfer issues
- **Condition**: Only if `docker-enabled=true` AND `released=true`
- **Depends on**: release job

### build-package

**Purpose**: Builds Python wheel distribution

- Builds wheel with version from semantic release
- Uses minimum Python version for best compatibility
- Uploads wheel to GitHub artifacts
- **Condition**: Only if `released=true`
- **Depends on**: release, extract-versions jobs

### publish-package

**Purpose**: Publishes wheel to Nexus repository

- Downloads built wheel from artifacts
- Publishes to Nexus using configured credentials
- **Condition**: Only if `publish-package-enabled=true` AND `released=true`
- **Depends on**: build-package job

### github-release

**Purpose**: Creates final GitHub release with all artifacts

- Downloads wheel artifacts
- Creates/updates GitHub release with semantic version
- Attaches wheel files to release
- Auto-generates release notes from commits
- **Condition**: Only if all jobs succeeded AND `released=true`
- **Depends on**: release, build-package jobs (waits for artifacts from build-package)

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
1. Semantic Release analyzes commits
   - No semver bump needed? → Workflow stops (skipped path)
   - New version needed? → Continue...
    ↓
2. Extract Python versions (parallel)
    ↓ (jobs run in parallel from here)
3a. Build Docker image v1.2.3
    ↓
    Push to registry

3b. Build Python wheel v1.2.3 → Upload to artifacts
    ↓
    Publish to Nexus (downloads from artifacts)
    ↓
4. Both complete → Create GitHub release with artifacts
    ↓
Done ✅
```

**Key points**:

- Docker build and push happen on **same runner** (no image loss)
- Python build and publish happen on **separate runners** (artifacts bridge them)
- All paths must complete before github-release runs

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
