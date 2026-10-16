#!/bin/sh
set -eu

model="${RECIPE_AI_MODEL:-qwen3:4b}"
server_pid=""
pull_pid=""

cleanup() {
    if [ -n "$pull_pid" ]; then
        kill "$pull_pid" 2>/dev/null || true
        wait "$pull_pid" 2>/dev/null || true
    fi
    if [ -n "$server_pid" ]; then
        kill "$server_pid" 2>/dev/null || true
        wait "$server_pid" 2>/dev/null || true
    fi
}

trap cleanup EXIT
trap 'exit 0' TERM INT

ollama serve &
server_pid=$!

attempt=0
until ollama list >/dev/null 2>&1; do
    if ! kill -0 "$server_pid" 2>/dev/null || [ "$attempt" -ge 60 ]; then
        echo "Ollama failed to start." >&2
        exit 1
    fi
    attempt=$((attempt + 1))
    sleep 1 &
    wait $!
done

if ! ollama show "$model" >/dev/null 2>&1; then
    echo "Downloading model: $model"
    ollama pull "$model" &
    pull_pid=$!
    wait "$pull_pid"
    pull_pid=""
fi

echo "Warming up model: $model..."
ollama run "$model" "" >/dev/null 2>&1 || true

echo "Model ready: $model"
wait "$server_pid"
