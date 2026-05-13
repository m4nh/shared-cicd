# GitHub Actions Self-Hosted Runner (Repository)

This directory contains a Docker Compose setup for running a GitHub Actions self-hosted runner scoped to a **single repository**, using the [`myoung34/github-runner`](https://hub.docker.com/r/myoung34/github-runner) image.

## Quick Start

### 1. Prerequisites

You need a GitHub Personal Access Token (PAT) with the following scopes:

- **`repo`** (required) — Full control of private repositories, including registering runners
- **`workflow`** (required) — Manage GitHub Actions workflows

Additional requirements:
- **Status**: Token must not be expired
- **Access**: User must have admin access to the repository

If you don't have a valid token, create one:

1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select the required scopes:
   - ✓ `repo` (full control of private repositories)
   - ✓ `workflow` (update GitHub Actions workflows)
4. Click "Generate token"
5. Copy the token and update it in `.env`

### 2. Configure Environment Variables

Create a `.env` file in this directory and fill in:

```bash
REPO_URL=https://github.com/your-org/your-repo   # Full URL of the target repository
RUNNER_NAME_PREFIX=runner                          # Prefix for the runner name
RUNNER_LABELS=linux,x64,docker                    # Comma-separated labels for job targeting
RUNNER_GROUP=default                               # Runner group (optional)
ACCESS_TOKEN=ghp_xxxxx...                         # Your GitHub PAT (repo scope)
```

### 3. Start the Runner

```bash
docker compose up -d
```

### 4. Verify Registration

Check the logs to confirm successful registration:

```bash
docker compose logs -f github-runner-1
```

You should see output like:
```
√ Connected to GitHub
√ Runner registration complete
```

Then verify in GitHub:
- Navigate to your repository
- Go to **Settings → Actions → Runners**
- Your runner should appear in the list with status "Idle"

## Configuration Details

The `docker compose.yml` is configured with:

- **RUNNER_SCOPE**: `repo` — Registers the runner to a single repository
- **GITHUB_HOST**: `github.com` — GitHub instance URL
- **RUNNER_WORKDIR**: `/tmp/github-runner-1` — Working directory for jobs
- **Persistent Volume**: `runner-data-1:/actions-runner` — Prevents re-registration on restart
- **Docker Socket**: `/var/run/docker.sock` — Enables Docker commands in workflows

## Key Environment Variables

| Variable | Description |
|----------|-------------|
| `ACCESS_TOKEN` | GitHub PAT with `repo` scope (required) |
| `REPO_URL` | Full URL of the repository, e.g. `https://github.com/owner/repo` |
| `RUNNER_NAME_PREFIX` | Prefix for the auto-generated runner name |
| `RUNNER_LABELS` | Comma-separated labels for job targeting |
| `RUNNER_SCOPE` | Set to `repo` for repository-scoped runners |
| `GITHUB_HOST` | GitHub instance (github.com for public GitHub) |
| `RUNNER_WORKDIR` | Working directory for job runs |
| `RUNNER_GROUP` | Runner group name (optional) |

## Differences from Organization Runner

| | Org Runner | Repo Runner |
|---|---|---|
| `RUNNER_SCOPE` | `org` | `repo` |
| Registration target | `ORG_NAME` | `REPO_URL` |
| PAT scope needed | `admin:org`, `repo`, `workflow` | `repo`, `workflow` |
| Visible in | Org Settings → Actions → Runners | Repo Settings → Actions → Runners |

## Troubleshooting

### "Invalid configuration provided for url"

This error means:
- Missing or invalid `REPO_URL` (must be the full URL, e.g. `https://github.com/owner/repo`)
- Missing `ACCESS_TOKEN` or token is expired/invalid
- Token lacks the required `repo` scope

**Solution**: Verify your `.env` file and regenerate your PAT with both `repo` and `workflow` scopes checked.

### Runner registers but jobs are not picked up

- Ensure the labels in `RUNNER_LABELS` match the `runs-on` value in your workflow
- Verify the runner appears as **Idle** in the repository settings
