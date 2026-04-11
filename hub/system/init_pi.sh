#!/bin/bash
#
# Growery: first-time setup on a Raspberry Pi (run ON the Pi).
# Installs Docker (with Compose plugin), rsync, prepares /hub, and configures
# passwordless sudo for docker/rsync so hub/system/deploy.sh can run non-interactively.
#
# Usage:
#   sudo ./init_pi.sh
#   sudo ./init_pi.sh pi          # explicit login name (optional)
#
set -euo pipefail

if [[ "${EUID:-}" -ne 0 ]]; then
    echo "Run this script on the Pi with sudo, e.g.: sudo $0"
    exit 1
fi

TARGET_USER="${1:-${SUDO_USER:-}}"
if [[ -z "${TARGET_USER}" || "${TARGET_USER}" == "root" ]]; then
    echo "Could not determine a non-root user. Usage: sudo $0 [username]"
    echo "Run from a normal account (not a root login) so \\\$SUDO_USER is set, or pass the username."
    exit 1
fi

if ! id -u "${TARGET_USER}" &>/dev/null; then
    echo "User '${TARGET_USER}' does not exist."
    exit 1
fi

echo "==> Growery Pi init for user: ${TARGET_USER}"

export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    rsync \
    openssh-server

if ! command -v docker &>/dev/null; then
    echo "==> Installing Docker Engine (includes Docker Compose plugin)"
    curl -fsSL https://get.docker.com | sh
else
    echo "==> Docker already installed, skipping get.docker.com"
fi

systemctl enable --now docker

echo "==> Adding ${TARGET_USER} to the docker group"
usermod -aG docker "${TARGET_USER}"

echo "==> Preparing deploy path /hub (matches hub/system/deploy.sh PI_PATH)"
mkdir -p /hub
chmod 755 /hub

DOCKER_BIN="$(command -v docker)"
RSYNC_BIN="$(command -v rsync)"

SUDOERS_TMP="$(mktemp)"
trap 'rm -f "${SUDOERS_TMP}"' EXIT

# Passwordless sudo only for docker and rsync — needed for non-interactive deploy over SSH.
printf '%s ALL=(ALL) NOPASSWD: %s, %s\n' "${TARGET_USER}" "${RSYNC_BIN}" "${DOCKER_BIN}" >"${SUDOERS_TMP}"

if ! visudo -c -f "${SUDOERS_TMP}"; then
    echo "Generated sudoers fragment failed validation; not installing."
    exit 1
fi

install -m 0440 -o root -g root "${SUDOERS_TMP}" /etc/sudoers.d/growery-deploy
echo "==> Installed /etc/sudoers.d/growery-deploy"

echo ""
echo "Done."
echo "  - Log out and back in (or reboot) so group 'docker' applies to ${TARGET_USER}."
echo "  - From your dev machine, ensure SSH works: ssh ${TARGET_USER}@<pi-host>"
echo "  - Match PI_USER / PI_HOST in hub/system/deploy.sh and hub/system/logs.sh, then run ./deploy.sh"
echo ""
