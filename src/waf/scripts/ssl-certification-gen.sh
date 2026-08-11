#!/bin/sh

set -e

echo "[*] SSL Certificate generation..."

# Check if both files exist
if [ -f "${SSL_CERT}" ] && [ -f "${SSL_KEY}" ]; then
  echo "[*] SSL Certificate and key already exist. Checking validity..."

  # Check if cert is still valid (expiry at least 1 day from now)
  if openssl x509 -checkend "${SSL_EXPIRY_DIFF}" -noout -in "$SSL_CERT" > /dev/null; then
    echo "[✔] SSL Certificate is still valid. Aborting generation."
    exit 0
  else
    echo "[!] SSL Certificate has expired or will expire within 24h. Continuing generation..."
  fi
else
  echo "[!] SSL Certificate or key missing. Continuing generation..."
fi

# Generate new self-signed certificate
openssl req \
	-x509 \
	-nodes \
	-days "${SSL_VALIDITY_PERIOD}" \
	-newkey "${SSL_KEY_TYPE}":"${SSL_KEY_SIZE}" \
	-keyout "${SSL_KEY}" \
	-out "${SSL_CERT}" \
	-subj "${SSL_COMMON_NAME}"

chmod 600 \
	"${SSL_CERT}" \
	"${SSL_KEY}"

echo "[✔] SSL Certificate generated successfully."