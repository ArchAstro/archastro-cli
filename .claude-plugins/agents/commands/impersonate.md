---
description: Start, inspect, refresh, or stop ArchAstro agent impersonation through the ArchAstro CLI
allowed-tools: ["Bash(archastro:*)"]
---

# ArchAstro Agent Impersonation

Manage ArchAstro agent impersonation from Claude Code.

Command forms:

```text
/agents:impersonate start <agent-id-or-flags>
/agents:impersonate status
/agents:impersonate sync
/agents:impersonate stop
```

## Instructions

1. **Read the compatibility contract first**:
   - Use `plugin-compatibility.json`.
   - For this command, prefer `plugins.agents.minimumCliVersion` and fall back to the top-level `minimumCliVersion`.
   - Treat that resolved value as the minimum supported CLI version for every check below.

2. **Check the installed CLI version first**:
   ```
   archastro --version
   ```
   If the command is missing, or the version is older than the resolved minimum version, tell the user to run `/cli:install`.

3. **Interpret the first argument** from `$ARGUMENTS` as the action. Supported actions are:
   - `start`
   - `status`
   - `sync`
   - `stop`

4. **Dispatch to the matching CLI command**:
   - `start`:
     ```
     archastro impersonate start <remaining-arguments>
     ```
     Then:
     ```
     archastro impersonate status --json
     ```
     Read the returned `identity_file`, adopt that identity for the current Claude Code session, and report the active agent, app, state file, and identity file.
   - `status`:
     ```
     archastro impersonate status --json
     ```
     Summarize whether impersonation is active. If active, report the agent name and ID, app ID, scope, tool count, skill count, state file path, identity file path, and timestamps.
   - `sync`:
     ```
     archastro impersonate sync <remaining-arguments>
     ```
     Then:
     ```
     archastro impersonate status --json
     ```
     Re-read the `identity_file`, re-adopt the refreshed identity, and summarize visible changes.
   - `stop`:
     ```
     archastro impersonate stop <remaining-arguments>
     ```
     Confirm that local impersonation state was removed and drop any impersonated identity from the current session.

5. **If the action is missing or unsupported**, explain the supported forms and show the command syntax.

6. **If authentication or app selection fails**, tell the user to run `/cli:auth` or provide `--app <id>`.
