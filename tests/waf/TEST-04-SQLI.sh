#!/bin/sh

. ../common.sh

STATUS=$(curl -sk -o /dev/null -w "%{http_code}" \
--data-urlencode "id=1' OR '1'='1" \
"$HOST")

if [ "$STATUS" = "403" ]; then
    pass "SQLi blocked"
else
    fail "SQLi returned $STATUS"
fi