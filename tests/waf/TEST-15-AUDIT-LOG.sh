#!/bin/sh

. ../common.sh

docker exec waf \
tail -50 /var/log/modsecurity/audit.log