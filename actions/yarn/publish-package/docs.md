# Publish NPM Package Action

A GitHub Action that publishes an NPM/Yarn package to a Nexus npm repository using Yarn 4.

## Overview

This action handles authenticating and publishing to Nexus:

- Sets up Node.js and enables Corepack for Yarn 4
- Configures Yarn to point to the Nexus registry with provided credentials
- Publishes the package with `yarn npm publish`

## Inputs

| Input            | Required | Default | Description                                                                         |
| ---------------- | -------- | ------- | ----------------------------------------------------------------------------------- |
| `nexus-username` | Yes      | —       | Nexus username for authentication                                                   |
| `nexus-password` | Yes      | —       | Nexus password for authentication                                                   |
| `repository-url` | Yes      | —       | Nexus npm repository URL (e.g., `https://nexus.example.com/repository/npm-hosted/`) |
| `node-version`   | No       | `20`    | Node.js version to use                                                              |
| `package-path`   | No       | `.`     | Path to the directory containing `package.json`                                     |

## Usage

### Basic

```yaml
- uses: m4nh/shared-cicd/actions/yarn/publish-package@main
  with:
    nexus-username: ${{ secrets.NEXUS_USERNAME }}
    nexus-password: ${{ secrets.NEXUS_PASSWORD }}
    repository-url: ${{ secrets.NEXUS_REPOSITORY_URL }}
```

### With Custom Node Version

```yaml
- uses: m4nh/shared-cicd/actions/yarn/publish-package@main
  with:
    nexus-username: ${{ secrets.NEXUS_USERNAME }}
    nexus-password: ${{ secrets.NEXUS_PASSWORD }}
    repository-url: ${{ secrets.NEXUS_REPOSITORY_URL }}
    node-version: "22"
```

### In a Monorepo

```yaml
- uses: m4nh/shared-cicd/actions/yarn/publish-package@main
  with:
    nexus-username: ${{ secrets.NEXUS_USERNAME }}
    nexus-password: ${{ secrets.NEXUS_PASSWORD }}
    repository-url: ${{ secrets.NEXUS_REPOSITORY_URL }}
    package-path: "packages/my-lib"
```

## Security Notes

- Never hardcode credentials in workflows
- Store `NEXUS_USERNAME`, `NEXUS_PASSWORD`, and `NEXUS_REPOSITORY_URL` as GitHub repository secrets
- Credentials are passed via environment variables, not command-line arguments
