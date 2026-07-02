# CI Svelte Workflow

A reusable GitHub Actions workflow for Svelte and Node.js projects that orchestrates all shared CI actions, including static analysis, type checking, and formatting.

## Overview

This workflow provides a complete CI pipeline for Svelte projects:

- Svelte compiler checks (`svelte-check`)
- TypeScript type checking (`tsc`)
- Linting (`eslint` / `lint-staged`)
- Formatting (`prettier`)

All jobs run in parallel to maximize CI speed and provide fast feedback on pull requests.

## Features

- ✅ Reusable across multiple Svelte repositories
- ✅ Fully configurable behavior via inputs (disable/enable checks as needed)
- ✅ Allows overriding default check commands
- ✅ Parallel execution for maximum speed

## Using This Workflow

### In Another Repository

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