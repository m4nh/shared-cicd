# Ubuntu 22.04, pinned: `latest` was Ubuntu 20.04, whose glibc 2.31 cannot load wheels
# built on newer systems and whose SQLite 3.31 breaks coverage>=7.17.1 (pytest-cov
# fails at the end of the run with "attempt to write a readonly database").
FROM myoung34/github-runner:ubuntu-jammy


# OpenCV dependencies including libGL.so.1 for Python OpenCV
# Note: If you experience DNS failures during build, use:
#   DOCKER_BUILDKIT=1 docker build --network=host -t shared-cicd/github-runner:latest -f Dockerfile .
# Then start each repo with: ./up.sh <repo>
RUN for i in 1 2 3; do \
  apt-get update && \
  apt-get install -y --no-install-recommends --fix-missing \
  ffmpeg libsm6 libxext6 libgl1 && \
  ok=1 && break; \
  sleep 5; \
  done; \
  [ "$ok" = 1 ] || exit 1; \
  rm -rf /var/lib/apt/lists/*

# Wipe caches left by earlier jobs before the runner registers.
COPY --chmod=755 cleanup-entrypoint.sh /cleanup-entrypoint.sh
ENTRYPOINT ["/cleanup-entrypoint.sh"]
# Setting ENTRYPOINT clears the base image's CMD, so restate it.
CMD ["./bin/Runner.Listener", "run", "--startuptype", "service"]

