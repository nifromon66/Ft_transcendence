#!/bin/sh

. ../common.sh

seq 1 100 | while read i
do
    curl -sk "$HOST" &
done

wait