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

All repos share one image, `shared-cicd/github-runner:latest`. Build it once, and again whenever the Dockerfile changes:

```bash
docker compose build github-runner
```

Then start each repo's runners. `up.sh` sets `REPO_URL` from the repo name and picks the env file (token) for it from the table at its top; add new repos there:

```bash
./up.sh eyenerf        # 2 runners
./up.sh eyenerf 4      # 4 runners
```

Don't pass `--build` per repo: that's only needed once, and the shared tag means every project picks up the new image on its next `./up.sh`.

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
# Build with host networking
DOCKER_BUILDKIT=1 docker build --network=host -t shared-cicd/github-runner:latest -f Dockerfile .

# Restart each repo's runners on the new image
./up.sh <repo>
```

### Missing libGL.so.1 Error

If your CI jobs fail with:

```
ImportError: libGL.so.1: cannot open shared object file: No such file or directory
```

The Dockerfile includes `libgl1-mesa-glx` to fix this. Verify it's installed:

```bash
docker exec runner-<repo>-github-runner-1 ldconfig -p | grep libGL
```

### Rebuilding from Scratch

```bash
docker compose build --no-cache github-runner
./up.sh <repo>   # for each repo
```

### Runners Stuck After a Network Outage

If the runner loses its connection to GitHub, it exits and tries to deregister. When the network is down, that deregistration can hang indefinitely while the container still shows as `Up`. Each runner has a healthcheck that verifies `Runner.Listener run` is alive, and the `autoheal` service restarts any container that becomes unhealthy (after about 5 minutes).

```bash
docker ps --filter name=runner- --format 'table {{.Names}}\t{{.Status}}'
```

Runners that never finished deregistering stay listed as offline under the repo's Settings → Actions → Runners; remove them there.

### Stale Packages From Earlier Jobs

With `EPHEMERAL` set, the runner exits after each job and Docker restarts the same container, so its filesystem carries over between jobs. Left alone, the toolcache Pythons (with torch installed into them), pip caches and `/tmp` leftovers grew to 20–35 GB per container. To keep jobs isolated, `cleanup-entrypoint.sh` empties `/opt/hostedtoolcache`, `/root/.cache` and `/tmp` (which holds the runner work directory) every time the container starts. Each job therefore installs Python again, but packages come from the pip cache.

The pip cache (`/root/.cache/pip`) is not wiped: it's the `github-runner-pip-cache` volume, shared by every runner on the host. It only grows, so purge it now and then:

```bash
docker run --rm -v github-runner-pip-cache:/c alpine sh -c 'rm -rf /c/*'
```

Containers created before this change don't run the cleanup. Rebuild the image and rerun `./up.sh <repo>` for each repo.
