#!/bin/sh

set -eu

UNSEAL_KEY=$(
    jq -r '.unseal_keys_b64[0]' \
        /vault/init/init.json
)

vault operator unseal \
    -tls-skip-verify \
    "$UNSEAL_KEY"