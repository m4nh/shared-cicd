# Extract Version from VCS Action

A simple GitHub Action that extracts the latest semantic version tag from git with a configurable prefix.

## Overview

This action simplifies version extraction in your CI/CD workflows by:

- Automatically fetching the latest semantic version tag from git
- Supporting custom tag prefixes (e.g., `v`, `release-`, etc.)
- Returning the version in two formats: with and without prefix
- Using sensible defaults (prefix `v`, fallback `0.0.0`)
- Clear output indicating whether a tag was found

Perfect for use in release workflows, version bumping, and automated deployments.

## Inputs

| Input              | Required | Default | Description                                               |
| ------------------ | -------- | ------- | --------------------------------------------------------- |
| `tag-prefix`       | No       | `v`     | Prefix for semantic version tags (e.g., `v` for `v1.0.0`) |
| `fallback-version` | No       | `0.0.0` | Version to return if no matching tags found               |

## Outputs

| Output    | Description                                                                       |
| --------- | --------------------------------------------------------------------------------- |
| `version` | The semantic version **without the 'v' prefix** (e.g., `1.2.3` from tag `v1.2.3`) |
| `tag`     | The full git tag **as matched** (e.g., `v1.2.3`)                                  |
| `found`   | Boolean string indicating if a matching tag was found (`true` or `false`)         |

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

### With Custom Tag Prefix

If you use a different tag naming convention:

```yaml
- name: Extract version from release tags
  uses: m4nh/shared-cicd/actions/python/vcs-version@main
  id: version
  with:
    tag-prefix: "release-"

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

This action searches for semantic version tags with a specific prefix in the format `<prefix>X.Y.Z`:

1. Uses `git tag -l '<prefix>*'` to find tags with the specified prefix
2. Filters for semantic version format: `<prefix>[0-9]+\.[0-9]+\.[0-9]+`
3. Returns the latest version using git version sorting
4. Strips the prefix for the `version` output, keeps it for the `tag` output

**Examples with default prefix `v`:**

- ✅ `v1.0.0` → version: `1.0.0`, tag: `v1.0.0`, found: `true`
- ✅ `v2.1.3` → version: `2.1.3`, tag: `v2.1.3`, found: `true`
- ❌ `1.0.0` → not matched (no v prefix)
- ❌ `v1.0.0-beta` → not matched (has suffix)
- ❌ No tags → returns fallback: `0.0.0`, found: `false`

**With custom prefix `release-`:**

```yaml
with:
  tag-prefix: "release-"
```

- ✅ `release-1.0.0` → version: `1.0.0`, tag: `release-1.0.0`, found: `true`
- ✅ `release-2.5.1` → version: `2.5.1`, tag: `release-2.5.1`, found: `true`

## Error Handling

- **No tags found**: Returns fallback version (default `0.0.0`) with `found: false`
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

### Action returns fallback version `0.0.0`

**Cause**: Repository has no semantic version tags matching the prefix.

**Solution**: Create a tag matching your prefix (e.g., `git tag v1.0.0 && git push --tags`) or verify the `tag-prefix` is correct.

### Wrong version returned

**Cause**: Git tags exist but don't match the semantic version format `<prefix>X.Y.Z`.

**Solution**: Check your tag format. Valid: `v1.2.3`, `release-1.2.3`. Invalid: `1.2.3` (wrong prefix), `v1.0.0-beta` (has suffix).

### Version not updated after pushing new tag

**Cause**: GitHub Actions cache or workflow not re-triggering.

**Solution**: Re-run the workflow manually or push a new commit.

## Related Actions

- [extract-python-versions](../extract-python-versions/) - Extract all supported Python versions from `pyproject.toml`
- [build-wheel](../build-wheel/) - Build Python wheels with automatic versioning
