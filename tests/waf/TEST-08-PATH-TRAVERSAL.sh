#!/bin/sh

. ../common.sh

STATUS=$(curl -sk \
-o /dev/null \
-w "%{http_code}" \
"$HOST/../../../../etc/passwd")

if [ "$STATUS" = "403" ]; then
    pass "Traversal blocked"
else
    fail "Traversal returned $STATUS"
fi