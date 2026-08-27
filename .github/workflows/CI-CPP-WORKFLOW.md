# CI C++ Workflow

A reusable GitHub Actions workflow for C++ projects that orchestrates testing, formatting checks, and Docker builds.

## Overview

This workflow provides a complete CI pipeline for C++ projects including:

- Code formatting checks with clang-format
- CMake build and testing with CTest
- Docker image building

## Features

- ✅ Reusable across multiple C++ repositories
- ✅ Fully configurable behavior via inputs
- ✅ Parallel execution for speed
- ✅ Optional features (formatting, tests, Docker)
- ✅ Modern C++ support (C++17, C++20, etc.)

## Using This Workflow

### In Another Repository

Create a workflow file in your repo at `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  pull_request:

jobs:
  ci:
    uses: m4nh/shared-cicd/.github/workflows/ci-cpp.yml@main
```

### With Default Configuration

Uses all defaults:

- Ubuntu 22.04 runner
- Format checking with clang-format enabled
- CMake build in Release mode with tests enabled
- Docker building enabled (looks for `Dockerfile` in repo root)

### Custom Configuration

```yaml
jobs:
  ci:
    uses: m4nh/shared-cicd/.github/workflows/ci-cpp.yml@main
    with:
      runner: "ubuntu-22.04"
      format-check-enabled: true
      tests-enabled: true
      cmake-build-type: "Release"
      docker-build-enabled: true
      docker-dockerfile: "dockerfiles/Dockerfile"
```

## Inputs

### General

| Input    | Type   | Default        | Description          |
| -------- | ------ | -------------- | -------------------- |
| `runner` | string | `ubuntu-22.04` | GitHub runner to use |

### Format Checking

| Input                   | Type    | Default | Description                       |
| ----------------------- | ------- | ------- | --------------------------------- |
| `format-check-enabled`  | boolean | `true`  | Enable clang-format check         |

**Note:** The format check looks for `.clang-format` in the repository root and validates all `.cpp` and `.hpp` files in `src/`, `includes/`, and `tests/` directories.

### Build & Testing

| Input               | Type    | Default                 | Description                           |
| ------------------- | ------- | ----------------------- | ------------------------------------- |
| `tests-enabled`     | boolean | `true`                  | Enable CMake build and testing        |
| `cmake-build-type`  | string  | `Release`               | CMake build type                      |
| `cmake-extra-args`  | string  | ``                      | Additional CMake configuration args   |
| `ctest-args`        | string  | `--output-on-failure`   | Additional arguments to pass to ctest |

**System Dependencies Installed:**
The workflow automatically installs all necessary dependencies for building C++ projects:
- Build tools: `build-essential`, `git`, `pkg-config`, `cmake 3.29.8`
- Image/Graphics: `libopencv-dev`, `libgl1-mesa-dev`, `libglu1-mesa-dev`, `libx11-dev`, `libglew-dev`
- Numerical: `libboost-all-dev`, `libeigen3-dev`, `libceres-dev`, `libsuitesparse-dev`
- Geometry: `libcgal-dev`, `libcgal-qt5-dev`
- Other: `nlohmann-json3-dev`, `libyaml-cpp-dev`, `libsqlite3-dev`, `libgoogle-glog-dev`

### Docker Building

| Input                 | Type    | Default      | Description                               |
| --------------------- | ------- | ------------ | ----------------------------------------- |
| `docker-build-enabled`| boolean | `true`       | Enable Docker building                    |
| `docker-dockerfile`   | string  | `Dockerfile` | Path to Dockerfile                        |
| `docker-context`      | string  | `.`          | Docker build context directory            |
| `docker-tags`         | string  | `ci:latest`  | Docker image tags (comma/space-separated) |
| `docker-build-args`   | string  | ``           | Build arguments (e.g., `--build-arg K=V`) |

## Complete Examples

### Basic C++ Project

```yaml
name: CI

on:
  pull_request:
  push:
    branches: [main]

jobs:
  ci:
    uses: m4nh/shared-cicd/.github/workflows/ci-cpp.yml@main
```

### With Custom Dockerfile Path

```yaml
jobs:
  ci:
    uses: m4nh/shared-cicd/.github/workflows/ci-cpp.yml@main
    with:
      docker-dockerfile: "dockerfiles/Dockerfile"
```

### Debug Build

```yaml
jobs:
  ci:
    uses: m4nh/shared-cicd/.github/workflows/ci-cpp.yml@main
    with:
      cmake-build-type: "Debug"
```

### With Custom CMake Arguments

```yaml
jobs:
  ci:
    uses: m4nh/shared-cicd/.github/workflows/ci-cpp.yml@main
    with:
      cmake-extra-args: "-DENABLE_SANITIZERS=ON -DBUILD_EXAMPLES=OFF"
```

### Disable Format Checking

```yaml
jobs:
  ci:
    uses: m4nh/shared-cicd/.github/workflows/ci-cpp.yml@main
    with:
      format-check-enabled: false
```

### Tests Only (No Docker)

```yaml
jobs:
  ci:
    uses: m4nh/shared-cicd/.github/workflows/ci-cpp.yml@main
    with:
      docker-build-enabled: false
```

### Minimal Configuration (Format and Tests Only)

```yaml
jobs:
  ci:
    uses: m4nh/shared-cicd/.github/workflows/ci-cpp.yml@main
    with:
      docker-build-enabled: false
```

### Verbose Test Output

```yaml
jobs:
  ci:
    uses: m4nh/shared-cicd/.github/workflows/ci-cpp.yml@main
    with:
      ctest-args: "--verbose --output-on-failure"
```

### Full-Featured Pipeline

```yaml
name: CI/CD

on:
  pull_request:
    branches: [develop, main]
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  ci:
    uses: m4nh/shared-cicd/.github/workflows/ci-cpp.yml@main
    with:
      runner: "ubuntu-22.04"
      format-check-enabled: true
      tests-enabled: true
      cmake-build-type: "Release"
      cmake-extra-args: "-DENABLE_COVERAGE=ON"
      ctest-args: "--output-on-failure --parallel 4"
      docker-build-enabled: true
      docker-dockerfile: "dockerfiles/Dockerfile"
      docker-context: "."
      docker-tags: "myapp:ci,myapp:${{ github.sha }}"
      docker-build-args: "--build-arg VERSION=${{ github.ref_name }}"
```

## Workflow Jobs

The workflow consists of three independent jobs that run in parallel:

### 1. Format Check (`format-check`)

- Installs clang-format
- Checks all C++ files (`*.cpp`, `*.hpp`) in `src/`, `includes/`, and `tests/`
- Fails if code doesn't match `.clang-format` configuration
- Controlled by: `format-check-enabled`

**Prerequisites:**
- Repository must have `.clang-format` file at the root

**To fix formatting locally:**
```bash
find src includes tests -name "*.cpp" -o -name "*.hpp" | xargs clang-format -i
```

### 2. Build & Test (`build-and-test`)

- Installs all system dependencies
- Installs CMake 3.29.8 (newer than Ubuntu 22.04 default)
- Configures CMake with specified build type
- Builds project with parallel compilation
- Runs all tests via CTest
- Controlled by: `tests-enabled`

**Prerequisites:**
- Repository must have `CMakeLists.txt` at the root
- Tests should be discoverable by CTest

### 3. Docker Build (`docker-build`)

- Uses the existing `m4nh/shared-cicd/actions/docker/build-docker-image@main` action
- Builds Docker image from specified Dockerfile
- Tags image with specified tags
- Validates image builds successfully (no push in CI)
- Controlled by: `docker-build-enabled`

**Prerequisites:**
- Repository must have Dockerfile at specified path

## Requirements

### Repository Structure

Your C++ repository should have:

```
your-repo/
├── .clang-format           # C++ formatting configuration
├── CMakeLists.txt          # CMake build configuration
├── src/                    # Source files
├── includes/               # Header files
├── tests/                  # Test files
└── Dockerfile              # Optional: for Docker builds
```

### .clang-format Configuration

Create a `.clang-format` file in your repository root. Example:

```yaml
BasedOnStyle: LLVM
Language: Cpp
Standard: Latest
ColumnLimit: 100
IndentWidth: 2
```

### CMakeLists.txt

Your CMakeLists.txt should support test building. Example:

```cmake
cmake_minimum_required(VERSION 3.20)
project(MyProject)

# ... your project configuration ...

# Tests (controlled by workflow)
option(BUILD_TESTS "Build tests" OFF)
if(BUILD_TESTS)
  enable_testing()
  add_subdirectory(tests)
endif()
```

The workflow automatically passes `-DBUILD_TESTS=ON` or your custom variable via `cmake-extra-args`.

## Troubleshooting

### Format Check Fails

**Symptom:** Format check job fails with formatting violations.

**Solution:**
```bash
# Run locally to fix
find src includes tests -name "*.cpp" -o -name "*.hpp" | xargs clang-format -i

# Or check what would change
find src includes tests -name "*.cpp" -o -name "*.hpp" | xargs clang-format --dry-run -Werror
```

### Build Fails Due to Missing Dependencies

**Symptom:** Build job fails with missing library errors.

**Solution:** The workflow installs a comprehensive set of dependencies. If you need additional packages, use `cmake-extra-args` to skip features or add a custom setup step in your repository workflow before calling the reusable workflow.

### Tests Fail

**Symptom:** CTest reports test failures.

**Solution:** Check the test output in the workflow logs. The `--output-on-failure` flag ensures failed test details are shown. Run tests locally:
```bash
cmake -B build -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTS=ON
cmake --build build
ctest --test-dir build --output-on-failure
```

### Docker Build Fails

**Symptom:** Docker build job fails.

**Solution:**
- Verify the Dockerfile path is correct (`docker-dockerfile` input)
- Test Docker build locally: `docker build -f <dockerfile-path> .`
- Check if build context is correct (`docker-context` input)

## Related Actions

This workflow uses the following shared actions:

- [`m4nh/shared-cicd/actions/docker/build-docker-image`](../../actions/docker/build-docker-image/docs.md) - Docker image building

## Version Pinning

### Using Latest

```yaml
uses: m4nh/shared-cicd/.github/workflows/ci-cpp.yml@main
```

### Using Specific Version

```yaml
uses: m4nh/shared-cicd/.github/workflows/ci-cpp.yml@v1.0.0
```

### Using Commit SHA (Most Stable)

```yaml
uses: m4nh/shared-cicd/.github/workflows/ci-cpp.yml@a1b2c3d4
```

## Support

For issues or questions:
1. Check the [troubleshooting section](#troubleshooting)
2. Review the [complete examples](#complete-examples)
3. Open an issue in the shared-cicd repository
