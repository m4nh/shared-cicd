# Extract Version from VCS Action

A composite GitHub Action that extracts the latest semantic version from git tags in your repository.

## Overview

This action simplifies version extraction in your CI/CD workflows by:

- Automatically fetching the latest semantic version tag from git
- Returning the version in multiple formats (with/without prefix, full tag)
- Supporting optional fallback versions for repositories without tags
- Customizable tag pattern matching
- Clear output indicating whether a tag was found

Perfect for use in release workflows, version bumping, and automated deployments.

## Inputs

| Input              | Required | Default | Description                                                                      |
| ------------------ | -------- | ------- | -------------------------------------------------------------------------------- |
| `tag-pattern`      | No       | `v*`    | Regex pattern for git tags to search (e.g., `v*`, `release-*`)                   |
| `fallback-version` | No       | —       | Version to return if no matching tags found (if not provided, action will error) |

## Outputs

| Output    | Description                                                               |
| --------- | ------------------------------------------------------------------------- |
| `version` | The semantic version without the 'v' prefix (e.g., `1.2.3`)               |
| `tag`     | The full git tag including prefix (e.g., `v1.2.3`)                        |
| `found`   | Boolean string indicating if a matching tag was found (`true` or `false`) |

## Usage

### Basic Example

Extract the latest semantic version tag:

```yaml
name: Release

on:
  push:
    branches: [main]

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Extract version from tags
        uses: m4nh/shared-cicd/actions/python/vcs-version@main
        id: version

      - name: Create release
        run: |
          echo "Latest version: ${{ steps.version.outputs.version }}"
          echo "Full tag: ${{ steps.version.outputs.tag }}"
```

### With Fallback Version

For repositories that might not have any tags yet, provide a fallback:

```yaml
- name: Extract version from tags
  uses: m4nh/shared-cicd/actions/python/vcs-version@main
  id: version
  with:
    fallback-version: "0.1.0"

- name: Use version
  run: |
    echo "Version: ${{ steps.version.outputs.version }}"
    echo "Was found: ${{ steps.version.outputs.found }}"
```

### With Custom Tag Pattern

If you use a different tag naming convention:

```yaml
- name: Extract version from release tags
  uses: m4nh/shared-cicd/actions/python/vcs-version@main
  id: version
  with:
    tag-pattern: "release-*"

- name: Build with version
  run: |
    docker build -t myapp:${{ steps.version.outputs.version }} .
```

### Conditional Steps Based on Tag Found

```yaml
- name: Extract version
  uses: m4nh/shared-cicd/actions/python/vcs-version@main
  id: version
  with:
    fallback-version: "0.1.0"

- name: Create release (only if tag exists)
  if: steps.version.outputs.found == 'true'
  run: |
    gh release create ${{ steps.version.outputs.tag }} --generate-notes

- name: Log fallback usage
  if: steps.version.outputs.found == 'false'
  run: |
    echo "No tags found, using fallback: ${{ steps.version.outputs.version }}"
```

## How It Works

1. **Fetches all git history** - Uses `fetch-depth: 0` to retrieve all tags
2. **Searches for semantic version tags** - Looks for tags matching the pattern `vX.Y.Z` (e.g., `v1.2.3`, `v2.0.0`)
3. **Returns the latest tag** - Uses git version sorting to find the most recent version
4. **Extracts version variants** - Provides both prefixed and unprefixed versions for flexibility

## Tag Format Requirements

By default, this action expects git tags in semantic versioning format with a `v` prefix:

- ✅ Valid: `v1.0.0`, `v2.1.3`, `v0.1.0`
- ❌ Invalid: `1.0.0` (missing `v`), `version-1.0.0` (wrong prefix), `v1.0` (incomplete version)

To support different naming schemes, use the `tag-pattern` input with a custom regex:

```yaml
with:
  tag-pattern: "release-*"
```

## Error Handling

- **No tags found & no fallback**: Action fails with error message
- **No tags found & fallback provided**: Action succeeds, returns fallback version with `found: false`
- **Invalid tag format**: Tags that don't match the semantic version pattern are ignored

## Common Patterns

### Use in Build Workflows

```yaml
- name: Extract version
  uses: m4nh/shared-cicd/actions/python/vcs-version@main
  id: version

- name: Build Docker image
  run: |
    docker build \
      -t myregistry/myimage:${{ steps.version.outputs.version }} \
      -t myregistry/myimage:latest \
      .
```

### Use in Release Workflows

```yaml
- name: Extract version
  uses: m4nh/shared-cicd/actions/python/vcs-version@main
  id: version

- name: Publish to PyPI
  env:
    TWINE_USERNAME: __token__
    TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}
  run: |
    python -m build
    twine upload dist/* --skip-existing
```

### Matrix Strategy with Version

```yaml
jobs:
  get-version:
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.version.outputs.version }}
    steps:
      - uses: actions/checkout@v4
      - name: Extract version
        uses: m4nh/shared-cicd/actions/python/vcs-version@main
        id: version

  deploy:
    needs: get-version
    runs-on: ubuntu-latest
    strategy:
      matrix:
        environment: [staging, production]
    steps:
      - run: echo "Deploying version ${{ needs.get-version.outputs.version }} to ${{ matrix.environment }}"
```

## Troubleshooting

### Action fails with "No release tags found"

**Cause**: Repository has no semantic version tags.

**Solution**: Either create a tag (`git tag v1.0.0 && git push --tags`) or use the `fallback-version` input.

### Wrong version returned

**Cause**: Git tags exist but don't match the expected pattern.

**Solution**: Check your tag format. Valid: `v1.2.3`. Invalid: `1.2.3` or `release-1.2.3` (use `tag-pattern: "release-*"` for custom formats).

### Version not updated after pushing new tag

**Cause**: GitHub Actions cache or workflow not re-triggering.

**Solution**: Re-run the workflow manually or push a new commit.

## Related Actions

- [extract-python-versions](../extract-python-versions/) - Extract all supported Python versions from `pyproject.toml`
- [build-wheel](../build-wheel/) - Build Python wheels with automatic versioning
