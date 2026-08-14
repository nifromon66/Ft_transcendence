#!/bin/sh

. ../common.sh

curl -sk \
-H "User-Agent: sqlmap" \
-v \
"$HOST"