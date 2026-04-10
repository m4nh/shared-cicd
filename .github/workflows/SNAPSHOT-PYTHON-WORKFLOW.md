# Snapshot Workflow - Python

A reusable GitHub Actions workflow that orchestrates development builds on the `develop` branch: creating a versioned dev tag, building and pushing a Docker image, and publishing the Python package to Nexus.

## Overview

This workflow automates the full dev-build process:

- **Dev Tagging**: Extracts the latest release version from VCS and creates an incremental dev tag (e.g., `develop/1.2.3.4`)
- **Docker Build & Push**: Builds and pushes a Docker image tagged with the PEP 440 dev version
- **Package Build & Publish**: Builds a Python wheel at the PEP 440 dev version and publishes it to Nexus

## Tag and Version Scheme

Given a latest release tag `v1.2.3` and a `tag-prefix` of `develop`:

| Artifact        | Format                                | Example                  |
| --------------- | ------------------------------------- | ------------------------ |
| Git tag         | `{tag-prefix}/{base-version}.{build}` | `develop/1.2.3.4`        |
| PEP 440 version | `{base-version}.dev{build}`           | `1.2.3.dev4`             |
| Docker image    | tagged with PEP 440 version           | `org/image:1.2.3.dev4`   |
| Wheel filename  | uses PEP 440 version                  | `myapp-1.2.3.dev4-*.whl` |

The build number auto-increments by counting existing dev tags for that base version.

## Using This Workflow

### In Another Repository

Create a workflow file in your repo at `.github/workflows/develop.yml`:

```yaml
name: Develop

on:
  push:
    branches:
      - develop

jobs:
  develop:
    uses: m4nh/shared-cicd/.github/workflows/develop-python.yml@main
    secrets:
      DOCKER_USERNAME: ${{ secrets.DOCKER_USERNAME }}
      DOCKER_PASSWORD: ${{ secrets.DOCKER_PASSWORD }}
      NEXUS_USERNAME: ${{ secrets.NEXUS_USERNAME }}
      NEXUS_PASSWORD: ${{ secrets.NEXUS_PASSWORD }}
      NEXUS_REPOSITORY_URL: ${{ secrets.NEXUS_REPOSITORY_URL }}
    with:
      docker-target-repository: "myorg/myapp"
```

### With All Options

```yaml
jobs:
  develop:
    uses: m4nh/shared-cicd/.github/workflows/develop-python.yml@main
    with:
      runner: "ubuntu-latest"
      tag-prefix: "develop"
      version-tag-prefix: "v"
      docker-enabled: true
      docker-target-repository: "myorg/myapp"
      docker-registry: "docker.io"
      docker-dockerfile: "Dockerfile"
      docker-context: "."
      docker-build-args: "--build-arg ENV=dev"
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
start
  │
  ▼
create-tag
  │
  ├──► docker-enabled? ──YES──► docker (build + push, same runner)
  │         └──NO──► skipped
  │
  └──► publish-enabled? ──YES──► build-and-publish-package
             └──NO──► skipped       (extracts python versions internally)
```

## Inputs

### General

| Input                | Type   | Default         | Description                                                          |
| -------------------- | ------ | --------------- | -------------------------------------------------------------------- |
| `runner`             | string | `ubuntu-latest` | GitHub runner to use                                                 |
| `tag-prefix`         | string | `develop`       | Prefix for dev tags (e.g., `develop` → `develop/1.2.3.4`)            |
| `version-tag-prefix` | string | `v`             | Prefix used on release tags to extract base version (e.g., `v1.2.3`) |

### Docker Configuration

| Input                      | Type    | Default      | Description                                          |
| -------------------------- | ------- | ------------ | ---------------------------------------------------- |
| `docker-enabled`           | boolean | `true`       | Enable Docker image build and push                   |
| `docker-target-repository` | string  | ``           | Target repository (e.g., `org/image`)                |
| `docker-registry`          | string  | `docker.io`  | Docker registry URL (e.g., `ghcr.io`)                |
| `docker-dockerfile`        | string  | `Dockerfile` | Path to Dockerfile                                   |
| `docker-context`           | string  | `.`          | Docker build context directory                       |
| `docker-build-args`        | string  | ``           | Additional build arguments (e.g., `--build-arg K=V`) |

### Package Configuration

| Input                     | Type    | Default | Description                        |
| ------------------------- | ------- | ------- | ---------------------------------- |
| `publish-package-enabled` | boolean | `true`  | Enable package publishing to Nexus |

## Secrets

| Secret                 | Required           | Description                       |
| ---------------------- | ------------------ | --------------------------------- |
| `DOCKER_USERNAME`      | If docker-enabled  | Docker registry username          |
| `DOCKER_PASSWORD`      | If docker-enabled  | Docker registry password or token |
| `NEXUS_USERNAME`       | If publish-enabled | Nexus username                    |
| `NEXUS_PASSWORD`       | If publish-enabled | Nexus password                    |
| `NEXUS_REPOSITORY_URL` | If publish-enabled | Nexus repository URL              |
| `GITHUB_TOKEN`         | Auto (GitHub)      | GitHub token for pushing tags     |

## Jobs

### create-tag

**Purpose**: Computes and pushes the next dev tag for this develop build

- Reads the latest release tag matching `{version-tag-prefix}X.Y.Z` from git
- Counts existing dev tags for that version to determine the next build number
- Creates and pushes a tag like `develop/1.2.3.4`
- Computes the PEP 440 version (`1.2.3.dev4`) used by all downstream jobs
- **Outputs**: `tag`, `version`, `build`, `pep440-version`
- **Depends on**: nothing (runs first)

### docker

**Purpose**: Builds and pushes the Docker image to configured registry in a single job

- Builds Docker image with `SETUPTOOLS_SCM_PRETEND_VERSION` set to the PEP 440 version
- Tags image with the PEP 440 version (e.g., `org/image:1.2.3.dev4`)
- Build and push happen on the **same runner** to avoid "image not found" errors
- **Condition**: Only if `docker-enabled=true`
- **Depends on**: create-tag

### build-and-publish-package

**Purpose**: Builds a Python wheel and publishes it to Nexus in a single job

- Extracts supported Python versions from `pyproject.toml`
- Builds wheel at the PEP 440 dev version (e.g., `1.2.3.dev4`) using the minimum supported Python version
- Publishes directly to Nexus (no artifact upload/download needed)
- **Condition**: Only if `publish-package-enabled=true`
- **Depends on**: create-tag

## Required Files

- `pyproject.toml`: Must contain `requires-python` for version extraction and build configuration
- `Dockerfile`: For Docker image builds (if `docker-enabled=true`)
- At least one release tag matching `{version-tag-prefix}X.Y.Z` must exist in the repository

## Concurrency

The workflow uses `cancel-in-progress: true` on the `develop` group. Rapid pushes to the develop branch cancel any in-progress build for the same group, ensuring only the latest commit gets built.

## Environment Setup

### Required Secrets

Set these in your GitHub repository settings:

```
DOCKER_USERNAME           # Docker registry username
DOCKER_PASSWORD           # Docker registry password/token
NEXUS_USERNAME            # Nexus username
NEXUS_PASSWORD            # Nexus password
NEXUS_REPOSITORY_URL      # e.g., https://nexus.example.com/repository/wheels/
```

### Dockerfile Requirements

The Dockerfile should accept `SETUPTOOLS_SCM_PRETEND_VERSION` as a build argument to stamp the version into the image:

```dockerfile
ARG SETUPTOOLS_SCM_PRETEND_VERSION=""
ENV SETUPTOOLS_SCM_PRETEND_VERSION=${SETUPTOOLS_SCM_PRETEND_VERSION}
```

## Example Flow

```
Push commit to develop branch
    ↓
Trigger workflow
    ↓
1a. Extract Python versions (from pyproject.toml)      [parallel]
1b. Create dev tag                                     [parallel]
    - Latest release tag found: v1.2.3
    - Existing dev tags for 1.2.3: develop/1.2.3.1, develop/1.2.3.2, develop/1.2.3.3
    - New tag: develop/1.2.3.4
    - PEP 440 version: 1.2.3.dev4
    ↓
2a. Build Docker image (1.2.3.dev4) → Push             [if docker-enabled]
2b. Build wheel (1.2.3.dev4) → Publish to Nexus        [if publish-package-enabled]
    ↓
Done ✅
```

## Notes

- **No release needed**: This workflow does not use semantic-release. It derives the version directly from existing release tags
- **Auto-incrementing build numbers**: The build number is global per base-version — it counts ALL dev tags for that version regardless of branch (useful if multiple dev branches share the same base)
- **PEP 440 compliance**: The `1.2.3.dev4` format is recognized by pip, twine, and PyPI-compatible registries as a pre-release
- **Concurrency safety**: `cancel-in-progress: true` means only the latest push gets built, avoiding stale dev builds piling up
- **Docker version injection**: `SETUPTOOLS_SCM_PRETEND_VERSION` is automatically prepended to build-args so the image always carries the correct version

## Security Best Practices

- Store all credentials as [GitHub Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- Never hardcode credentials or repository URLs in workflows
- Use repository-scoped secrets when possible

## Related Documentation

- [Release Workflow](RELEASE-PYTHON-WORKFLOW.md)
- [CI Workflow](CI-PYTHON-WORKFLOW.md)
- [Build Wheel Action](../../actions/python/build-wheel/docs.md)
- [Publish Package Action](../../actions/python/publish-package/docs.md)
- [Build Docker Image Action](../../actions/docker/build-docker-image/docs.md)
- [Push Docker Action](../../actions/docker/push-docker/docs.md)
