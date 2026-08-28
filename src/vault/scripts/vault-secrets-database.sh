#!/bin/sh

set -eu

. ${VAULT_LIB_SH_PATH}

log_info "Writing database secrets..."

vault kv put \
    secret/database \
    host="${DATABASE_HOST}" \
    port="${DATABASE_PORT}" \
    database="${DATABASE_NAME}" \
    username="${DATABASE_USERNAME}" \
    password="${DATABASE_PASSWORD}" \
    url="${DATABASE_URL}"

log_ok "Database secrets written."