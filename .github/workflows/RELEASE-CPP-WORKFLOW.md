# Release Workflow - C++

A reusable GitHub Actions workflow that orchestrates the complete release process for C++ projects: semantic versioning, optional testing, Docker image building and publishing.

## Overview

This workflow automates the full release process:

- **Optional Testing**: Runs CMake build and CTest before release (if enabled)
- **Semantic Versioning**: Automatically determines version based on conventional commits and creates a GitHub release
- **Docker Build & Push**: Builds and pushes Docker image to registry (if enabled)

## Using This Workflow

### In Another Repository

Create a workflow file in your repo at `.github/workflows/release.yml`:

```yaml
name: Release

on:
  push:
    branches:
      - main

permissions:
  contents: write

jobs:
  release:
    uses: m4nh/shared-cicd/.github/workflows/release-cpp.yml@main
    secrets:
      DOCKER_USERNAME: ${{ secrets.DOCKER_USERNAME }}
      DOCKER_PASSWORD: ${{ secrets.DOCKER_PASSWORD }}
    with:
      docker-target-repository: "myorg/myapp"
```

### With All Options

```yaml
jobs:
  release:
    uses: m4nh/shared-cicd/.github/workflows/release-cpp.yml@main
    with:
      runner: "ubuntu-22.04"
      tests-enabled: true
      cmake-build-type: "Release"
      cmake-extra-args: "-DENABLE_COVERAGE=ON"
      ctest-args: "--output-on-failure --parallel 4"
      docker-enabled: true
      docker-target-repository: "myorg/myapp"
      docker-registry: "docker.io"
      docker-dockerfile: "dockerfiles/Dockerfile"
      docker-context: "."
      docker-build-args: "--build-arg ENV=prod"
    secrets:
      DOCKER_USERNAME: ${{ secrets.DOCKER_USERNAME }}
      DOCKER_PASSWORD: ${{ secrets.DOCKER_PASSWORD }}
```

## Workflow Diagram

```
test (optional, if tests-enabled=true)
  ├─ Install system dependencies
  ├─ Install CMake
  ├─ Configure, build, and run tests
  └─ Fail if tests fail (blocks release)

release (semantic versioning, creates tag + GitHub release)
  ├─ Depends on: test (or skipped if test disabled)
  ├─ Analyzes conventional commits
  ├─ Creates git tag (e.g., v1.2.3) if version bump detected
  └─ Creates GitHub release

docker (build + push, optional)
  ├─ Depends on: release
  ├─ Condition: docker-enabled=true AND released=true
  ├─ Builds Docker image with semantic version
  └─ Pushes to registry
```

## Inputs

### General

| Input          | Type   | Default        | Description          |
| -------------- | ------ | -------------- | -------------------- |
| `runner`       | string | `ubuntu-22.04` | GitHub runner to use |

### Testing

| Input              | Type    | Default                 | Description                         |
| ------------------ | ------- | ----------------------- | ----------------------------------- |
| `tests-enabled`    | boolean | `true`                  | Enable CMake build and unit tests   |
| `cmake-build-type` | string  | `Release`               | CMake build type                    |
| `cmake-extra-args` | string  | ``                      | Additional CMake configuration args |
| `ctest-args`       | string  | `--output-on-failure`   | Additional arguments to pass to ctest |

### Docker Configuration

| Input                      | Type    | Default      | Description                                          |
| -------------------------- | ------- | ------------ | ---------------------------------------------------- |
| `docker-enabled`           | boolean | `true`       | Enable Docker image build and push                   |
| `docker-target-repository` | string  | ``           | Target repository (e.g., `org/image`)                |
| `docker-registry`          | string  | `docker.io`  | Docker registry URL (e.g., `ghcr.io`)                |
| `docker-dockerfile`        | string  | `Dockerfile` | Path to Dockerfile                                   |
| `docker-context`           | string  | `.`          | Docker build context directory                       |
| `docker-build-args`        | string  | ``           | Additional build arguments (e.g., `--build-arg K=V`) |

### System Dependencies

| Input                 | Type   | Default                              | Description                                               |
| --------------------- | ------ | ------------------------------------ | --------------------------------------------------------- |
| `system-dependencies` | string | (see workflow for default list)      | System packages to install for build/test                 |

**Default system dependencies**: build-essential, cmake, git, OpenCV, Eigen, Boost, COLMAP dependencies, etc.

## Permissions

The calling workflow **must** grant the following permissions:

```yaml
permissions:
  contents: write # Required for semantic-release to create tags and GitHub releases
```

## Secrets

| Secret            | Required          | Description                           |
| ----------------- | ----------------- | ------------------------------------- |
| `DOCKER_USERNAME` | If docker-enabled | Docker registry username              |
| `DOCKER_PASSWORD` | If docker-enabled | Docker registry password or token     |
| `GITHUB_TOKEN`    | Auto (GitHub)     | GitHub API token for release creation |

## Jobs

### test

**Purpose**: Builds and tests the C++ project with CMake and CTest

- Installs all system dependencies (CMake, OpenCV, Eigen, Boost, etc.)
- Installs CMake 3.29.8 (newer than Ubuntu 22.04 default)
- Configures CMake with specified build type and `-DCALIBRY_BUILD_TESTS=ON`
- Builds project with parallel compilation
- Runs all tests via CTest
- **Condition**: Only if `tests-enabled=true`
- **Depends on**: nothing (runs first)

### release

**Purpose**: Creates semantic version tag and GitHub release using conventional commits

- Analyzes commit history to determine if a new version is needed
- Creates a version tag and GitHub release if qualifying commits are found
- If no commits warrant a new release, the workflow exits early (docker job skips)
- Uses `cycjimmy/semantic-release-action@v4` with `@semantic-release/github`
- **Outputs**: `released` (true/false), `version` (semver), `tag` (git tag)
- **Depends on**: test job (or skipped if test disabled)

### docker

**Purpose**: Builds and pushes the Docker image to configured registry

- Builds Docker image tagged with the semantic version
- Build and push happen on the **same runner** to avoid "image not found" errors
- **Condition**: Only if `docker-enabled=true` AND a new release was published
- **Depends on**: release job

## Required Files

- `CMakeLists.txt`: Must be configured to support CMake builds and optional tests
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
Test job (if enabled):
  - Install dependencies
  - Build with CMake
  - Run CTest
  - Pass/Fail → blocks release if fail
    ↓
Release job:
  - Semantic Release analyzes commits
  - No semver bump needed? → Workflow stops (docker is skipped)
  - New version needed? → Creates tag v1.5.0 and GitHub release
    ↓
Docker job (if released and enabled):
  - Build Docker image (1.5.0) → Push to registry
    ↓
Done ✅
```

## Configuration Examples

### Skip Tests (Release Only)

```yaml
jobs:
  release:
    uses: m4nh/shared-cicd/.github/workflows/release-cpp.yml@main
    with:
      tests-enabled: false
      docker-target-repository: "myorg/myapp"
    secrets:
      DOCKER_USERNAME: ${{ secrets.DOCKER_USERNAME }}
      DOCKER_PASSWORD: ${{ secrets.DOCKER_PASSWORD }}
```

### Debug Build with Tests

```yaml
jobs:
  release:
    uses: m4nh/shared-cicd/.github/workflows/release-cpp.yml@main
    with:
      cmake-build-type: "Debug"
      docker-target-repository: "myorg/myapp"
    secrets:
      DOCKER_USERNAME: ${{ secrets.DOCKER_USERNAME }}
      DOCKER_PASSWORD: ${{ secrets.DOCKER_PASSWORD }}
```

### Custom Dockerfile Path

```yaml
jobs:
  release:
    uses: m4nh/shared-cicd/.github/workflows/release-cpp.yml@main
    with:
      docker-dockerfile: "dockerfiles/Dockerfile"
      docker-target-repository: "myorg/myapp"
    secrets:
      DOCKER_USERNAME: ${{ secrets.DOCKER_USERNAME }}
      DOCKER_PASSWORD: ${{ secrets.DOCKER_PASSWORD }}
```

### Release Only (No Docker)

```yaml
jobs:
  release:
    uses: m4nh/shared-cicd/.github/workflows/release-cpp.yml@main
    with:
      docker-enabled: false
```

## Notes

- **Conventional commits required**: Only `fix:`, `feat:`, and breaking changes trigger a new version
- **Early exit**: If no release is published, `docker` job is automatically skipped — this is expected behavior, not a bug
- **Docker version injection**: The workflow passes `version` via `build-args` to the Docker build; your Dockerfile should accept `ARG VERSION` if you want to use it
- **Concurrency**: `concurrency: group: release, cancel-in-progress: false` ensures only one release runs at a time without canceling in-progress releases

## Troubleshooting

### No release created

**Cause**: No conventional commits since last release warrant a version bump.

**Solution**: Ensure commits follow [Conventional Commits](https://www.conventionalcommits.org/) spec:
- `fix:` triggers patch version (0.0.X)
- `feat:` triggers minor version (0.X.0)
- `BREAKING CHANGE:` triggers major version (X.0.0)

### Tests fail during release

**Cause**: Tests are enabled but failing.

**Solution**: Fix the failing tests or disable tests with `tests-enabled: false` if you want to release anyway.

### Docker build fails

**Cause**: Dockerfile error or missing build context.

**Solution**: Test Docker build locally first:
```bash
docker build -f dockerfiles/Dockerfile --build-arg VERSION=1.0.0 .
```

## Related Documentation

- [CI C++ Workflow](CI-CPP-WORKFLOW.md)
- [Build Docker Image Action](../../actions/docker/build-docker-image/docs.md)
- [Push Docker Action](../../actions/docker/push-docker/docs.md)
