#!/usr/bin/env bash
# Deploys the given image to a Docker host. Run by Jenkins over SSH, or locally.
# Usage: scripts/deploy.sh <image:tag> [container-name] [host-port]
set -euo pipefail

IMAGE="${1:?usage: deploy.sh <image:tag> [container-name] [host-port]}"
NAME="${2:-flask-jenkins-app}"
HOST_PORT="${3:-5000}"

echo "Pulling ${IMAGE}"
docker pull "${IMAGE}"

echo "Replacing container ${NAME}"
docker rm -f "${NAME}" >/dev/null 2>&1 || true
docker run -d \
  --name "${NAME}" \
  --restart unless-stopped \
  -p "${HOST_PORT}:5000" \
  "${IMAGE}"

echo "Waiting for health check"
for i in $(seq 1 15); do
  if curl -fsS "http://localhost:${HOST_PORT}/health" >/dev/null; then
    echo "Deployment healthy"
    exit 0
  fi
  sleep 2
done

echo "Deployment failed health check" >&2
docker logs "${NAME}" || true
exit 1
