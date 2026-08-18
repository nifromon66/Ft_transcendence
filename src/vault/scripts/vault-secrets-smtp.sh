#!/bin/sh

set -eu

. ${VAULT_LIB_SH_PATH}

log_info "Writing SMTP secrets..."

vault kv put \
    -tls-skip-verify \
    secret/smtp \
    host="${SMTP_HOST}" \
    port="${SMTP_PORT}" \
    username="${SMTP_USERNAME}" \
    password="${SMTP_PASSWORD}"

log_ok "SMTP secrets written."