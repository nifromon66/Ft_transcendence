#!/bin/sh

set -eu

. ${VAULT_LIB_SH_PATH}

log_info "Vault entrypoint..."

#########################################
# Runtime directories
#########################################

log_info "Creating necessary runtime directories..."

mkdir -p \
    ${VAULT_INIT_DIR} \
    ${VAULT_TLS_DIR} \
    ${VAULT_STORAGE_DATA_DIR} \
    ${VAULT_STORAGE_DATABASE_DIR} \
	${VAULT_LOGS_DIR} \
    ${VAULT_APPROLE_ID_DIR}

mkdir -p \
    ${VAULT_APPROLE_BACKEND_ID_DIR} \
    ${VAULT_APPROLE_ADMIN_ID_DIR}

log_ok "Created necessary runtime directories."

#########################################
# TLS
#########################################

log_info "Vault TLS Certificate generation..."

${VAULT_SH_TLS_CERT_GEN_PATH}

#########################################
# Generate vault.hcl
#########################################

log_info "Generating ${VAULT_SH_HCL_CONFIG_PATH} from ${VAULT_SH_HCL_CONFIG_TEMPLATE_PATH}..."

envsubst '
${VAULT_LISTEN_ADDRESS}
${VAULT_TLS_CERT}
${VAULT_TLS_KEY}
${VAULT_STORAGE_DATA_DIR}
${VAULT_STORAGE_NODE_ID}
${VAULT_API_ADDR}
${VAULT_CLUSTER_ADDR}
${VAULT_LOGGING_LEVEL}' \
    < ${VAULT_SH_HCL_CONFIG_TEMPLATE_PATH} \
    > ${VAULT_SH_HCL_CONFIG_PATH}

log_ok "Generated ${VAULT_SH_HCL_CONFIG_PATH}."

#########################################
# Logs
#########################################

touch "${VAULT_LOGS_PATH}"

#########################################
# Start Vault
#########################################

chown -R vault:vault \
    ${VAULT_INIT_DIR} \
    ${VAULT_TLS_DIR} \
    ${VAULT_STORAGE_DATA_DIR} \
    ${VAULT_STORAGE_DATABASE_DIR} \
	${VAULT_LOGS_DIR} \
    ${VAULT_APPROLE_ID_DIR} \
    ${VAULT_APPROLE_BACKEND_ID_DIR} \
    ${VAULT_APPROLE_ADMIN_ID_DIR}

log_info "Starting Vault..."

vault server -config=/tmp/vault.hcl &

VAULT_PID=$!

${VAULT_SH_BOOTSTRAP_PATH} "$@"

wait "$VAULT_PID"

log_ok "Vault is ready."
