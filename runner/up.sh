#!/bin/bash
# Start (or update) the runners for one repo: ./up.sh <repo> [replicas]
# REPO_URL comes from the repo name, so the env files only hold the token
# and shared settings; the shell value takes precedence over --env-file.
set -euo pipefail
cd "$(dirname "$0")"

ORG=eyecan-ai

# Which env file (i.e. which token) each repo registers with.
declare -A ENV_FILE=(
  [eyenspect]=.env.eyenspect
  [eyenerf]=.env.eyenspect
  [eyesplat]=.env.eyenspect
  [eyeo]=.env.eyenspect
  [eyecan-neural-twins-bakery]=.env.eyenspect
  [splatty-patty]=.env.eyeflow
  [supaboard]=.env.eyeflow
  [portreyet]=.env.eyeflow
  [eyeflow-client-py]=.env.eyeflow
  # Marco's runners, started from his checkout with his own token.
  [eyeline]=.env.eyeline
  [eyenode]=.env.eyenode
  [eyepick]=.env.eyepick
)

repo=${1:-}
replicas=${2:-2}

if [ -z "$repo" ] || [ -z "${ENV_FILE[$repo]:-}" ]; then
  echo "usage: $0 <repo> [replicas]" >&2
  echo "known repos: $(printf '%s\n' "${!ENV_FILE[@]}" | sort | tr '\n' ' ')" >&2
  exit 1
fi

REPO_URL="https://github.com/$ORG/$repo" \
  docker compose -p "runner-$repo" --env-file "${ENV_FILE[$repo]}" \
  up -d --scale github-runner="$replicas" github-runner
