#!/bin/bash
# Fix docker socket permissions every time the container starts.
# This ensures Jenkins can always reach the Docker daemon
chmod 666 /var/run/docker.sock 2>/dev/null || true

# Hand off to the original Jenkins entrypoint
exec /usr/bin/tini -- /usr/local/bin/jenkins.sh "$@"