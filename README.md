# shared-cicd

Shared GitHub Actions workflows, templates, and organization-wide automation.

## Purpose

This repository contains reusable GitHub configuration and automation shared across all repositories in the organization, including:

- Reusable GitHub Actions workflows
- CI/CD pipelines
- Workflow templates
- Issue templates
- Pull request templates
- Organization standards and conventions

## Repository Structure

```text
shared-cicd/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml
│   │   ├── release.yml
│   │   └── deploy.yml
│   ├── ISSUE_TEMPLATE/
│   └── pull_request_template.md
```

## Reusable Workflows

Reusable workflows are stored in:

```text
.github/workflows/
```

They can be used from any repository in the organization.

Example usage:

```text
jobs:
  ci:
    uses: m4nh/shared-cicd/.github/workflows/ci.yml@main
```

## Creating a Reusable Workflow

Example workflow:

```text
name: Shared CI

on:
  workflow_call:

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4
      - run: echo "Running shared CI"
```

## Usage Guidelines

- Keep workflows generic and reusable
- Prefer inputs instead of hardcoded values
- Document required secrets and permissions
- Avoid repository-specific logic
- Version workflows when making breaking changes

## Versioning

Reference workflows using:

- @main (development)
- @v1.0.0 (stable release tag)
- commit SHA (production-safe)

Example:

```text
uses: m4nh/shared-cicd/.github/workflows/ci.yml@v1.0.0
```

## Contributing

- Ensure workflows are reusable across repositories
- Document inputs, outputs, and secrets
- Test before merging changes
- Keep logic modular and composable

## References

GitHub Actions:
https://docs.github.com/en/actions

Reusable Workflows:
https://docs.github.com/en/actions/using-workflows/reusing-workflows

Composite Actions:
https://docs.github.com/en/actions/creating-actions/creating-a-composite-action
