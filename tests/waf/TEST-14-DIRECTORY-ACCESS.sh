#!/bin/sh

. ../common.sh

curl -sk \
"$HOST/.git/config"

curl -sk \
"$HOST/.env"