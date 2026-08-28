#!/bin/sh

set -eu
umask 077

. ${VAULT_LIB_SH_PATH}

log_info "Initializing Vault..."

vault operator init \
    -key-shares=${VAULT_UNSEAL_KEY_COUNT} \
    -key-threshold=${VAULT_UNSEAL_KEY_THRESHOLD} \
    -format=json \
    > ${VAULT_INIT_PATH}

chmod 600 ${VAULT_INIT_PATH}

log_ok "Vault initialized."