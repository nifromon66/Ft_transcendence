#!/bin/sh

##########################################
# WAF entrypoint		                 #
##########################################

set -e

echo "[*] waf entrypoint executing..."

##########################################
# SSL Certificates generation            #
##########################################

/usr/local/src/waf/scripts/ssl-certification-gen.sh

##########################################
# *.conf.template => *.conf              #
##########################################

echo "[*] Converting templates to configs..."

echo "[*] Converting nginx.conf.template to nginx.conf..."

envsubst '
${NGINX_MODSEC_MODULE_FILE_PATH}
${NGINX_ERROR_LOG_PATH}
${NGINX_CLIENT_MAX_BODY_SIZE}
${NGINX_ACCESS_LOG_PATH}
${NGINX_MODSEC_RULES_FILE_PATH}
${NGINX_CONF_INCLUDE_PATH}' \
	< /usr/local/src/waf/nginx/nginx.conf.template \
	> /usr/local/src/waf/nginx/nginx.conf

echo "[✔] nginx.conf.template converted to nginx.conf successfully."

echo "[*] Converting nginx.conf.template to nginx.conf..."

envsubst '
${SERVER_NAME}
${SERVER_REDIRECT_PORT}
${SERVER_REVERSE_PROXY_PORT}
${SSL_CERT}
${SSL_KEY}
${BACKEND_HOST}
${BACKEND_PORT}
${FRONTEND_HOST}
${FRONTEND_PORT}' \
	< /usr/local/src/waf/nginx/conf.d/reverse-proxy.conf.template \
	> /usr/local/src/waf/nginx/conf.d/reverse-proxy.conf

echo "[✔] reverse-proxy.conf.template converted to reverse-proxy.conf successfully."

echo "[*] Converting modsecurity.conf.template to modsecurity.conf..."

envsubst '
${MODSEC_RULE_ENGINE}
${MODSEC_AUDIT_ENGINE}
${MODSEC_AUDIT_LOG}
${MODSEC_AUDIT_LOG_FORMAT}
${MODSEC_DEBUG_LOG}
${MODSEC_DEBUG_LOG_LEVEL}
${MODSEC_CUSTOM_RULES_INCLUDE_PATH}' \
	< /usr/local/src/waf/modsecurity/modsecurity.conf.template \
	> /usr/local/src/waf/modsecurity/modsecurity.conf

echo "[✔] modsecurity.conf.template converted to modsecurity.conf successfully."

echo "[✔] Converted templates to configs successfully."

##########################################
# Copying all necessary config files     #
##########################################

mkdir -p /etc/nginx/modsecurity
mkdir -p /var/log/nginx
mkdir -p /var/log/modsecurity

mkdir -p /etc/nginx/modsecurity/custom

echo "[*] Copying all necessary config files..."

cp /usr/local/src/waf/nginx/nginx.conf \
   /etc/nginx/nginx.conf

echo "[✔] Copied nginx.conf file."

cp -r /usr/local/src/waf/nginx/conf.d/* \
      /etc/nginx/conf.d/

echo "[✔] Copied all nginx conf.d/* files."

cp /usr/local/src/waf/modsecurity/modsecurity.conf \
      /etc/nginx/modsecurity/

echo "[✔] Copied modsecurity.conf file."

cp /usr/local/src/waf/modsecurity/unicode.mapping \
	/etc/nginx/modsecurity/

echo "[✔] Copied unicode.mapping file."

cp /usr/local/src/waf/modsecurity/crs-setup.conf \
	/etc/nginx/modsecurity/

echo "[✔] Copied crs-setup.conf file."

cp /usr/local/src/waf/modsecurity/REQUEST-900-EXCLUSION-RULES-BEFORE-CRS.conf \
	/etc/nginx/modsecurity/

echo "[✔] Copied REQUEST-900-EXCLUSION-RULES-BEFORE-CRS.conf file."

cp /usr/local/src/waf/modsecurity/RESPONSE-999-EXCLUSION-RULES-AFTER-CRS.conf \
	/etc/nginx/modsecurity/

echo "[✔] Copied RESPONSE-999-EXCLUSION-RULES-AFTER-CRS.conf file."


cp -r /usr/local/src/waf/modsecurity/custom/* \
	/etc/nginx/modsecurity/custom/

echo "[✔] Copied all modsecurity /custom/*.conf files."

echo "[✔] Copied all necessary config files."

##########################################
# Launching Nginx                        #
##########################################

echo "[*] Putting nginx daemon off ..."

exec nginx -g "daemon off; error_log stderr debug;"

echo "[✔] nginx daemon off."

echo "[✔] waf entrypoint successful."