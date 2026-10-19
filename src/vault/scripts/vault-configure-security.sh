#!/bin/sh

set -eu

. ${VAULT_LIB_SH_PATH}

#########################################
# Vault Security Configuration
#########################################

if ! vault_policy_written
then
    log_info "Writing Vault backend policies..."

    vault policy write \
        -tls-skip-verify \
        backend \
        ${VAULT_POLICY_BACKEND_PATH}

    log_ok "Vault backend policies written."
    log_info "Writing Vault admin policies..."

    vault policy write \
        -tls-skip-verify \
        admin \
        ${VAULT_POLICY_ADMIN_PATH}

    log_ok "Vault admin policies written."
fi

if ! vault_approle_written
then

    log_info "Enabling Vault approles..."

    vault auth enable \
        -tls-skip-verify \
        approle

    log_ok "Vault approles enabled."

    log_info "Writing Vault backend role..."

    vault write \
        -tls-skip-verify \
        ${VAULT_APPROLE_BACKEND_AUTH_PATH} \
        @${VAULT_ROLE_BACKEND_PATH}

    log_ok "Vault admin role written."

    vault write \
        -tls-skip-verify \
        ${VAULT_APPROLE_ADMIN_AUTH_PATH} \
        @${VAULT_ROLE_ADMIN_PATH}

    log_ok "Vault admin role written."
fi

if ! vault_approles_valid
then
    ${VAULT_SH_APPROLE_GENERATE_PATH}
fi