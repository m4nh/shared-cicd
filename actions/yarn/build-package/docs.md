# Build Node.js Package Action

A GitHub Action that sets up Node.js with Yarn 4 (via Corepack), optionally stamps a version into `package.json`, installs dependencies, and builds the package.

## Overview

This action handles the complete Node.js build lifecycle:

- Sets up Node.js with the specified version
- Enables Corepack to activate the project's Yarn version (`packageManager` field)
- Optionally stamps a custom version into `package.json` before building
- Installs dependencies with `yarn install --immutable`
- Builds the package with `yarn build` (or a custom command)

## Inputs

| Input           | Required | Default | Description                                                                                                           |
| --------------- | -------- | ------- | --------------------------------------------------------------------------------------------------------------------- |
| `node-version`  | No       | `20`    | Node.js version to use                                                                                                |
| `package-path`  | No       | `.`     | Path to the directory containing `package.json`                                                                       |
| `build-command` | No       | `build` | Yarn build command to run (e.g., `build`, `build:prod`)                                                               |
| `version`       | No       | ``      | Version to stamp into `package.json` before building (e.g., `1.2.3-dev.4`). If empty, `package.json` is not modified. |

## Usage

### Basic Build

```yaml
- uses: m4nh/shared-cicd/actions/yarn/build-package@main
```

### With Version Stamping

```yaml
- uses: m4nh/shared-cicd/actions/yarn/build-package@main
  with:
    version: ${{ needs.compute-version.outputs.semver-version }}
```

### With Custom Build Command and Node Version

```yaml
- uses: m4nh/shared-cicd/actions/yarn/build-package@main
  with:
    build-command: "build:prod"
    node-version: "22"
    version: ${{ needs.release.outputs.version }}
```

### In a Monorepo

```yaml
- uses: m4nh/shared-cicd/actions/yarn/build-package@main
  with:
    package-path: "packages/my-app"
    version: ${{ needs.compute-version.outputs.semver-version }}
```

## Requirements

- The project must have a `packageManager` field in `package.json` pointing to a Yarn 4.x version (e.g., `"yarn@4.10.3"`)
- Corepack is included by default with all official Node.js distributions starting from Node 16.9
