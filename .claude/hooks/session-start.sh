#!/bin/bash
# Installs OmniRoute (needs Node >= 22.22.2 / 24) and starts it so the
# "omniroute" MCP server from .mcp.json works in Claude Code cloud sessions.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

NODE_VERSION="24.14.1"
OMNIROUTE_VERSION="3.8.51"
export NVM_DIR="${NVM_DIR:-/opt/nvm}"
NODE_BIN="$NVM_DIR/versions/node/v$NODE_VERSION/bin"

if [ ! -x "$NODE_BIN/node" ]; then
  # shellcheck disable=SC1091
  . "$NVM_DIR/nvm.sh"
  nvm install "$NODE_VERSION" >&2
fi
export PATH="$NODE_BIN:$PATH"

if [ "$(omniroute --version 2>/dev/null | grep -o '[0-9.]*$' || true)" != "$OMNIROUTE_VERSION" ]; then
  npm install -g "omniroute@$OMNIROUTE_VERSION" >&2
fi

# Only reachable from inside the container.
export OMNIROUTE_SERVER_HOST=127.0.0.1
if ! curl -s -o /dev/null --max-time 5 http://127.0.0.1:20128/; then
  omniroute serve --daemon --no-open --no-tray >&2
fi
