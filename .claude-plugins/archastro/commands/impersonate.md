---
description: Run an archastro embed CLI command directly
allowed-tools: ["Bash(archastro:*)"]
---

# ArchAstro Agent Impersonation (CLI passthrough)

Pass arguments directly to `archastro embed`.

```text
/archastro:impersonate start <agent-id>
/archastro:impersonate status
/archastro:impersonate sync
/archastro:impersonate stop
/archastro:impersonate list skills
/archastro:impersonate install skill <id> [--harness codex] [--install-scope project]
```

## Instructions

1. Read `plugin-compatibility.json`. Prefer `plugins.archastro.minimumCliVersion`, fall back to the top-level `minimumCliVersion`.
2. Run `archastro --version`. If missing or too old, tell the user to run `/archastro:install`.
3. Run:
   ```
   archastro embed $ARGUMENTS
   ```
4. If the command was `start` or `sync`, also run `archastro embed status --json`, read the `identity_file`, and adopt the identity for the current session.
5. If the command was `stop`, drop any impersonated identity from the current session.
6. If auth or app selection fails, direct the user to `/archastro:auth` or `--app <id>`.
