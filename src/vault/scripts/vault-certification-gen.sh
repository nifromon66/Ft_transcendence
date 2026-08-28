#!/bin/sh

set -eu

. "${VAULT_LIB_SH_PATH}"

log_info "Generating Vault ${VAULT_NODE_NAME} server certificate..."

mkdir -p "${VAULT_TLS_SERVER_DIR}"

if [ -f "${VAULT_TLS_SERVER_CERT}" ] && [ -f "${VAULT_TLS_SERVER_KEY}" ]; then
    log_info "Vault ${VAULT_NODE_NAME} server certificate already exists."

    if openssl x509 \
        -checkend "${VAULT_TLS_SERVER_CERT_EXPIRY_DIFF}" \
        -noout \
        -in "${VAULT_TLS_SERVER_CERT}"
    then
        log_ok "Vault ${VAULT_NODE_NAME} server certificate still valid."
        exit 0
    fi

    log_warn "Vault ${VAULT_NODE_NAME} server certificate is expired or near expiry."

    rm -f \
        "${VAULT_TLS_SERVER_CERT}" \
        "${VAULT_TLS_SERVER_KEY}" \
        "${VAULT_TLS_SERVER_CSR}"
fi

openssl genrsa \
    -out "${VAULT_TLS_SERVER_KEY}" \
    "${VAULT_TLS_SERVER_KEY_SIZE}"

chmod 600 "${VAULT_TLS_SERVER_KEY}"

openssl req \
    -new \
    -key "${VAULT_TLS_SERVER_KEY}" \
    -out "${VAULT_TLS_SERVER_CSR}" \
    -subj "/C=${VAULT_TLS_SERVER_CERT_COUNTRY}/ST=${VAULT_TLS_SERVER_CERT_STATE}/L=${VAULT_TLS_SERVER_CERT_CITY}/O=${VAULT_TLS_SERVER_CERT_ORGANIZATION}/CN=${VAULT_NODE_NAME}"

openssl x509 \
    -req \
    -in "${VAULT_TLS_SERVER_CSR}" \
    -CA "${VAULT_TLS_CA_CERT}" \
    -CAkey "${VAULT_TLS_CA_KEY}" \
    -CAcreateserial \
    -out "${VAULT_TLS_SERVER_CERT}" \
    -days "${VAULT_TLS_SERVER_CERT_VALIDITY_PERIOD}" \
    -sha256 \
    -extfile "${VAULT_TLS_SERVER_EXT}"

chmod 644 "${VAULT_TLS_SERVER_CERT}"

rm -f \
    "${VAULT_TLS_SERVER_CSR}" \
    "${VAULT_TLS_CA_CERT}.srl"

log_ok "Vault ${VAULT_NODE_NAME} server certificate generated."