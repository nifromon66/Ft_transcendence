#!/bin/sh

set -eu

. ${VAULT_LIB_SH_PATH}

if [ -f "${VAULT_TLS_CERT}" ] && [ -f "${VAULT_TLS_KEY}" ]; then

    log_info "Certificate already exists."

    if openssl x509 \
        -checkend "${VAULT_TLS_CERT_EXPIRY_DIFF}" \
        -noout \
        -in "${VAULT_TLS_CERT}"
    then
        log_ok "Certificate still valid."
        exit 0
    fi

    log_warn "Certificate expired."

    rm -f \
        "${VAULT_TLS_CERT}" \
        "${VAULT_TLS_KEY}"
fi

openssl req \
    -x509 \
    -newkey "${VAULT_TLS_KEY_TYPE}:${VAULT_TLS_KEY_SIZE}" \
    -nodes \
    -days "${VAULT_TLS_CERT_VALIDITY_PERIOD}" \
    -keyout "${VAULT_TLS_KEY}" \
    -out "${VAULT_TLS_CERT}" \
    -subj "/C=${VAULT_TLS_CERT_COUNTRY}/ST=${VAULT_TLS_CERT_STATE}/L=${VAULT_TLS_CERT_CITY}/O=${VAULT_TLS_CERT_ORGANIZATION}/CN=${VAULT_TLS_CERT_COMMON_NAME}"

chmod 600 "${VAULT_TLS_KEY}"
chmod 644 "${VAULT_TLS_CERT}"

log_ok "[✔] Vault certificate generated."