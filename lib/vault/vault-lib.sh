#!/bin/sh

. /usr/local/src/vault/scripts/lib/logs.sh

vault_status() {
    vault status -tls-skip-verify >/dev/null 2>&1
    return $?
}

vault_is_reachable() {
    vault_status
    STATUS=$?

    [ "$STATUS" -eq 0 ] || [ "$STATUS" -eq 2 ]
}

vault_is_initialized() {
    STATUS="$(vault status -tls-skip-verify 2>/dev/null || true)"

    if echo "$STATUS" | grep -q "Initialized.*true"; then
        log_ok "Vault already initialized. Skipping Initialization..."
        return 0
    fi
    log_info "Vault not initialized. Proceeding with Initialization..."
    return 1
}

vault_is_sealed() {
    STATUS="$(vault status -tls-skip-verify 2>/dev/null || true)"

    if echo "$STATUS" | grep -q "Sealed.*true"; then
        log_ok "Vault still sealed. Proceeding with Unsealing..."
        return 0
    fi
    log_info "Vault already unsealed. Skipping Unsealing..."
    return 1
}

vault_secret_enabled() {
    SECRETS="$(vault secrets list -tls-skip-verify 2>/dev/null || true)"

    if echo "$SECRETS" | grep -q "^secret/"; then
        return 0
    fi
    return 1
}

vault_audit_enabled() {
    AUDITS="$(vault audit list -tls-skip-verify 2>/dev/null || true)"

    if echo "$AUDITS" | grep -q "^file/"; then
        return 0
    fi
    return 1
}

vault_policy_written() {
    POLICIES="$(vault policy list -tls-skip-verify 2>/dev/null || true)"

    if echo "$POLICIES" | grep -q "^backend" && echo "$POLICIES" | grep -q "^admin"; then
        return 0
    fi
    return 1
}

vault_approle_written() {
    if vault read \
        -tls-skip-verify \
        ${VAULT_APPROLE_BACKEND_AUTH_PATH} >/dev/null 2>&1 && 
        vault read \
        -tls-skip-verify \
        ${VAULT_APPROLE_ADMIN_AUTH_PATH} >/dev/null 2>&1
    then
        return 0
    fi
    return 1
}

vault_approle_ids_exist()
{
    [ -f "$VAULT_APPROLE_ADMIN_ROLE_ID_PATH" ] &&
    [ -f "$VAULT_APPROLE_ADMIN_SECRET_ID_PATH" ] &&
    [ -f "$VAULT_APPROLE_BACKEND_ROLE_ID_PATH" ] &&
    [ -f "$VAULT_APPROLE_BACKEND_SECRET_ID_PATH" ]
}

vault_approle_valid() {
    ROLE_ID_FILE="$1"
    SECRET_ID_FILE="$2"

    [ -s "$ROLE_ID_FILE" ] || return 1
    [ -s "$SECRET_ID_FILE" ] || return 1

    ROLE_ID="$(cat "$ROLE_ID_FILE")"
    SECRET_ID="$(cat "$SECRET_ID_FILE")"

    vault write         -tls-skip-verify         auth/approle/login         role_id="$ROLE_ID"         secret_id="$SECRET_ID" >/dev/null 2>&1
    return $?
}

vault_approles_valid() {
    vault_approle_valid "$VAULT_APPROLE_ADMIN_ROLE_ID_PATH" "$VAULT_APPROLE_ADMIN_SECRET_ID_PATH" &&     vault_approle_valid "$VAULT_APPROLE_BACKEND_ROLE_ID_PATH" "$VAULT_APPROLE_BACKEND_SECRET_ID_PATH"
}

vault_system_configured() {
    if vault_secret_enabled; then
        log_ok "Vault secrets enabled. Skipping secrets enabling..."
    else
        log_info "Vault secrets not enabled. Proceeding with secrets enabling..."
    fi
    if vault_audit_enabled; then
        log_ok "Vault audits enabled. Skipping audits enabling..."
    else
        log_info "Vault audits not enabled. Proceeding with audits enabling..."
    fi
    if vault_secret_enabled && vault_audit_enabled; then
        log_ok "Vault System Configured. Skipping Vault System Configuration..."
        return 0
    fi
    log_info "Vault System not configured. Proceeding with Vault System Configuration..."
    return 1
}

vault_security_configured() {
    if vault_policy_written; then
        log_ok "Vault Policies written. Skipping writing policies..."
    else
        log_info "Vault Policies not written. Proceeding with writing policies..."
    fi
    if vault_approle_written; then
        log_ok "Vault AppRoles written. Skipping writing AppRoles..."
    else
        log_ok "Vault AppRoles not written. Proceeding with writing AppRoles..."
    fi
    if vault_approle_ids_exist; then
        log_ok "Vault AppRoles IDs exist. Skipping creating AppRoles IDs..."
    else
        log_ok "Vault AppRoles IDs don't exist. Proceeding with creating AppRoles IDs..."
    fi
    if vault_policy_written && vault_approle_written && vault_approle_ids_exist; then
        log_ok "Vault Security Configured. Skipping Vault Security Configuration..."
        return 0
    fi
    log_info "Vault Security not configured. Proceeding with Vault Security Configuration..."
    return 1
}

vault_get_role_id() {
    cat "$1"
}

vault_get_secret_id() {
    cat "$1"
}

vault_with_root() {
    source ${VAULT_SH_APPROLE_ROOT_LOGIN_PATH}

    "$@"

    source ${VAULT_SH_APPROLE_LOGOUT_PATH}
}

vault_with_admin() {
    source ${VAULT_SH_APPROLE_LOGIN_PATH} admin

    "$@"

    source ${VAULT_SH_APPROLE_LOGOUT_PATH}
}