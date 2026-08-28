#!/bin/sh

set -eu

. ${VAULT_LIB_SH_PATH}

log_info "Vault token revocation..."

vault token revoke-self \
    >/dev/null 2>&1 || true

unset VAULT_TOKEN

log_ok "Vault token revoked."