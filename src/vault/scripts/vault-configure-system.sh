#!/bin/sh

set -eu

. ${VAULT_LIB_SH_PATH}

#########################################
# Vault System Configuration
#########################################

if ! vault_audit_enabled
then
    log_info "Enabling Vault audit logs..."

    vault audit enable \
        file \
        file_path=${VAULT_LOGS_PATH}

    log_ok "Vault audit logs enabled."
fi

if ! vault_secret_enabled
then
    log_info "Enabling Vault secrets..."

    vault secrets enable \
        -path=secret \
        kv-v2

    log_ok "Vault secrets enabled."
fi