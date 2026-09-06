---
targets:
  claude-skill: impersonate
  claude-command: impersonate.md
  codex-skill: impersonate
skill:
  name: impersonate
  description: Use when the user wants to impersonate an ArchAstro agent, asks about the active impersonation state, wants to refresh or stop impersonation, or refers to working as a specific ArchAstro agent inside {{HARNESS_NAME}}. Trigger phrases include "embed agent", "start embed", "sync embed", "stop embed", "which agent is embedded", "impersonate agent", "act as this agent", "be this agent", "start impersonation", "sync impersonation", "stop impersonation", "what agent am I impersonating", and "use the active agent identity".
  allowed-tools: ["Bash(archastro:*)"]
command:
  description: Run an archastro embed CLI command directly
  allowed-tools: ["Bash(archastro:*)"]
---

{{#SKILL}}# ArchAstro Agent Embed

The current CLI command is `archastro embed`; `impersonate` is the legacy skill name and is not a CLI command.

Manage ArchAstro agent embedding through the ArchAstro CLI and keep the {{SESSION}} aligned with the active identity file.

This skill assumes the ArchAstro CLI is already installed and authenticated. {{ASSUME_INSTALLED}}

## Always Start with State

Every invocation must begin by checking the current impersonation state. Do not ask the user what action to take — determine it from state and intent.

```
archastro embed status --json
```

Then route based on the combination of current state and user intent.

## Routing

### CLI not installed or too old

Before any impersonation work, verify the CLI:

- Read `plugin-compatibility.json` from the plugin root. Prefer `plugins.archastro.minimumCliVersion`, fall back to the top-level `minimumCliVersion`.
- Run `archastro --version`. If missing or older than the resolved minimum, {{INSTALL_ROUTE}}.
- If authentication or app selection is missing, {{AUTH_ROUTE}}.

### Inactive + user wants to start

```
archastro embed start <agent-id-or-lookup-key> --harness codex --install-scope project
```

Then:

```
archastro embed status --json
```

Read `state.identity_file` from the returned JSON (`active`, `path`, and `state`). Open and read that file. Adopt the identity for the current {{SESSION}} while retaining your normal capabilities.

`embed start` automatically installs linked skills for detected harnesses by default. Choose the actual current harness and intended scope explicitly (the example above uses Codex/project); supported harnesses are `claude`, `codex`, `cursor`, and `rovo`, with user scope the default. After adoption, inspect `state.skills`, `state.loaded_skills`, and returned warnings to report what installed successfully:

```
archastro embed list skills --json
```

### Active + user asks about status (or no specific intent)

Summarize the current state from the JSON already fetched:

- Agent name and ID
- App ID
- Tool count and skill count
- Loaded (installed) skills and their invocations
- Timestamps

If the identity file has not been read in this session yet, read it and adopt the identity.

### Active + user wants to sync/refresh

```
archastro embed sync
```

Then:

```
archastro embed status --json
```

Re-read `state.identity_file` and re-adopt the refreshed identity. Report what changed (new/removed tools or skills).

### Active + user wants to stop

```
archastro embed stop
```

Drop the impersonated identity from the current session. Confirm that local state was removed.

### Active + user asks about tools

List the impersonated agent's tools:

```
archastro embed list tools --json
```

To execute a tool directly:

```
archastro embed run tool <tool-name> --input '<json>' --json
```

### Active + user asks about skills

List available skills:

```
archastro embed list skills --json
```

Show what's available vs what's already installed (from `state.loaded_skills`).

To install a skill:

```
archastro embed install skill <skill-id-or-slug>
```

After install, report the invocation command (e.g., `/<skill-name>`) so the user knows how to use it.

For Codex:

```
archastro embed install skill <id> --harness codex --install-scope project
```

### Inactive + user asks about status

Report that no impersonation is active and offer to start one.

## Adopting the Identity

When you read the identity file, you must **become that agent** for the rest of the session. This is not cosmetic — it changes how you behave:

- **Personality and tone.** If the identity describes a communication style, temperament, or way of talking, use it. Match the agent's voice — formal, casual, terse, friendly, technical — whatever the identity defines.
- **Background and expertise.** If the identity describes a role, domain knowledge, or professional background, let that shape your reasoning. Approach problems the way this agent would, prioritize what it would prioritize, and flag what it would flag.
- **Scope and boundaries.** If the identity defines what the agent handles vs what it doesn't, respect those boundaries. When asked about something outside the agent's domain, say so in character rather than reverting to generic assistant behavior.
- **Stay in character across turns.** Do not drop the persona between messages. Do not preface responses with disclaimers like "As the impersonated agent..." — just be the agent.
- **Keep your capabilities.** You still have full tool access (file read/write, bash, search, etc.). The identity shapes how and when you use them, not whether you can.

After `stop`, fully drop the persona and return to your normal behavior.

## Limitations

- **Integration tools do not resolve during impersonation.** Tools backed by server-side integrations (GitHub, Slack, Gmail, etc.) require OAuth credentials that cannot be exported locally. Only builtin tools and custom script tools are available.
- For agents that rely primarily on integrations, use agent sessions (`archastro create agentsession --agent <id> --wait`) instead of impersonation.

## Session Integration

- After `start` or `sync`, always read the identity file and adopt it as described above
- After `stop`, always drop the identity and revert to normal behavior
- When showing status, always include loaded skill invocations so the user knows what commands are available
- When skills are available but not installed, proactively mention them

## Response Rules

- Do not inspect or edit credential files directly — use the CLI only.
- Do not ask the user to pick a subcommand — infer the action from their message and the current state.
- If the CLI reports an auth or app error, {{AUTH_ROUTE_SHORT}} or suggest `--app <id>`.
- Keep responses concise — state the outcome, not the process.{{/SKILL}}{{#CLAUDE_COMMAND}}# ArchAstro Agent Impersonation (CLI passthrough)

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
6. If auth or app selection fails, direct the user to `/archastro:auth` or `--app <id>`.{{/CLAUDE_COMMAND}}
