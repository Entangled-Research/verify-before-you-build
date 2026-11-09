#!/bin/sh
set -eu
TASK_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
MINDCRAFT_DIR=${MINDCRAFT_HOME:-"$TASK_DIR/../../minecraft-demo"}
NODE_BIN="$MINDCRAFT_DIR/.local/node22/bin/node"
if [ ! -x "$NODE_BIN" ]; then NODE_BIN=node; fi
exec "$NODE_BIN" "$TASK_DIR/cli.mjs" "$@" --mindcraft "$MINDCRAFT_DIR"
