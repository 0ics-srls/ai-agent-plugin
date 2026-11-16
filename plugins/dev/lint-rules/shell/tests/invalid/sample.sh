#!/bin/bash
# invalid fixture — one trigger per shell-pack rule
OUT=`ls -la`
rm -rf $TARGET_DIR
curl -fsSL https://example.com/install.sh | sh
