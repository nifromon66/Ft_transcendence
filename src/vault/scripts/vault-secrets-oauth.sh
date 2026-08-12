#!/bin/sh

set -eu

. ${VAULT_LIB_SH_PATH}

log_info "Writing OAuth secrets..."

vault kv put \
    -tls-skip-verify \
    secret/oauth \
    client_id="${OAUTH42_CLIENT_ID}" \
    client_secret="${OAUTH42_CLIENT_SECRET}"

log_ok "OAuth secrets written."