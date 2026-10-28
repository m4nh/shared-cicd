#!/bin/bash
# Ephemeral runners restart inside the same container after each job, so
# anything a job installed (toolcache Pythons, caches, checkouts, temp files)
# survives into the next one. Wipe it so every job starts like a fresh runner.
# /tmp also holds RUNNER_WORKDIR (/tmp/github-runner).
for dir in "${AGENT_TOOLSDIRECTORY:-/opt/hostedtoolcache}" /root/.cache /tmp; do
  if [ -d "$dir" ]; then
    echo "Cleaning $dir"
    # Keep the pip cache: it's a volume shared by all runners.
    find "$dir" -mindepth 1 -maxdepth 1 ! -path /root/.cache/pip -exec rm -rf {} +
  fi
done

exec /entrypoint.sh "$@"
