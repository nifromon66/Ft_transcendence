#!/bin/sh

. ../common.sh

dd if=/dev/zero bs=1M count=30 > body.bin

curl -sk \
-F "file=@body.bin" \
"$HOST"

rm body.bin