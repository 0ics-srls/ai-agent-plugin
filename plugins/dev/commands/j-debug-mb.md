---
allowed-tools: Read(/${CLAUDE_PLUGIN_ROOT}/**)
description: Debug any problem with Protocol D - MBEL compact version (junior workflow). Uses ~70% fewer tokens than /dev:j-debug — prefer this in large context sessions. Same methodology, compressed mindset.
---

# /dev:j-debug-mb (compact variant of /dev:j-debug)

This command is identical to **j-debug** — the ONLY difference is the mindset file: it loads the MBEL-compact `debug-protocol-mb.md` (~70% fewer tokens) instead of the verbose `debug-protocol.md`.

## What to do

1. Read `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/debug-protocol-mb.md` (if not read this session) — NOT the verbose debug-protocol.md
2. Read `${CLAUDE_PLUGIN_ROOT}/commands/j-debug.md` and follow it EXACTLY, reading its `debug-protocol-e2e.md` prerequisite without its `$include` of `debug-protocol.md` (the compact variant you already loaded takes its place)

All steps, rules, and dialogs are defined in j-debug.md — single source of truth.
