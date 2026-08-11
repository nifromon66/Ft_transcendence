#!/bin/sh

HOST="${HOST:-https://localhost}"

GREEN="\033[32m"
RED="\033[31m"
YELLOW="\033[33m"
RESET="\033[0m"

pass() {
    printf "${GREEN}[PASS]${RESET} %s\n" "$1"
}

fail() {
    printf "${RED}[FAIL]${RESET} %s\n" "$1"
}