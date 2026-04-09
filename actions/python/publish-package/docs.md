# Publish Package to Nexus Action

A GitHub Action for publishing Python packages to a Nexus repository using twine. Handles authentication and uploads wheels built by the build-wheel action.

## Overview

This action provides a simple, secure way to:

- Set up Python environment
- Install and configure twine for package distribution
- Authenticate with Nexus using credentials
- Upload wheels to your Nexus repository

Perfect for release workflows where you need to publish packages to a private Nexus registry.

## Inputs

| Input            | Required | Default | Description                                   |
| ---------------- | -------- | ------- | --------------------------------------------- |
| `nexus-username` | Yes      | -       | Nexus username for authentication             |
| `nexus-password` | Yes      | -       | Nexus password for authentication             |
| `wheel-path`     | Yes      | -       | Path to wheel file or directory (e.g., dist/) |
| `python-version` | No       | `3.11`  | Python version to use                         |
| `repository-url` | Yes      | -       | Nexus repository URL                          |

## Usage

### Basic: Publish built wheel

```yaml
- name: Publish to Nexus
  uses: m4nh/shared-cicd/actions/python/publish-package@main
  with:
    nexus-username: ${{ secrets.NEXUS_USERNAME }}
    nexus-password: ${{ secrets.NEXUS_PASSWORD }}
    wheel-path: dist/
```

### Complete workflow with build and publish

```yaml
jobs:
  build-and-publish:
    name: Build and Publish Package
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Build wheel
        uses: m4nh/shared-cicd/actions/python/build-wheel@main
        id: build

      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/

  publish:
    name: Publish Package
    runs-on: ubuntu-latest
    needs: build-and-publish

    steps:
      - name: Download artifacts
        uses: actions/download-artifact@v4
        with:
          name: dist
          path: dist/

      - name: Publish to Nexus
        uses: m4nh/shared-cicd/actions/python/publish-package@main
        with:
          nexus-username: ${{ secrets.NEXUS_USERNAME }}
          nexus-password: ${{ secrets.NEXUS_PASSWORD }}
          wheel-path: dist/
          python-version: "3.11"
```

### Using custom Nexus URL

```yaml
- name: Publish to Custom Nexus
  uses: m4nh/shared-cicd/actions/python/publish-package@main
  with:
    nexus-username: ${{ secrets.NEXUS_USERNAME }}
    nexus-password: ${{ secrets.NEXUS_PASSWORD }}
    wheel-path: dist/
    repository-url: https://your-nexus-instance/repository/custom-repo/
```

## Environment Variables

The action uses the following environment variables internally but they're set automatically:

- `TWINE_USERNAME`: Set from `nexus-username` input
- `TWINE_PASSWORD`: Set from `nexus-password` input

## Security Best Practices

- Always store `nexus-username` and `nexus-password` as [GitHub Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- Never hardcode credentials in workflows
- Use repository-scoped secrets when possible
- Consider using fine-grained personal access tokens instead of passwords

## Notes

- The `wheel-path` input can point to a single wheel file or a directory containing wheels
- Multiple wheels can be uploaded by specifying the directory path (e.g., `dist/`)
- Wildcards are supported in the wheel path (e.g., `dist/*.whl`)
- The action requires the wheel file(s) to already exist on the runner
