FROM myoung34/github-runner:latest


# OpenCV dependencies including libGL.so.1 for Python OpenCV
# Note: If you experience DNS failures during build, use:
#   DOCKER_BUILDKIT=1 docker build --network=host -t runner-github-runner -f Dockerfile .
# Then run: docker compose up -d --scale github-runner=4
RUN for i in 1 2 3; do \
  apt-get update && \
  apt-get install -y --no-install-recommends --fix-missing \
  ffmpeg libsm6 libxext6 libgl1-mesa-glx && \
  break || sleep 5; \
  done && \
  rm -rf /var/lib/apt/lists/*


