#!/bin/sh

set -eu

. "${VAULT_LIB_SH_PATH}"

log_info "Generating Vault Certificate Authority..."

if [ -f "${VAULT_TLS_CA_CERT}" ] && [ -f "${VAULT_TLS_CA_KEY}" ]; then
    log_ok "Vault Certificate Authority already exists."
    exit 0
fi

openssl req \
    -x509 \
    -new \
    -nodes \
    -newkey "${VAULT_TLS_CA_KEY_TYPE}:${VAULT_TLS_CA_KEY_SIZE}" \
    -sha256 \
    -days "${VAULT_TLS_CA_CERT_VALIDITY_PERIOD}" \
    -keyout "${VAULT_TLS_CA_KEY}" \
    -out "${VAULT_TLS_CA_CERT}" \
    -subj "/C=${VAULT_TLS_CA_CERT_COUNTRY}/ST=${VAULT_TLS_CA_CERT_STATE}/L=${VAULT_TLS_CA_CERT_CITY}/O=${VAULT_TLS_CA_CERT_ORGANIZATION}/CN=${VAULT_TLS_CA_CERT_COMMON_NAME}"

chmod 600 "${VAULT_TLS_CA_KEY}"
chmod 644 "${VAULT_TLS_CA_CERT}"

log_ok "Vault Certificate Authority generated."