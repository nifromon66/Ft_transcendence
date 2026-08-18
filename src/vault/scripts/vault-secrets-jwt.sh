#!/bin/sh

set -eu

. ${VAULT_LIB_SH_PATH}

log_info "Writing JWT secret..."

vault kv put \
    -tls-skip-verify \
    secret/jwt \
    secret_key="${JWT_SECRET_KEY}" \
    expiration="${JWT_EXPIRATION}"

log_ok "JWT secret written."