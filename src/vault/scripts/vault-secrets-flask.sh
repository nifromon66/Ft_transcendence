#!/bin/sh

set -eu

. ${VAULT_LIB_SH_PATH}

log_info "Writing Flask secret..."

vault kv put \
    secret/flask \
    secret_key="${FLASK_SECRET_KEY}"

log_ok "Flask secret written."