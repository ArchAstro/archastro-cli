---
name: agent_deploy
description: Use when the user wants to deploy an ArchAstro agent, set up a new agent from a YAML template, or get an agent running in a thread. Trigger phrases include "deploy agent", "deploy this agent", "set up an agent", "create an agent", "get this agent running", "launch agent".
allowed-tools: ["Bash(archastro:*)"]
---

# ArchAstro Agent Deployment

Deploy an agent from a YAML template and get it running in a thread.

This skill depends on the `cli` plugin for CLI installation and authentication. Use that plugin's commands instead of trying to install or authenticate the CLI manually inside this skill.

## Always Start with State

Every invocation must begin by understanding what already exists:

```
archastro list agents
```

Determine whether the user wants to deploy a new agent or work with an existing one.

## Routing

### CLI not installed or too old

Before any deployment work, verify the CLI:

- Read `plugin-compatibility.json` from the plugin root.
- Prefer `plugins.cli.minimumCliVersion`, fall back to the top-level `minimumCliVersion`.
- Run `archastro --version`. If missing or older than the resolved minimum, direct the user to `/cli:install`.
- If authentication or app selection is missing, direct the user to `/cli:auth`.

### User wants to deploy a new agent

1. **Deploy the agent**:
   ```
   archastro deploy agent <yaml-file>
   ```
   This creates the full agent stack in one step: app config, agent record, routines, and installations. Note the agent ID (`agi_...`) from the output.

   **Important:** Always use `deploy agent`, not `create agent`. The `create agent` command only creates the agent record without provisioning routines or installations.

2. **Verify the deployment**:
   ```
   archastro list agents
   ```

3. **Offer next steps**: ask if the user wants to add the agent to a thread and start chatting. If yes, create a thread with members and hand off to the `chat` skill.

### User wants to add an agent to a thread

1. **If no thread exists**, create one:
   ```
   archastro create thread --title "..." --user <user-id>
   ```

2. **Add the agent as a member**:
   ```
   archastro create threadmember --thread <thread-id> --agent-id <agent-id>
   ```

3. **Add any other participants**:
   ```
   archastro create threadmember --thread <thread-id> --user-id <user-id>
   ```

4. **Confirm** the thread is ready and offer to send the first message.

### User asks about existing agents

List agents and present them:
```
archastro list agents
```

Summarize what's deployed and offer to deploy a new one or add an existing one to a thread.

## Response Rules

- Do not inspect or edit credential files directly — use the CLI only.
- Do not ask the user to pick a subcommand — infer the action from their message.
- If the CLI reports an auth or app error, route to `/cli:auth` or suggest `--app <id>`.
- Keep responses concise — state the outcome, not the process.
