# GitHub Actions Self-Hosted Runner

This directory contains a Docker Compose setup for running a GitHub Actions self-hosted runner using the [`myoung34/github-runner`](https://hub.docker.com/r/myoung34/github-runner) image.

## Quick Start

### 1. Prerequisites

You need a GitHub Personal Access Token (PAT) with the following scopes:

- **`admin:org`** (required) — Register and manage organization runners
- **`repo`** (required) — Access workflow repositories
- **`workflow`** (required) — Manage GitHub Actions workflows

Additional requirements:
- **Status**: Token must not be expired
- **Access**: User must have admin access to the organization

If you don't have a valid token, create one:

1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select the required scopes:
   - ✓ `admin:org`
   - ✓ `repo` (full control of private repositories)
   - ✓ `workflow` (update GitHub Actions workflows)
4. Click "Generate token"
5. Copy the token and update it in `.env`

### 2. Configure Environment Variables

Edit `.env` and fill in:

```bash
ORG_NAME=m4nh              # Your GitHub organization
RUNNER_NAME=runner-01             # Unique name for this runner
RUNNER_LABELS=linux,x64,docker    # Comma-separated labels for job targeting
RUNNER_GROUP=default              # Runner group (optional)
ACCESS_TOKEN=ghp_xxxxx...         # Your GitHub PAT (admin:org scope)
```

### 3. Start the Runner

```bash
docker-compose up -d
```

### 4. Verify Registration

Check the logs to confirm successful registration:

```bash
docker-compose logs -f github-runner
```

You should see output like:
```
√ Connected to GitHub
√ Runner registration complete
```

Then verify in GitHub:
- Navigate to your organization settings
- Go to **Settings → Actions → Runners**
- Your runner should appear in the list with status "Idle"

## Configuration Details

The `docker-compose.yml` is configured with:

- **RUNNER_SCOPE**: `org` — Registers the runner to your organization
- **GITHUB_HOST**: `github.com` — GitHub instance URL
- **RUNNER_WORKDIR**: `/tmp/github-runner` — Working directory for jobs
- **Persistent Volume**: `runner-data:/actions-runner` — Prevents re-registration on restart
- **Docker Socket**: `/var/run/docker.sock` — Enables Docker commands in workflows

## Key Environment Variables

| Variable | Description |
|----------|-------------|
| `ACCESS_TOKEN` | GitHub PAT with `admin:org` scope (required) |
| `ORG_NAME` | Organization name for org-level runners |
| `RUNNER_NAME` | Unique identifier for this runner |
| `LABELS` | Comma-separated labels for job targeting |
| `RUNNER_SCOPE` | Set to `org` for organization runners |
| `GITHUB_HOST` | GitHub instance (github.com for public GitHub) |
| `RUNNER_WORKDIR` | Working directory for job runs |
| `RUNNER_GROUP` | Runner group name (optional) |

## Troubleshooting

### "Invalid configuration provided for url"

This error means:
- Missing or invalid `RUNNER_SCOPE: org` 
- Missing `ACCESS_TOKEN` or token is expired/invalid
- Token lacks required scopes: `admin:org`, `repo`, or `workflow`

**Solution**: Verify your `.env` file and regenerate your PAT with all three required scopes checked.

### Runner keeps re-registering

This means the persistent volume isn't working:
- Check that `runner-data` volume exists: `docker volume ls | grep runner-data`
- Ensure `/actions-runner` is properly mounted in the container

### Access denied errors

Your PAT lacks proper permissions:
- Verify all required scopes are enabled: `admin:org`, `repo`, `workflow`
- Regenerate the token if scopes are missing
- Verify the token hasn't expired
- Check that your user has admin access to the organization

## Documentation

For complete documentation and advanced configuration, see:

- **Original Docker Image Docs**: https://hub.docker.com/r/myoung34/github-runner
- **GitHub Runner Configuration**: https://github.com/myoung34/docker-github-actions-runner
- **GitHub Actions Self-Hosted Runners**: https://docs.github.com/en/actions/hosting-your-own-runners

## Common Tasks

### Stop the runner

```bash
docker-compose down
```

### View logs

```bash
docker-compose logs -f github-runner
```

### Restart the runner

```bash
docker-compose restart github-runner
```

### Remove and re-register

```bash
docker-compose down -v  # Remove persistent volume
docker-compose up -d    # Start fresh
```

### Update the image

```bash
docker-compose pull
docker-compose up -d
```
