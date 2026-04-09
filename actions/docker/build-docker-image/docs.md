# Build Docker Image Action

A simple GitHub Action that builds Docker images with support for custom build arguments.

## Overview

This action focuses on building Docker images by:

- Building Docker images with customizable Dockerfile and context
- Supporting custom build arguments
- Outputting image metadata (ID and digest)
- Loading images for local use or testing

For pushing to registries, use a separate push action.

## Inputs

| Input        | Required | Default      | Description                                                                 |
| ------------ | -------- | ------------ | --------------------------------------------------------------------------- |
| `dockerfile` | No       | `Dockerfile` | Path to the Dockerfile                                                      |
| `context`    | No       | `.`          | Docker build context directory                                              |
| `tags`       | **Yes**  | —            | Image tags (comma or space-separated, e.g., `myimage:latest,myimage:1.0.0`) |
| `build-args` | No       | ``           | Docker build arguments (e.g., `--build-arg VERSION=1.0.0`)                  |

## Outputs

| Output         | Description                 | Example                  |
| -------------- | --------------------------- | ------------------------ |
| `image-id`     | Built image ID (short hash) | `abc123def456`           |
| `image-digest` | Full image digest SHA256    | `sha256:abc123def456...` |

## Usage

### Basic Build

```yaml
- uses: m4nh/shared-cicd/actions/docker/build-docker-image@main
  with:
    tags: "myimage:latest"
```

### Multiple Tags

```yaml
- uses: m4nh/shared-cicd/actions/docker/build-docker-image@main
  with:
    tags: "myimage:latest,myimage:1.0.0"
```

### With Build Arguments

```yaml
- uses: m4nh/shared-cicd/actions/docker/build-docker-image@main
  with:
    tags: "myimage:latest"
    build-args: "--build-arg VERSION=1.0.0 --build-arg ENV=prod"
```

### Custom Dockerfile and Context

```yaml
- uses: m4nh/shared-cicd/actions/docker/build-docker-image@main
  with:
    dockerfile: "docker/Dockerfile.prod"
    context: "./app"
    tags: "myimage:latest"
```

## Complete Workflow Example

```yaml
name: Build and Push Docker

on:
  push:
    branches: [main]
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      image-id: ${{ steps.build.outputs.image-id }}
    steps:
      - uses: actions/checkout@v4

      - name: Build Docker image
        uses: m4nh/shared-cicd/actions/docker/build-docker-image@main
        id: build
        with:
          tags: |
            ghcr.io/${{ github.repository }}:latest
            ghcr.io/${{ github.repository }}:${{ github.sha }}
          build-args: |
            --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
            --build-arg VCS_REF=${{ github.sha }}
          push: "true"
          registry: "ghcr.io"
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Image built
        run: echo "Built image: ${{ steps.build.outputs.image-id }}"
```

## Release Workflow

```yamlDocker

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build Docker image
        uses: m4nh/shared-cicd/actions/docker/build-docker-image@main
        id: build
        with:
          tags: "myimage:latest,myimage:${{ github.sha }}"
          build-args: |
            --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
            --build-arg VCS_REF=${{ github.sha }}

      - name: Image built
        run: echo "Built image: ${{ steps.build.outputs.image-id }}"
```

## With Push Action

For pushing to registries, combine with another action:

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      image-id: ${{ steps.build.outputs.image-id }}
    steps:
      - uses: actions/checkout@v4
Registry Credentials

For now, pushing is handled by separate actions. See the push action documentation for credential handling.

## Tips

- **Build arguments**: Pass configuration at build time rather than runtime
- **Layer caching**: Use consistent tags to benefit from Docker layer caching
- **GitHub runner**: Standard ubuntu-latest includes Docker; no additional setup needed
- **Outputs**: Use image ID and digest for logging or verification
- **Separation of concerns**: Building is separate from pushing for flexibility ["python", "app.py"]
```

### With Build Arguments

```dockerfile
ARG VERSION=unknown
ARG BUILD_DATE=unknown
ARG VCS_REF=unknown

FROM python:3.11
ENV VERSION=${VERSION}
LABEL org.opencontainers.image.created=$BUILD_DATE
LABEL org.opencontainers.image.revision=$VCS_REF
LABEL org.opencontainers.image.version=$VERSION
```

## Prerequisites

- Docker must be available on the runner (standard on GitHub-hosted runners)
- For pushing: appropriate registry credentials in secrets
- Valid Dockerfile in the repository

## Tips

- **Multiple registries**: Tag for multiple registries in one action
- **Semantic versioning**: Use version outputs from other jobs for tags
- **Build arguments**: Pass configuration at build time rather than runtime
- **Layer caching**: Use consistent tags to benefit from Docker layer caching
- **Security**: Use `--build-arg` for sensitive data instead of ENV in Dockerfile
- **GitHub runner**: Standard ubuntu-latest includes Docker; no additional setup needed

## Related Actions

- **build-wheel** - Build Python wheels
- **extract-python-versions** - Extract Python versions from pyproject.toml
