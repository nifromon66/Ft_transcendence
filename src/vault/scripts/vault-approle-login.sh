#!/bin/bash

set -euo pipefail

. ${VAULT_LIB_SH_PATH}

[ $# -eq 1 ] || fatal "usage: vault-approle-login <role>"

ROLE="$1"

log_info "Login into $ROLE AppRole..."

ROLE_ID="$(vault_get_role_id ${VAULT_APPROLE_ID_DIR}/"$ROLE"/role-id)"
SECRET_ID="$(vault_get_secret_id ${VAULT_APPROLE_ID_DIR}/"$ROLE"/secret-id)"

LOGIN_RESPONSE="$(vault write \
    -format=json \
    auth/approle/login \
    role_id="$ROLE_ID" \
    secret_id="$SECRET_ID")"

VAULT_TOKEN="$(printf '%s' "$LOGIN_RESPONSE" | jq -er '.auth.client_token')"

[ -n "$VAULT_TOKEN" ] || fatal "Vault returned an empty client token."

log_ok "Logged into $ROLE AppRole."

log_info "Exporting Vault Token..."

export VAULT_TOKEN

log_ok "Vault Token Exported."