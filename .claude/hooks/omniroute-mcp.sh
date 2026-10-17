#!/bin/bash
# Launches OmniRoute's stdio MCP server with the Node runtime installed by session-start.sh.
NODE_BIN="${NVM_DIR:-/opt/nvm}/versions/node/v24.14.1/bin"
export PATH="$NODE_BIN:$PATH"
exec omniroute --mcp
