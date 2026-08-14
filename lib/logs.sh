#!/bin/sh

log_info() {
    printf '[*] %s\n' "$*"
}

log_ok() {
    printf '[✔] %s\n' "$*"
}

log_warn() {
    printf '[!] %s\n' "$*"
}

log_error() {
    printf '[✘] %s\n' "$*" >&2
}