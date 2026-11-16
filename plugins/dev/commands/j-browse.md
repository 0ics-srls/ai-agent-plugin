---
allowed-tools: Read(/${CLAUDE_PLUGIN_ROOT}/**)
description: INTERACTIVE browsing - user guides, the agent clicks. Browse and interact with any web page via ChromeDevTools MCP, token-efficient (text snapshots; a screenshot only when text is not enough, read by an agent). Use when user says browse, naviga, open page, apri questa pagina, click on, fill the form, or to reproduce a bug in the UI. To run the project's end-to-end checklist use /dev:j-e2e instead.
---

# Browser Navigation — Token-Efficient

Interactive browsing of any web page. The user guides what to do, you execute via ChromeDevTools.

## Prerequisites
- The ChromeDevTools MCP server answers (`mcp__chrome-devtools__*` tools). When it does not: run
  `/dev:j-mcp-setup` and choose chrome-devtools, then come back. STOP.

## Arguments

`$ARGUMENTS` may contain a URL. If provided, navigate there. If empty, ask the user.

## Core Principle: TEXT FIRST

- **Always** use `take_snapshot` to understand a page — gives UIDs, element types, text
- **Never** take a screenshot just to see what's on the page
- **Visual checks** only when text is insufficient: a screenshot as webp quality 30, read by an agent

## Navigation

```
mcp__chrome-devtools__navigate_page url=<target>
mcp__chrome-devtools__take_snapshot
```

## Interaction

All interaction uses UIDs from the latest snapshot:
- `mcp__chrome-devtools__click` uid=<uid>
- `mcp__chrome-devtools__fill` uid=<uid> value=<text>
- `mcp__chrome-devtools__press_key` key=Enter
- `mcp__chrome-devtools__type_text` text=<text>
- `mcp__chrome-devtools__evaluate_script` for complex JS checks

## Login (when needed)

If the page shows a login form (a provider's or the application's own), the accounts are in `.00-secrets/test-accounts.md`
(the project's secrets, encrypted in git — `principles.md` 5.2): find the section of this application,
fill username and password, sign in, verify the redirect. The file missing, or no account for this
application → ask the user.

Not all sites require login — only handle it if a login page appears.

## Visual Check Pattern

Save the screenshot to a file; an agent reads it and describes it, so the image never enters the main
conversation:
```
mcp__chrome-devtools__take_screenshot filePath=problem-chrome-dt/visual-check.webp format=webp quality=30
```
```
Agent prompt="Read the screenshot at <path> and describe what you see in 5 lines max."
```

## Rules

- **NEVER** read screenshot files with the Read tool in the main conversation (image processing burns the orchestrator's context)
- **CHECK** console messages when something seems wrong: `list_console_messages`
- **REPORT** what you find concisely to the user
- **ASK** the user what to do next — this is interactive browsing, not automated testing
