#!/bin/sh

set -eu

. ${VAULT_LIB_SH_PATH}

if [ "${VAULT_AUTO_UNSEAL}" != "true" ]
then
    log_warn "Automatic Vault unsealing is disabled."
    log_warn "Vault will remain sealed."
    exit 0
fi

log_info "Unsealing Vault with ${VAULT_UNSEAL_KEY_THRESHOLD} unseal keys..."

for INDEX in $(seq 0 $((${VAULT_UNSEAL_KEY_THRESHOLD} - 1)))
do
    UNSEAL_KEY="$(
        jq -er \
            --argjson index $INDEX \
            '.unseal_keys_b64[$index]' \
            ${VAULT_INIT_PATH}
    )"

    vault operator unseal $UNSEAL_KEY >/dev/null

    unset UNSEAL_KEY

    log_ok "Unseal key $(($INDEX + 1))/${VAULT_UNSEAL_KEY_THRESHOLD}/${VAULT_UNSEAL_KEY_COUNT} accepted."
done

if vault_is_sealed
then
    log_error "Vault is still sealed after unseal procedure."
    exit 1
fi

log_ok "Vault unsealed."