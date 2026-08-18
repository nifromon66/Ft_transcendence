#!/bin/sh

set -eu

. ${VAULT_LIB_SH_PATH}

log_info "Vault AppRole logging out..."

vault token revoke-self \
    -tls-skip-verify \
    >/dev/null 2>&1 || true

unset VAULT_TOKEN

log_ok "Vault AppRole logged out."