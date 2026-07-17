#!/usr/bin/env bash
set -euo pipefail

SWAP_SIZE_MB=${SWAP_SIZE_MB:-1024}
SWAPFILE=${SWAPFILE:-/swapfile}

if swapon --show | grep -q "$SWAPFILE"; then
  echo "swap already enabled on $SWAPFILE"
  exit 0
fi

sudo fallocate -l "${SWAP_SIZE_MB}M" "$SWAPFILE"
sudo chmod 600 "$SWAPFILE"
sudo mkswap "$SWAPFILE"
sudo swapon "$SWAPFILE"
if ! grep -q "$SWAPFILE" /etc/fstab; then
  echo "$SWAPFILE none swap sw 0 0" | sudo tee -a /etc/fstab >/dev/null
fi
swapon --show
free -h
