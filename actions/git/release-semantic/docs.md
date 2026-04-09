# Semantic Release Action

A GitHub Action that automates version management and GitHub releases using [python-semantic-release](https://github.com/python-semantic-release/python-semantic-release). Automatically generates version numbers and release notes based on commit messages (following conventional commits format).

## Overview

This action simplifies release workflows by:

- Automatically determining version numbers based on commit history (semantic versioning)
- Creating git tags with proper versioning (e.g., `v1.2.3`)
- Generating GitHub releases with automatic release notes
- Following conventional commit format (feat:, fix:, breaking:, etc.)
- Respecting version constraints in `pyproject.toml`
- Outputting release metadata for use in downstream jobs

Perfect for automated CI/CD release pipelines that need semantic versioning without manual version management.

## Inputs

| Input          | Required | Default | Description                                                              |
| -------------- | -------- | ------- | ------------------------------------------------------------------------ |
| `github-token` | **Yes**  | —       | GitHub token for creating releases and tags (use `secrets.GITHUB_TOKEN`) |
| `commit`       | No       | `false` | Commit version changes to repository (false = tag-only mode).            |
| `push`         | No       | `true`  | Push tags and release info to GitHub                                     |
| `vcs-release`  | No       | `true`  | Create a GitHub release (requires `push: true`)                          |

## Outputs

| Output     | Description                                         | Example  |
| ---------- | --------------------------------------------------- | -------- |
| `released` | Whether a new version was released (`true`/`false`) | `true`   |
| `version`  | Released version number without prefix              | `1.2.3`  |
| `tag`      | Created git tag                                     | `v1.2.3` |

## Usage

### Basic: Automatic Release on Main Branch

```yaml
name: Release

on:
  push:
    branches: [main]

jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Create Release
        uses: m4nh/shared-cicd/actions/release-semantic@main
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
```

### With Python Setup (for version detection)

If your release depends on Python package versioning:

```yaml
jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Create Release
        uses: m4nh/shared-cicd/actions/release-semantic@main
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
```

### Conditional Downstream Jobs Based on Release

```yaml
jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    outputs:
      released: ${{ steps.semrel.outputs.released }}
      version: ${{ steps.semrel.outputs.version }}
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Create Release
        id: semrel
        uses: m4nh/shared-cicd/actions/release-semantic@main
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}

  publish:
    name: Publish to PyPI
    runs-on: ubuntu-latest
    needs: release
    if: needs.release.outputs.released == 'true'
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ needs.release.outputs.tag }}

      - name: Build and publish
        run: |
          python -m build
          twine upload dist/*
```

### Tag-Only Mode (No Commits)

Recommended for most workflows - creates tags and releases without committing:

```yaml
- name: Create Release
  uses: m4nh/shared-cicd/actions/release-semantic@main
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    commit: "false" # Tag-only mode
    push: "true" # Push tags to GitHub
```

### With Version Commit to Repository

If you want to update version files and commit them:

```yaml
- name: Create Release with Commit
  uses: m4nh/shared-cicd/actions/release-semantic@main
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    commit: "true" # Commit version changes
    push: "true"
```

## Commit Message Format

This action uses [Conventional Commits](https://www.conventionalcommits.org/) to determine version bumps:

### Semantic Versioning Rules

```
<type>(<scope>): <subject>
```

- **`feat:`** - New feature → **Minor version bump** (1.0.0 → 1.1.0)
- **`fix:`** - Bug fix → **Patch version bump** (1.0.0 → 1.0.1)
- **`BREAKING CHANGE:`** - Breaking change → **Major version bump** (1.0.0 → 2.0.0)
- **`docs:`, `style:`, `test:`, `chore:`** - No version bump

### Examples

```
feat: Add user authentication           # 1.0.0 → 1.1.0
fix: Correct login redirect             # 1.0.0 → 1.0.1
BREAKING CHANGE: Remove legacy API      # 1.0.0 → 2.0.0
feat!: Redesign configuration format    # 1.0.0 → 2.0.0 (equivalent to BREAKING)
```

## Prerequisites

### Required

1. **Git Repository** - Full git history for semantic versioning

   - Ensure `fetch-depth: 0` in checkout step

2. **GitHub Token** - For creating tags and releases

   - Default `secrets.GITHUB_TOKEN` works in most cases
   - Requires `contents: write` permission

3. **Semantic Versioning Configuration** - In `pyproject.toml`:

```toml
[tool.semantic_release]
version_source = "tag"
branch = "main"
upload_to_vcs_release = true
commit_parser = "angular"
tag_format = "v{version}"
```

### Optional

- **Previous Tags** - Action works without any tags (starts from 0.0.0)
- **Python Setup** - Only needed if using Python-specific version detection

## Workflow Examples

### Complete Release Pipeline

```yaml
name: Release Pipeline

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -e ".[dev]"
      - run: pytest

  release:
    name: Release
    runs-on: ubuntu-latest
    needs: test
    permissions:
      contents: write
    outputs:
      released: ${{ steps.semrel.outputs.released }}
      version: ${{ steps.semrel.outputs.version }}
      tag: ${{ steps.semrel.outputs.tag }}
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Create Release
        id: semrel
        uses: m4nh/shared-cicd/actions/release-semantic@main
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}

  build-and-publish:
    name: Build and Publish
    runs-on: ubuntu-latest
    needs: release
    if: needs.release.outputs.released == 'true'
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ needs.release.outputs.tag }}

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Build wheel
        run: python -m build

      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.PYPI_TOKEN }}

  notify:
    name: Notify
    runs-on: ubuntu-latest
    needs: release
    if: needs.release.outputs.released == 'true'
    steps:
      - name: Announce Release
        run: |
          echo "🎉 Released version ${{ needs.release.outputs.version }}"
          echo "📦 Tag: ${{ needs.release.outputs.tag }}"
          echo "See: https://github.com/${{ github.repository }}/releases/tag/${{ needs.release.outputs.tag }}"
```

### Scheduled Release Check

```yaml
name: Release on Schedule

on:
  schedule:
    - cron: "0 10 * * 1" # Every Monday at 10:00 UTC

jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Create Release
        uses: m4nh/shared-cicd/actions/release-semantic@main
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
```

## Troubleshooting

### No Release Created (released: false)

**Cause**: Commits since last tag don't match conventional commit format.

**Solution**: Ensure commits follow conventional format:

- ✅ `feat: ...` or `fix: ...`
- ❌ `Update readme` or `WIP`

### "No commits found" Error

**Cause**: Repository is shallow cloned or has no commit history.

**Solution**: Add `fetch-depth: 0` to checkout:

```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 0
```

### Permission Denied on Push

**Cause**: GitHub token lacks `contents: write` permission.

**Solution**: Add permissions to job:

```yaml
permissions:
  contents: write
```

### Release Notes Not Generated

**Cause**: `vcs_release: false` or no GitHub release configured.

**Solution**: Ensure `vcs_release: true` (default) and `push: true`.

## Configuration Files

### Minimal `pyproject.toml` for Semantic Release

```toml
[tool.semantic_release]
version_source = "tag"
branch = "main"
upload_to_vcs_release = true
commit_parser = "angular"
tag_format = "v{version}"
```

### Advanced Configuration

```toml
[tool.semantic_release]
version_source = "tag"
branch = "main"
upload_to_vcs_release = true
commit_parser = "angular"
tag_format = "v{version}"
build_command = "pip install build && python -m build"
version_toml = ["pyproject.toml:project.version"]
allow_zero_version = true
```

## Related Actions

- [vcs-version](../python/vcs-version/) - Extract existing semantic version from git tags
- [build-wheel](../python/build-wheel/) - Build Python wheels with automatic versioning

## References

- [python-semantic-release Documentation](https://python-semantic-release.readthedocs.io/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
