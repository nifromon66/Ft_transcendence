#!/bin/sh

. ../common.sh

STATUS=$(curl -sk \
-o /dev/null \
-w "%{http_code}" \
"$HOST/?page=../../../../etc/passwd")

if [ "$STATUS" = "403" ]; then
    pass "LFI blocked"
else
    fail "LFI returned $STATUS"
fi