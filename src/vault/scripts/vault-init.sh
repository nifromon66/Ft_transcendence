#!/bin/sh

set -eu

echo "[*] Initializing Vault..."

mkdir -p /usr/local/src/vault/init

vault operator init \
    -tls-skip-verify \
    -key-shares=1 \
    -key-threshold=1 \
    -format=json \
    > /vault/init/init.json

chmod 600 /vault/init/init.json

echo "[✔] Vault initialized."