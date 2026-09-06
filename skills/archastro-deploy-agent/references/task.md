# ArchAstro Agent Deployment

Deploy an agent from a YAML template and get it running in a thread.

First complete [bootstrap](bootstrap.md), then resume this task.

## Always Start with State

Every invocation must begin by understanding what already exists:

```
archastro auth status
archastro list agents
```

If the user is working from a local repo, also inspect whether a `configs/` directory already exists. Determine whether they want to:
- deploy a new config-driven agent,
- redeploy an existing template,
- or work with an existing running agent.

## Routing

### CLI not installed or too old

Before any deployment work, verify the CLI:

- Read [plugin-compatibility.json](plugin-compatibility.json) beside this reference.
- Prefer `plugins.archastro.minimumCliVersion`, fall back to the top-level `minimumCliVersion`.
- Run `archastro --version`. If missing or older than the resolved minimum, execute [installation](install.md), verify the version, then resume this task.
- If authentication or app selection is missing, run `archastro auth login` and resume after browser authentication completes.

### Local config directory not initialized

If the user has config files but no `configs/` directory set up, route to the [manage-configs guide](manage-configs.md) first. That skill owns local config management.

### User wants to deploy a new agent

Use the config-driven golden path. Do not skip straight to `create agent`.

1. **Deploy configs first**:
   ```
   archastro deploy configs
   ```
   This pushes Script and AgentTemplate configs to the server. For config-driven agents, this should happen before provisioning the agent itself.

2. **Deploy the agent from the template file**:
   ```
   archastro deploy agent <yaml-file>
   ```
   This creates the full agent stack in one step: app config, agent record, routines, and installations. Note the agent ID (`agi_...`) from the output.

   **Important:** Always use `deploy agent`, not `create agent`. The `create agent` command only creates the agent record without provisioning routines or installations.

3. **Verify the deployment**:
   ```
   archastro list agents
   ```

4. **Offer next steps**: ask if the user wants to add the agent to a thread and start chatting. If yes, create a thread with members and hand off to the [chat guide](chat.md).

### User needs help creating or editing the config files first

Route to the [author-agent guide](author-agent.md) before deploying. That skill owns:
- `AgentTemplate` and Script config creation
- `archastro describe configsample`
- `archastro describe scriptdocs`
- routine scheduling shape
- env-var scope guidance

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

## Recovery Rules

- If `archastro deploy agent` fails with a validation-style error, inspect the exact CLI output first. Do not immediately fall back to lower-level provisioning commands.
- If the problem appears to be in the config files, route to `author-agent`.
- If a script-related validation error appears, use:
  ```
  archastro describe scriptdocs
  archastro describe configsample Script
  ```
  Do not invent script syntax from memory.
- Prefer human-readable `config_ref` names that match deployed config lookup keys. Do not rewrite refs to raw `cfg_...` IDs unless explicitly debugging a broken environment.

## Response Rules

- Do not inspect or edit credential files directly — use the CLI only.
- Do not ask the user to pick a subcommand — infer the action from their message.
- If the CLI reports an auth or app error, run `archastro auth login` or suggest `--app <id>`.
- Keep responses concise — state the outcome, not the process.
