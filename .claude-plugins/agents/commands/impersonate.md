---
description: Run an archastro impersonate CLI command directly
allowed-tools: ["Bash(archastro:*)"]
---

# ArchAstro Agent Impersonation (CLI passthrough)

Pass arguments directly to `archastro impersonate`.

```text
/agents:impersonate start <agent-id>
/agents:impersonate status
/agents:impersonate sync
/agents:impersonate stop
/agents:impersonate list skills
/agents:impersonate install skill <id> [--harness codex] [--install-scope project]
```

## Instructions

1. Read `plugin-compatibility.json`. Prefer `plugins.agents.minimumCliVersion`, fall back to the top-level `minimumCliVersion`.
2. Run `archastro --version`. If missing or too old, tell the user to run `/cli:install`.
3. Run:
   ```
   archastro impersonate $ARGUMENTS
   ```
4. If the command was `start` or `sync`, also run `archastro impersonate status --json`, read the `identity_file`, and adopt the identity for the current session.
5. If the command was `stop`, drop any impersonated identity from the current session.
6. If auth or app selection fails, direct the user to `/cli:auth` or `--app <id>`.
