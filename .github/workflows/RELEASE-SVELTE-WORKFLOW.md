# Release Workflow - Svelte

A reusable GitHub Actions workflow that orchestrates the complete release process for Svelte/Node.js projects: semantic versioning, Docker image publishing, and NPM package publishing to Nexus.

## Overview

This workflow automates the full release process:

- **Semantic Versioning**: Automatically determines version based on conventional commits and creates a GitHub release
- **Docker Build & Push**: Builds and pushes Docker image to registry (if enabled)
- **Package Build & Publish**: Builds the Yarn package and publishes it to Nexus (if enabled)

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
    uses: m4nh/shared-cicd/.github/workflows/release-svelte.yml@main
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
  release:
    uses: m4nh/shared-cicd/.github/workflows/release-svelte.yml@main
    with:
      runner: "ubuntu-latest"
      node-version: "20"
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
  ├── released? ──NO──► all downstream jobs skipped
  │
  └── released? ──YES──►
        │
        ├──► docker-enabled? ──YES──► docker (build + push)
        │         └──NO──► skipped
        │
        └──► publish-enabled? ──YES──► build-and-publish-package
                   └──NO──► skipped
```

## Inputs

### General

| Input          | Type   | Default         | Description                                                    |
| -------------- | ------ | --------------- | -------------------------------------------------------------- |
| `runner`       | string | `ubuntu-latest` | GitHub runner to use                                           |
| `node-version` | string | `20`            | Node.js version to use for semantic release, build and publish |

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

## Permissions

The calling workflow **must** grant the following permissions:

```yaml
permissions:
  contents: write # Required for semantic-release to create tags and GitHub releases
```

## Secrets

| Secret                 | Required           | Description                           |
| ---------------------- | ------------------ | ------------------------------------- |
| `DOCKER_USERNAME`      | If docker-enabled  | Docker registry username              |
| `DOCKER_PASSWORD`      | If docker-enabled  | Docker registry password or token     |
| `NEXUS_USERNAME`       | If publish-enabled | Nexus username                        |
| `NEXUS_PASSWORD`       | If publish-enabled | Nexus password                        |
| `NEXUS_REPOSITORY_URL` | If publish-enabled | Nexus repository URL                  |
| `GITHUB_TOKEN`         | Auto (GitHub)      | GitHub API token for release creation |

## Jobs

### release

**Purpose**: Creates semantic version tag and GitHub release using conventional commits

- Analyzes commit history to determine if a new version is needed
- Creates a version tag and GitHub release if qualifying commits are found
- If no commits warrant a new release, the workflow exits early (all downstream jobs skip)
- Uses `cycjimmy/semantic-release-action@v4` with `@semantic-release/github`
- **Outputs**: `released` (true/false), `version` (semver), `tag` (git tag)
- **Depends on**: nothing (runs first)

### docker

**Purpose**: Builds and pushes the Docker image to configured registry

- Builds Docker image tagged with the semantic version
- Build and push happen on the **same runner** to avoid "image not found" errors
- **Condition**: Only if `docker-enabled=true` AND a new release was published
- **Depends on**: release

### build-and-publish-package

**Purpose**: Builds the Yarn package and publishes it to Nexus

- Stamps the release version into `package.json`
- Installs dependencies with `yarn install --immutable` (via Corepack)
- Builds with `yarn build`
- Publishes directly to Nexus
- **Condition**: Only if `publish-package-enabled=true` AND a new release was published
- **Depends on**: release

## Required Files

- `package.json`: Must include `packageManager: yarn@X.Y.Z` for Corepack and semantic release configuration
- `release.config.js` (or `.releaserc`): Semantic release configuration (branches, plugins)
- `Dockerfile`: For Docker image builds (if `docker-enabled=true`)

## Semantic Release Configuration

Configure semantic release in your repo's `release.config.js`:

```js
export default {
  branches: ["main"],
  plugins: [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    ["@semantic-release/github", { successComment: false, failComment: false }],
  ],
};
```

> **Note**: `successComment: false` and `failComment: false` are required because the reusable workflow only has `contents: write` permission — it cannot comment on pull requests.

## Example Flow

```
Push commit with conventional message to main
    ↓
Trigger workflow
    ↓
Release job:
  - Semantic Release analyzes commits
  - No semver bump needed? → Workflow stops (docker and build-and-publish-package are skipped)
  - New version needed? → Creates tag v1.5.0 and GitHub release
    ↓
Parallel execution (if released):
  ├─ Build Docker image (1.5.0) → Push to registry    [if docker-enabled]
  └─ Stamp version → yarn build → Publish to Nexus    [if publish-package-enabled]
    ↓
Done ✅
```

## Notes

- **Conventional commits required**: Only `fix:`, `feat:`, and breaking changes trigger a new version
- **Early exit**: If no release is published, `docker` and `build-and-publish-package` are automatically skipped — this is expected behavior, not a bug
- **Corepack required**: The project's `package.json` must define `packageManager` with a Yarn 4.x version
- **Docker version injection**: Pass version via `docker-build-args` if your Dockerfile needs it

## Related Documentation

- [Snapshot Workflow](SNAPSHOT-SVELTE-WORKFLOW.md)
- [Build Package Action](../../actions/yarn/build-package/docs.md)
- [Publish Package Action](../../actions/yarn/publish-package/docs.md)
- [Build Docker Image Action](../../actions/docker/build-docker-image/docs.md)
- [Push Docker Action](../../actions/docker/push-docker/docs.md)
