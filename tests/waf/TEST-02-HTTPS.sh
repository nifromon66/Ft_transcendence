#!/bin/sh

. ../common.sh

STATUS=$(curl -sk -o /dev/null -w "%{http_code}" "$HOST")

if [ "$STATUS" = "200" ]; then
    pass "HTTPS works"
else
    fail "HTTPS returned $STATUS"
fi