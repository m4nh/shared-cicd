# Execute Taskfile Action

A generic GitHub Action to execute tasks from a Taskfile with flexible configuration options.

## Overview

This action provides a simple way to run [Taskfile](https://taskfile.dev/) tasks in your GitHub Actions workflow. It's designed to be flexible and reusable across different projects and directories.

## Prerequisites

- [Taskfile](https://taskfile.dev/) must be installed in your workflow environment
  - For macOS: `brew install go-task/tap/go-task`
  - For Linux: `sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d`
  - For Windows: `choco install task-go` or download from [releases](https://github.com/go-task/task/releases)

## Inputs

| Input      | Description                                                         | Required | Default    |
| ---------- | ------------------------------------------------------------------- | -------- | ---------- |
| `taskfile` | Path to the Taskfile                                                | No       | `Taskfile` |
| `task`     | Task name to execute                                                | **Yes**  | -          |
| `vars`     | Task variables (comma-separated key=value pairs)                    | No       | ``         |
| `dir`      | Working directory to execute the task in                            | No       | `.`        |
| `env-vars` | Environment variables for secrets (comma-separated KEY=VALUE pairs) | No       | ``         |

## Usage Examples

### Basic Usage

Execute the default task from a Taskfile:

```yaml
- name: Run default task
  uses: m4nh/shared-cicd/actions/taskfile@main
  with:
    task: build
```

### With Variables

Pass variables to your task:

```yaml
- name: Run task with variables
  uses: m4nh/shared-cicd/actions/taskfile@main
  with:
    task: deploy
    vars: environment=production,version=1.0.0
```

### Custom Taskfile Path

Specify a custom Taskfile location:

```yaml
- name: Run task from custom Taskfile
  uses: m4nh/shared-cicd/actions/taskfile@main
  with:
    taskfile: ./scripts/Taskfile
    task: test
```

### Custom Working Directory

Execute the task in a specific directory:

```yaml
- name: Run task in subdirectory
  uses: m4nh/shared-cicd/actions/taskfile@main
  with:
    dir: ./backend
    task: lint
```

### Complete Example

Combine all options:

```yaml
- name: Execute comprehensive task
  uses: m4nh/shared-cicd/actions/taskfile@main
  with:
    taskfile: ./deployment/Taskfile
    task: release
    vars: environment=staging,build_number=${{ github.run_number }}
    dir: ./services/api
```

## Security & Secrets

### Using Secrets Safely

The action supports GitHub repository secrets through the `env-vars` input. **Secrets passed this way are automatically masked in logs by GitHub Actions**, making it safe to use API keys, tokens, and other sensitive data.

**⚠️ Important:** Use `env-vars` for secrets, NOT `vars`. The `env-vars` input is designed for sensitive data and will be masked in logs.

### Example: Passing Secrets

```yaml
- name: Deploy with API key
  uses: m4nh/shared-cicd/actions/taskfile@main
  with:
    task: deploy
    vars: environment=production
    env-vars: API_KEY=${{ secrets.DEPLOY_API_KEY }},REGISTRY_TOKEN=${{ secrets.REGISTRY_TOKEN }}
```

In your Taskfile, access these as environment variables:

```yaml
tasks:
  deploy:
    cmds:
      - echo "Deploying to {{.environment}}"
      - ./deploy.sh --token=$API_KEY --registry=$REGISTRY_TOKEN
```

### Why Two Inputs?

- **`vars`**: For non-sensitive task parameters (versions, environments, configurations)
- **`env-vars`**: For secrets and sensitive data (automatically masked in logs by GitHub Actions)

## Full Workflow Example

```yaml
name: Build and Deploy
on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Task
        run: sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d -b /usr/local/bin

      - name: Run tests
        uses: m4nh/shared-cicd/actions/taskfile@main
        with:
          task: test

      - name: Build
        uses: m4nh/shared-cicd/actions/taskfile@main
        with:
          task: build
          vars: version=${{ github.ref_name }}

      - name: Deploy with secrets
        uses: m4nh/shared-cicd/actions/taskfile@main
        with:
          taskfile: ./deployment/Taskfile
          task: deploy
          vars: environment=production,tag=${{ github.sha }}
          env-vars: DEPLOY_TOKEN=${{ secrets.DEPLOY_TOKEN }},DOCKER_REGISTRY=${{ secrets.REGISTRY_HOST }}
          dir: ./deployment
```

## Notes

- The action uses a shell composite action, so it's platform-agnostic (works on Linux, macOS, Windows)
- Task variables are converted to `--set` flags for Task
- Environment variables (secrets) are exposed via the `env-vars` input and **automatically masked in logs by GitHub Actions**
- The working directory is applied at the shell level, so all paths remain relative to that directory
- Ensure your Taskfile exists at the specified path, or the action will fail
- The action avoids using `eval`, making it safer for shell injection attacks

## Troubleshooting

### Task not found

Make sure the task name matches exactly what's defined in your Taskfile (case-sensitive).

### Variables not working

Check that variables are formatted as `key=value` pairs separated by commas, with no spaces around the equals sign.

### File not found

Verify the `taskfile` path is correct relative to your repository root or the `dir` you specified.

### Secrets not visible to task

Ensure you're accessing environment variables in your Taskfile via `$ENV_VAR_NAME` or through your scripting language (e.g., `$API_KEY` in bash, `process.env.API_KEY` in Node.js).

## Related Actions

- [run-pytest](../python/run-pytest) - Run Python tests
- [build-wheel](../python/build-wheel) - Build Python wheels
