FROM hashicorp/vault:1.19

USER root

RUN apk add --no-cache \
    bash \
    gettext \
    curl \
    jq \
    openssl

COPY src/vault/scripts /usr/local/src/vault/scripts
COPY src/vault/config /usr/local/src/vault/config
COPY src/vault/policies /usr/local/src/vault/policies
COPY src/vault/roles /usr/local/src/vault/roles
COPY lib/logs.sh /usr/local/src/vault/scripts/lib/logs.sh
COPY lib/vault /usr/local/src/vault/scripts/lib/vault

RUN chmod +x /usr/local/src/vault/scripts/*.sh

ENTRYPOINT [ "/usr/local/src/vault/scripts/entrypoint.sh" ]