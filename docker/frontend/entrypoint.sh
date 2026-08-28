#!/bin/sh

if [ ! -d "node_modules" ] || [ -z "$(ls -A node_modules)" ]; then
    npm install --legacy-peer-deps
fi

exec "$@"