FROM owasp/modsecurity-crs:nginx-alpine

USER root

RUN apk add --no-cache bash gettext openssl

RUN mkdir -p /var/log/nginx

COPY src/waf /usr/local/src/waf

RUN chmod +x \
    /usr/local/src/waf/scripts/entrypoint.sh \
    /usr/local/src/waf/scripts/ssl-certification-gen.sh

ENTRYPOINT [ "/usr/local/src/waf/scripts/entrypoint.sh" ]