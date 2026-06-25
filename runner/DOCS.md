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
