#!/bin/sh

set -eu

. ${VAULT_LIB_SH_PATH}

log_info "Waiting for Vault..."

while ! vault_is_reachable
do
    sleep 1
done

log_ok "Vault is reachable."

log_info "Vault Initialization..."

if ! vault_is_initialized
then
    ${VAULT_SH_INIT_PATH}
    log_ok "Vault Initialized."
else
    log_ok "Vault Already Initialized."
fi

log_info "Unsealing Vault..."

if vault_is_sealed
then
    ${VAULT_SH_UNSEAL_PATH}
    log_ok "Vault Unsealed."
else
    log_ok "Vault Already Unsealed."
fi

log_info "Waiting for Vault to become active leader..."

while ! vault status 2>/dev/null | grep -E "HA Mode[[:space:]]+active" > /dev/null
do
    sleep 1
done

log_ok "Vault is active leader."

log_info "Configuring Vault..."

vault_with_root "${VAULT_SH_CONFIGURE_PATH}"

