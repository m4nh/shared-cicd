# Push Docker Image Action

A GitHub Action for pushing Docker images to Docker Hub or any Docker-compatible registry. Handles authentication and image tagging before push.

## Overview

This action focuses on pushing Docker images by:

- Authenticating with Docker Hub or custom registry
- Tagging images for the target repository
- Pushing images to the registry

Works seamlessly with the build-docker-image action to create a complete build and push workflow.

## Inputs

| Input               | Required | Default     | Description                                          |
| ------------------- | -------- | ----------- | ---------------------------------------------------- |
| `docker-username`   | Yes      | -           | Docker registry username for authentication          |
| `docker-password`   | Yes      | -           | Docker registry password or token for authentication |
| `image-name`        | Yes      | -           | Local image name to push (e.g., `myapp`)             |
| `image-tag`         | Yes      | -           | Image tag/version to push (e.g., `1.0.0`)            |
| `target-repository` | Yes      | -           | Target repository path (e.g., `myorg/myapp`)         |
| `registry`          | No       | `docker.io` | Docker registry URL (Docker Hub by default)          |

## Usage

### Basic: Push to Docker Hub

```yaml
- uses: m4nh/shared-cicd/actions/docker/push-docker@main
  with:
    docker-username: ${{ secrets.DOCKER_USERNAME }}
    docker-password: ${{ secrets.DOCKER_TOKEN }}
    image-name: myapp
    image-tag: "1.0.0"
    target-repository: myorg/myapp
```

### Complete workflow with build and push

```yaml
jobs:
  build:
    name: Build Docker Image
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Build image
        uses: m4nh/shared-cicd/actions/docker/build-docker-image@main
        with:
          tags: "myapp:1.0.0"

  push:
    name: Push Docker Image
    runs-on: ubuntu-latest
    needs: build

    steps:
      - name: Push to Docker Hub
        uses: m4nh/shared-cicd/actions/docker/push-docker@main
        with:
          docker-username: ${{ secrets.DOCKER_USERNAME }}
          docker-password: ${{ secrets.DOCKER_TOKEN }}
          image-name: myapp
          image-tag: "1.0.0"
          target-repository: myorg/myapp
```

### Push to custom registry

```yaml
- uses: m4nh/shared-cicd/actions/docker/push-docker@main
  with:
    docker-username: ${{ secrets.REGISTRY_USERNAME }}
    docker-password: ${{ secrets.REGISTRY_PASSWORD }}
    image-name: myapp
    image-tag: "1.0.0"
    target-repository: myorg/myapp
    registry: registry.example.com
```

### With version from release output

```yaml
- name: Push image from release
  uses: m4nh/shared-cicd/actions/docker/push-docker@main
  if: needs.release.outputs.released == 'true'
  with:
    docker-username: ${{ secrets.DOCKER_USERNAME }}
    docker-password: ${{ secrets.DOCKER_TOKEN }}
    image-name: efc
    image-tag: ${{ needs.release.outputs.version }}
    target-repository: eyecan/eyeflow-client-py
```

## Security Best Practices

- Always store `docker-username` and `docker-password` as [GitHub Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- Never hardcode credentials in workflows
- Use repository-scoped secrets when possible
- Consider using fine-grained personal access tokens or registry tokens instead of main account passwords

## Notes

- The image must already exist locally in Docker before this action runs
- Use the build-docker-image action to build images in the same workflow
- The `registry` input defaults to Docker Hub's `docker.io`
- For Docker Hub, the registry input should typically remain as the default
