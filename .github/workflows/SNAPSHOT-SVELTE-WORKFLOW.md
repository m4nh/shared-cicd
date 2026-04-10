# Snapshot Workflow - Svelte

A reusable GitHub Actions workflow that orchestrates development builds: computing a dev version from git tags, building and pushing a Docker image, and publishing the Svelte/Node.js package to Nexus.

## Overview

This workflow automates the full dev-build process:

- **Version Computation**: Extracts the latest release version from VCS and computes an incremental semver dev version (e.g., `1.2.3-dev.4`)
- **Docker Build & Push**: Builds and pushes a Docker image tagged with the dev version
- **Package Build & Publish**: Builds and publishes the Yarn package to Nexus at the dev version

## Version Scheme

Given a latest release tag `v1.2.3` and 4 commits since that tag:

| Artifact       | Format                       | Example                 |
| -------------- | ---------------------------- | ----------------------- |
| Release tag    | `{prefix}{base-version}`     | `v1.2.3`                |
| Semver version | `{base-version}-dev.{build}` | `1.2.3-dev.4`           |
| Docker image   | tagged with semver version   | `org/image:1.2.3-dev.4` |
| NPM package    | uses semver version          | `myapp@1.2.3-dev.4`     |

The build number is computed by counting commits since the latest release tag.

## Using This Workflow

### In Another Repository

Create a workflow file in your repo at `.github/workflows/snapshot.yml`:

```yaml
name: Snapshot

on:
  push:
    branches:
      - develop

jobs:
  snapshot:
    uses: m4nh/shared-cicd/.github/workflows/snapshot-svelte.yml@main
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
  snapshot:
    uses: m4nh/shared-cicd/.github/workflows/snapshot-svelte.yml@main
    with:
      runner: "ubuntu-latest"
      version-tag-prefix: "v"
      node-version: "20"
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
compute-version (extract version from tags, compute semver dev version)
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
| `node-version`       | string | `20`            | Node.js version to use for build and publish                         |

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

## Jobs

### compute-version

**Purpose**: Computes the semver dev version for this build

- Uses `vcs-version` action to find the latest release tag matching `{version-tag-prefix}X.Y.Z`
- Counts commits since that tag to determine the build number
- Computes the semver dev version (e.g., `1.2.3-dev.4`) used by all downstream jobs
- Does NOT create or push any git tags
- **Outputs**: `version`, `semver-version`
- **Depends on**: nothing (runs first)

### docker

**Purpose**: Builds and pushes the Docker image to configured registry

- Builds Docker image tagged with the semver dev version
- Build and push happen on the **same runner** to avoid "image not found" errors
- **Condition**: Only if `docker-enabled=true`
- **Depends on**: compute-version

### build-and-publish-package

**Purpose**: Builds the Yarn package and publishes it to Nexus

- Stamps the semver dev version into `package.json`
- Installs dependencies with `yarn install --immutable`
- Builds with `yarn build`
- Publishes directly to Nexus
- **Condition**: Only if `publish-package-enabled=true`
- **Depends on**: compute-version

## Required Files

- `package.json`: Must include `packageManager: yarn@X.Y.Z` for Corepack version management
- `Dockerfile`: For Docker image builds (if `docker-enabled=true`)
- At least one release tag matching `{version-tag-prefix}X.Y.Z` pattern must exist in the repository (e.g., `v1.2.3`)

## Concurrency

The workflow uses `cancel-in-progress: true` on the `develop` group. Rapid pushes cancel any in-progress build for the same group, ensuring only the latest commit gets built.

## Example Flow

```
Push commit to develop branch (e.g., 4 commits after v1.2.3)
    ↓
Trigger workflow
    ↓
Compute version:
  - Latest release tag found: v1.2.3
  - Commits since v1.2.3: 4
  - Semver version: 1.2.3-dev.4
    ↓
Parallel execution:
  ├─ Build Docker image (1.2.3-dev.4) → Push to registry   [if docker-enabled]
  └─ Stamp version → yarn build → Publish to Nexus          [if publish-enabled]
    ↓
Done ✅
```

## Notes

- **No tag creation**: This workflow computes the version from existing release tags but does NOT create new git tags
- **Build number from commits**: The dev build number counts commits since the latest release tag
- **Corepack required**: The project's `package.json` must define `packageManager` with a Yarn 4.x version
- **Concurrency safety**: `cancel-in-progress: true` means only the latest push gets built

## Related Documentation

- [Release Workflow](RELEASE-SVELTE-WORKFLOW.md)
- [Build Package Action](../../actions/yarn/build-package/docs.md)
- [Publish Package Action](../../actions/yarn/publish-package/docs.md)
- [Build Docker Image Action](../../actions/docker/build-docker-image/docs.md)
- [Push Docker Action](../../actions/docker/push-docker/docs.md)
