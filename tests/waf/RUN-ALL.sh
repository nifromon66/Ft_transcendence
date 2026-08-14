#!/bin/sh

. ../common.sh

for test in TEST-*.sh
do
    echo
    echo "================================="
    echo "$test"
    echo "================================="
    sh "$test"
done