#!/bin/sh

. ../common.sh

for METHOD in TRACE TRACK
do

STATUS=$(curl -sk \
-X "$METHOD" \
-o /dev/null \
-w "%{http_code}" \
"$HOST")

echo "$METHOD -> $STATUS"

done