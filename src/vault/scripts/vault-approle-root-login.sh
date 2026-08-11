#!/bin/sh

set -eu

. ${VAULT_LIB_SH_PATH}

#########################################
# Vault Root Login
#########################################

log_info "Login in the Vault as root..."

ROOT_TOKEN="$(jq -r '.root_token' ${VAULT_INIT_PATH})"

export VAULT_TOKEN="$ROOT_TOKEN"

log_ok "Logged in the Vault as root."