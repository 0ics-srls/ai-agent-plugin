#!/bin/bash
# valid fixture — compliant twins of each rule
OUT=$(ls -la)
rm -rf "${TARGET_DIR:?}"
curl -fsSL https://example.com/install.sh -o install.sh
bash install.sh
