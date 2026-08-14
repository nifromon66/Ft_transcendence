#!/bin/sh

. ../common.sh

STATUS=$(curl -sk \
-o /dev/null \
-w "%{http_code}" \
--data-urlencode "q=<script>alert(1)</script>" \
"$HOST")

if [ "$STATUS" = "403" ]; then
    pass "XSS blocked"
else
    fail "XSS returned $STATUS"
fi