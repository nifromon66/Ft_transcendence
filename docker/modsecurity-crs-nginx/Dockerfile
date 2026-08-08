FROM owasp/modsecurity-crs:nginx-alpine

USER root

RUN apk add --no-cache bash gettext openssl

COPY src/modsecurity-crs-nginx /usr/local/src/modsecurity

RUN chmod +x \
    /usr/local/src/modsecurity/scripts/entrypoint.sh \
    /usr/local/src/modsecurity/scripts/ssl-certification-gen.sh

ENTRYPOINT [ "/usr/local/src/modsecurity/scripts/entrypoint.sh" ]