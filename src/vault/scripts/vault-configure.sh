#!/bin/sh

set -eu

. ${VAULT_LIB_SH_PATH}

log_info "Vault System Configuration..."

if ! vault_system_configured
then
    ${VAULT_SH_CONFIGURE_SYSTEM_PATH}
    log_ok "Vault System Configured."
else
    log_ok "Vault System Already Configured."
fi

log_info "Vault Security Configuration..."

if ! vault_security_configured
then
    ${VAULT_SH_CONFIGURE_SECURITY_PATH}
    log_ok "Vault Security Configured."
else
    log_ok "Vault Security Already Configured."
fi
