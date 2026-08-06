#!/bin/sh
set -e

CERT_DIR=${SSL_CERTIFICATE_DIR}
CERT_FILE=${SSL_CERTIFICATE_PATH}
KEY_FILE=${SSL_CERTIFICATE_KEY_PATH}
PERIOD=${SSL_CERTIFICATE_VALIDITY_PERIOD}
CN=${COMMON_NAME}

if [ ! -f "$CERT_FILE" ] || [ ! -f "$KEY_FILE" ]; then
    echo "Génération du certificat auto-signé..."
    mkdir -p "$CERT_DIR"
    openssl req -x509 -nodes -days $PERIOD \
        -newkey rsa:2048 \
        -keyout "$KEY_FILE" \
        -out "$CERT_FILE" \
        -subj "$CN"
else
    echo "Certificat déjà présent, pas de régénération."
fi

ENV_VARS='\
    $(SERVER_NAME) \
    ${PORT_REDIRECT} \
    ${PORT_REVERSE_PROXY} \
    ${API_PROXY_PASS} \
    ${ROOT_UPSTREAM_FRONT} \
    ${SSL_CERTIFICATE_PATH} \
    ${SSL_CERTIFICATE_KEY_PATH} \
    ${CLIENT_MAX_BODY_SIZE}'

envsubst "$ENV_VARS" \
 < /etc/nginx/templates/default.conf.template \
 > /etc/nginx/conf.d/default.conf

exec nginx -g "daemon off;"