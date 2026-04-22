# Snapshot Workflow - Python

A reusable GitHub Actions workflow that orchestrates development builds on the `develop` branch: computing a dev version from git tags, building and pushing a Docker image, and publishing the Python package to Nexus.

## Overview

This workflow automates the full dev-build process:

- **Version Computation**: Extracts the latest release version from VCS and computes an incremental PEP 440 dev version (e.g., `1.2.3.dev4`)
- **Docker Build & Push**: Builds and pushes a Docker image tagged with the PEP 440 dev version
- **Package Build & Publish**: Builds a Python wheel at the PEP 440 dev version and publishes it to Nexus

## Version Scheme

Given a latest release tag `v1.2.3`, 4 commits since that tag, a `version-tag-prefix` of `v`, and a current commit SHA of `abc1234`:

| Artifact        | Format                            | Example                          |
| --------------- | --------------------------------- | -------------------------------- |
| Release tag     | `{prefix}{base-version}`          | `v1.2.3`                         |
| PEP 440 version | `{base-version}.dev{build}+{sha}` | `1.2.3.dev4+abc1234`             |
| Docker image    | tagged with PEP 440 version       | `org/image:1.2.3.dev4+abc1234`   |
| Wheel filename  | uses PEP 440 version              | `myapp-1.2.3.dev4+abc1234-*.whl` |

The build number is computed by counting commits since the latest release tag, and the SHA is the short commit hash of the current HEAD (e.g., 4 commits after `v1.2.3` with SHA `abc1234` → `1.2.3.dev4+abc1234`).

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
compute-version (extract version from tags, compute PEP 440 dev version)
  │
  ├──► docker-enabled? ──YES──► docker (build + push)
  │         └──NO──► skipped
  │
  └──► publish-enabled? ──YES──► build-and-publish-package
             └──NO──► skipped
```

## Inputs

### General

| Input                | Type   | Default         | Description                                                          |
| -------------------- | ------ | --------------- | -------------------------------------------------------------------- |
| `runner`             | string | `ubuntu-latest` | GitHub runner to use                                                 |
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

### compute-version

**Purpose**: Computes the PEP 440 dev version for this build

- Reads the latest release tag matching `{version-tag-prefix}X.Y.Z` from git
- Counts commits since that tag to determine the build number
- Computes the PEP 440 dev version (e.g., `1.2.3.dev4`) used by all downstream jobs
- Does NOT create or push any git tags
- **Outputs**: `version`, `pep440-version`
- **Depends on**: nothing (runs first)

### docker

**Purpose**: Builds and pushes the Docker image to configured registry

- Builds Docker image, optionally injecting the PEP 440 version as a build arg (via `docker-version-build-arg`)
- Tags image with the PEP 440 version (e.g., `org/image:1.2.3.dev4`)
- Build and push happen on the **same runner** to avoid "image not found" errors
- **Condition**: Only if `docker-enabled=true`
- **Depends on**: compute-version

### build-and-publish-package

**Purpose**: Builds a Python wheel and publishes it to Nexus

- Extracts supported Python versions from `pyproject.toml`
- Builds wheel at the PEP 440 dev version (e.g., `1.2.3.dev4`) using the minimum supported Python version
- Publishes directly to Nexus (no artifact upload/download needed)
- **Condition**: Only if `publish-package-enabled=true`
- **Depends on**: compute-version

## Required Files

- `pyproject.toml`: Must contain `requires-python` for version extraction and build configuration
- `Dockerfile`: For Docker image builds (if `docker-enabled=true`)
- At least one release tag matching `{version-tag-prefix}X.Y.Z` pattern must exist in the repository (e.g., `v1.2.3`)

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

If you want the computed PEP 440 version stamped into the image, pass it via `docker-build-args`:

```yaml
with:
  docker-build-args: "--build-arg APP_VERSION=1.2.3.dev4"
```

And declare it in your Dockerfile:

```dockerfile
ARG APP_VERSION=""
ENV APP_VERSION=${APP_VERSION}
```

## Example Flow

```
Push commit to develop branch (e.g., 4 commits after v1.2.3)
    ↓
Trigger workflow
    ↓
Compute version:
  - Latest release tag found: v1.2.3
  - Commits since v1.2.3: 4
  - PEP 440 version: 1.2.3.dev4
    ↓
2a. Build Docker image (1.2.3.dev4) → Push            [if docker-enabled]
2b. Build wheel (1.2.3.dev4) → Publish to Nexus       [if publish-package-enabled]
    ↓
Done ✅
```

## Notes

- **No tag creation**: This workflow computes the PEP 440 version from existing release tags but does NOT create new git tags
- **Build number from commits**: The dev build number counts commits since the latest release tag (not previous dev tags)
- **PEP 440 compliance**: The `1.2.3.dev4` format is recognized by pip, twine, and PyPI-compatible registries as a pre-release
- **Concurrency safety**: `cancel-in-progress: true` means only the latest push gets built, avoiding stale dev builds piling up
- **Docker version injection**: Pass the version via `docker-build-args` (e.g., `--build-arg APP_VERSION=1.2.3.dev4`) if you need it available in the Docker build.
- **No release tags created**: If you need to create a release tag, use the [Release Workflow](RELEASE-PYTHON-WORKFLOW.md)

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
