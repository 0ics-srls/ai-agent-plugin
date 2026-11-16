# PowerShell (ps1) — native-only lint

PowerShell has **no ast-grep grammar**, so it is native-only — the same policy as `dart` and
`perl`. There is no ast-grep rule layer for `.ps1`; the only lint is PSScriptAnalyzer, driven by
`native/PSScriptAnalyzerSettings.psd1`.

## How to lint (Windows)

```powershell
Invoke-ScriptAnalyzer -Path . -Recurse -Settings ${CLAUDE_PLUGIN_ROOT}/lint-rules/shell/native/PSScriptAnalyzerSettings.psd1
```

## Gate policy

- **Linux CI does not gate `.ps1`** — PSScriptAnalyzer is a PowerShell module and the repo
  harness runs on Linux, so ps1 findings are advisory only there.
- Bash (`.sh`) IS gated: ast-grep rules (this pack) + shellcheck (`native/.shellcheckrc`).
