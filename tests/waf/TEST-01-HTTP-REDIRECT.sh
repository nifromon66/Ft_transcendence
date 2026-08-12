#!/bin/sh

. ../common.sh

STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost)

if [ "$STATUS" = "301" ] || [ "$STATUS" = "308" ]; then
    pass "HTTP redirects to HTTPS"
else
    fail "Expected redirect, got $STATUS"
fi