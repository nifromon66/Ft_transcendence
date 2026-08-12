#!/bin/sh

set -eu

. ${VAULT_LIB_SH_PATH}

log_info "Vault Secrets Insertion..."

vault_with_admin ${VAULT_SH_SECRETS_DATABASE_PATH}
vault_with_admin ${VAULT_SH_SECRETS_FLASK_PATH}
vault_with_admin ${VAULT_SH_SECRETS_JWT_PATH}
vault_with_admin ${VAULT_SH_SECRETS_OAUTH_PATH}
vault_with_admin ${VAULT_SH_SECRETS_SMTP_PATH}

log_ok "Vault Secrets inserted."