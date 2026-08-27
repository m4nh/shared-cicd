# GitHub Actions Self-Hosted Runner (Unified: Repo + Org)

This setup runs a GitHub Actions self-hosted runner that supports both repo and org scope using a single configuration.

Mode is controlled by:

```bash
RUNNER_SCOPE=repo | org
```

## Quick Start

### 1. Prerequisites

GitHub PAT scopes:

- repo mode: repo, workflow
- org mode: admin:org, repo, workflow

Token must be valid and have access to target repo/org.

### 2. .env file

```bash
RUNNER_SCOPE=repo

REPO_URL=https://github.com/your-org/your-repo
ORG_NAME=your-org

RUNNER_NAME_PREFIX=runner
RUNNER_LABELS=linux,x64,docker
RUNNER_GROUP=default

ACCESS_TOKEN=ghp_xxxxx...
```

### 3. Start runner

```bash
docker compose up -d
```

Optional scaling:

```bash
docker compose up -d --scale github-runner=2
```

### 4. Verify

```bash
docker compose logs -f github-runner
```

Expected:
√ Connected to GitHub
√ Runner registration complete

## How it works

The container uses `RUNNER_SCOPE` to decide registration:

```bash
if RUNNER_SCOPE = repo:
register using REPO_URL

if RUNNER_SCOPE = org:
register using ORG_NAME with --organization flag
```

## Key variables

```bash
RUNNER_SCOPE -> repo or org
ACCESS_TOKEN -> GitHub PAT
REPO_URL -> required for repo mode
ORG_NAME -> required for org mode
RUNNER_LABELS -> workflow targeting
RUNNER_GROUP -> optional grouping
RUNNER_WORKDIR -> job directory
EPHEMERAL -> remove runner after job
```

## Workflow targeting

```bash
runs-on: [self-hosted, linux, docker]
```

Labels must match `RUNNER_LABELS`.

## Repo vs Org

Repo:

- single repository
- high isolation

Org:

- shared across repos
- centralized compute pool

## Troubleshooting

### DNS/Network Issues During Build

If `docker compose up` fails with DNS resolution errors (e.g., "Temporary failure resolving 'archive.ubuntu.com'"), build the image manually with host networking:

```bash
# Stop any running containers
docker compose down

# Build with host networking
DOCKER_BUILDKIT=1 docker build --network=host -t runner-github-runner -f Dockerfile .

# Start containers
docker compose up -d --scale github-runner=4
```

### Missing libGL.so.1 Error

If your CI jobs fail with:

```
ImportError: libGL.so.1: cannot open shared object file: No such file or directory
```

The Dockerfile includes `libgl1-mesa-glx` to fix this. Verify it's installed:

```bash
docker exec runner-github-runner-1 ldconfig -p | grep libGL
```

### Rebuilding from Scratch

```bash
docker compose down
docker compose build --no-cache
docker compose up -d --scale github-runner=4
```
