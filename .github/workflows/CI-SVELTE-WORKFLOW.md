# CI Svelte Workflow

A reusable GitHub Actions workflow for Svelte and Node.js projects that orchestrates all shared CI actions, including static analysis, type checking, and formatting.

## Overview

This workflow provides a complete CI pipeline for Svelte projects:

- Svelte compiler checks (`svelte-check`)
- TypeScript type checking (`tsc`)
- Linting (`eslint`)
- Formatting (`prettier`)

All jobs run in parallel to maximize CI speed and provide fast feedback on pull requests.

## Features

- ✅ Reusable across multiple Svelte repositories
- ✅ Fully configurable behavior via inputs (disable/enable checks as needed)
- ✅ Allows overriding default check commands
- ✅ Parallel execution for maximum speed
- ✅ Support for monorepos with configurable package paths
- ✅ Private npm registry support (Nexus) for scoped packages

## Using This Workflow

### Basic Usage

Create a workflow file in your repo at `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  pull_request:
    branches: [develop, main]
  push:
    branches: [main]

jobs:
  ci:
    uses: m4nh/shared-cicd/.github/workflows/ci-svelte.yml@main
```

### With Custom Inputs

```yaml
jobs:
  ci:
    uses: m4nh/shared-cicd/.github/workflows/ci-svelte.yml@main
    with:
      node-version: "22"
      package-path: "apps/my-svelte-app"
      svelte-check-enabled: true
      tsc-enabled: true
      lint-enabled: true
      prettier-enabled: true
```

### With Private npm Registry

```yaml
jobs:
  ci:
    uses: m4nh/shared-cicd/.github/workflows/ci-svelte.yml@main
    with:
      npm-scope: "myorg"
    secrets:
      NEXUS_USERNAME: ${{ secrets.NEXUS_USERNAME }}
      NEXUS_PASSWORD: ${{ secrets.NEXUS_PASSWORD }}
```

## Inputs

| Input | Description | Type | Default | Required |
|-------|-------------|------|---------|----------|
| `runner` | Runner to use for jobs | `string` | `ubuntu-latest` | ❌ |
| `node-version` | Node.js version to use | `string` | `20` | ❌ |
| `package-path` | Path to directory containing `package.json` | `string` | `.` | ❌ |
| `svelte-check-enabled` | Enable Svelte compiler checks | `boolean` | `true` | ❌ |
| `svelte-check-command` | Command to run for svelte-check | `string` | `yarn svelte-check` | ❌ |
| `tsc-enabled` | Enable TypeScript type checking | `boolean` | `true` | ❌ |
| `tsc-command` | Command to run for type checking | `string` | `yarn tsc --noEmit` | ❌ |
| `lint-enabled` | Enable ESLint | `boolean` | `true` | ❌ |
| `lint-command` | Command to run for linting | `string` | `yarn lint` | ❌ |
| `prettier-enabled` | Enable Prettier formatting check/write | `boolean` | `true` | ❌ |
| `prettier-command` | Command to run for prettier | `string` | `yarn prettier --check .` | ❌ |
| `npm-scope` | Private npm scope to authenticate (e.g., `myorg`) | `string` | `` | ❌ |

## Secrets

| Secret | Description | Required |
|--------|-------------|----------|
| `NEXUS_USERNAME` | Nexus username for private package installation | ❌ (required if `npm-scope` is set) |
| `NEXUS_PASSWORD` | Nexus password for private package installation | ❌ (required if `npm-scope` is set) |

## Jobs

### `svelte-check`
Runs Svelte compiler checks (`svelte-check`) to validate component syntax and type safety.
- Conditional: Controlled by `svelte-check-enabled` input
- Default command: `yarn svelte-check`

### `type-check`
Runs TypeScript type checking (`tsc`) to catch type errors.
- Conditional: Controlled by `tsc-enabled` input
- Default command: `yarn tsc --noEmit`

### `lint`
Runs ESLint to check code quality and style consistency.
- Conditional: Controlled by `lint-enabled` input
- Default command: `yarn lint`

### `prettier`
Runs Prettier to verify code formatting.
- Conditional: Controlled by `prettier-enabled` input
- Default command: `yarn prettier --check .`

## Configuration Examples

### Disable specific checks

```yaml
jobs:
  ci:
    uses: m4nh/shared-cicd/.github/workflows/ci-svelte.yml@main
    with:
      svelte-check-enabled: false  # Skip svelte-check
      prettier-enabled: false      # Skip prettier
```

### Use custom lint command

```yaml
jobs:
  ci:
    uses: m4nh/shared-cicd/.github/workflows/ci-svelte.yml@main
    with:
      lint-command: "yarn lint:fix"  # Custom lint command
```

### Monorepo with multiple packages

```yaml
jobs:
  check-web:
    uses: m4nh/shared-cicd/.github/workflows/ci-svelte.yml@main
    with:
      package-path: "packages/web"
      
  check-admin:
    uses: m4nh/shared-cicd/.github/workflows/ci-svelte.yml@main
    with:
      package-path: "packages/admin"
```

### Run on custom Node.js version

```yaml
jobs:
  ci:
    uses: m4nh/shared-cicd/.github/workflows/ci-svelte.yml@main
    with:
      node-version: "22"
```

## Best Practices

1. **Pin workflow version**: Always use a specific version tag (e.g., `@v1.0.0`) in production instead of `@main`
2. **Parallel execution**: All jobs run in parallel by default for faster feedback
3. **Customize commands**: Override default commands if your project uses custom scripts
4. **Monorepo support**: Use `package-path` for monorepo configurations
5. **Private packages**: Set up Nexus credentials for private npm scopes

## Troubleshooting

### Workflow not found

Error: `Workflow does not exist or is inaccessible`

**Solution**: Ensure you're using the correct workflow path and version tag:
```yaml
uses: m4nh/shared-cicd/.github/workflows/ci-svelte.yml@main
```

### Dependencies not installing

**Solution**: Verify your `package.json` exists at the `package-path` and Corepack is enabled for yarn.

### Private packages failing to install

**Solution**: Ensure both `npm-scope` input and `NEXUS_USERNAME`/`NEXUS_PASSWORD` secrets are properly configured.

## Support

For issues or questions, please refer to the main [shared-cicd README](../README.md)