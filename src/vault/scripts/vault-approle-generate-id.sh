#!/bin/sh

set -eu

. ${VAULT_LIB_SH_PATH}

log_info "Generating AppRoles IDs..."

log_info "Generating AppRoles IDs for Backend..."

#
# Backend RoleID
#

log_info "Generating AppRole Backend RoleID..."

vault read \
    -tls-skip-verify \
    -field=role_id \
    ${VAULT_APPROLE_BACKEND_AUTH_ROLE_ID_PATH} \
    > ${VAULT_APPROLE_BACKEND_ROLE_ID_PATH}

log_ok "Generated AppRole Backend RoleID."

#
# Backend SecretID
#

log_info "Generating AppRole Backend SecretID..."

vault write \
    -tls-skip-verify \
    -f \
    -field=secret_id \
    ${VAULT_APPROLE_BACKEND_AUTH_SECRET_ID_PATH} \
    > ${VAULT_APPROLE_BACKEND_SECRET_ID_PATH}

log_ok "Generated AppRole Backend SecretID."

log_ok "Generated AppRoles IDs for Backend."

log_info "Generating AppRoles IDs for admin."

#
# Admin RoleID
#

log_info "Generating AppRole Admin RoleID..."

vault read \
    -tls-skip-verify \
    -field=role_id \
    ${VAULT_APPROLE_ADMIN_AUTH_ROLE_ID_PATH} \
    > ${VAULT_APPROLE_ADMIN_ROLE_ID_PATH}

log_ok "Generated AppRole Admin RoleID."

#
# Admin SecretID
#

log_info "Generating AppRole Admin SecretID..."

vault write \
    -tls-skip-verify \
    -f \
    -field=secret_id \
    ${VAULT_APPROLE_ADMIN_AUTH_SECRET_ID_PATH} \
    > ${VAULT_APPROLE_ADMIN_SECRET_ID_PATH}

log_ok "Generated AppRole Admin SecretID."

log_ok "Generated AppRoles IDs for Admin."

log_ok "Generated AppRoles IDs."