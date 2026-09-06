---
targets:
  claude-skill: deploy-agent
  codex-skill: deploy-agent
skill:
  name: deploy-agent
  description: Use when the user wants to deploy an ArchAstro agent, turn a config-driven agent repo into a running agent, or get an existing agent running in a thread. Trigger phrases include "deploy agent", "deploy this agent", "set up an agent", "launch agent", "ship this agent", "get this agent running".
  allowed-tools: ["Bash(archastro:*)"]
---


# ArchAstro Agent Deployment

Deploy an agent from a YAML template and get it running in a thread.

This skill assumes the ArchAstro CLI is already installed and authenticated. {{ASSUME_INSTALLED}}

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

- Read `plugin-compatibility.json` from the plugin root.
- Prefer `plugins.archastro.minimumCliVersion`, fall back to the top-level `minimumCliVersion`.
- Run `archastro --version`. If missing or older than the resolved minimum, {{INSTALL_ROUTE}}.
- If authentication or app selection is missing, {{AUTH_ROUTE}}.

### Local config directory not initialized

If the user has config files but no `configs/` directory set up, route to the `manage-configs` skill first. That skill owns local config management.

### User wants to deploy a new agent

Use the config-driven golden path. Do not skip straight to `create agent`.

1. **Deploy supporting configs when needed**:
   ```
   archastro deploy configs
   ```
   Run this only when the template references local scripts, skills, workflows, schemas, or other supporting configs. A self-contained AgentTemplate can go directly to `deploy agent`. Remove unused sample references rather than deploying unrelated dependencies.

2. **Deploy the agent from the template file**:
   ```
   archastro deploy agent <yaml-file>
   ```
   This creates the full agent stack in one step: app config, agent record, routines, and installations. Record the agent ID returned in the output.

   **Important:** Always use `deploy agent`, not `create agent`. The `create agent` command only creates the agent record without provisioning routines or installations.

3. **Verify the deployment**:
   ```
   archastro list agents
   ```

4. **Offer next steps**: ask if the user wants to add the agent to a thread and start chatting. If yes, create a thread with members and hand off to the `chat` skill.

### Existing templates and redeployment

`archastro deploy agent --template <config-id-or-lookup-key>` provisions from an existing server template without uploading a file. Keep the template config lookup key distinct from the agent lookup key (`agent_key` in YAML or `--agent-key`).

Do not assume deployment updates an existing agent in place. Inspect the existing agent before repeating a deploy. `--recreate` deletes the matching agent and its threads, routines, and installations before creating another; use it only when that deletion is explicitly intended. Updating config files with `deploy configs` alone does not reprovision an existing agent.

### User wants to upgrade an existing agent

For an agent tracked to a Solution AgentTemplate, use `upgrade agent` to apply template changes to the existing agent. Uploading a newer config version alone does not apply that version to the running agent. Inspect its current state, then preview:

```
archastro describe agent <agent-id> --json
archastro upgrade agent <agent-id> --dry-run --json
```

The preview reports additions, updates, removals, and unchanged resources. Inspect its template and Solution identities and the proposed changes. To select a replacement Solution AgentTemplate, add `--template <config-id-or-lookup-key>` to both preview and apply. This is not a general command for replacing an arbitrary untracked agent; report unsupported-template errors rather than falling back to deletion.

Apply the same reviewed inputs, passing the actual `review_fingerprint` returned by the preview:

```
archastro upgrade agent <agent-id> --review-fingerprint <review-fingerprint> --json
archastro describe agent <agent-id> --json
```

If the fingerprint is stale, fetch a fresh preview and review it again. Verify the same agent ID and the returned upgrade result after applying. `upgrade` updates the existing agent's template-managed resources; `deploy agent --recreate` deletes and replaces the agent and is a separate destructive operation.

### User wants to export an existing agent

```
archastro export agent <agent-id> --dir ./agent-export
```

This writes `agents/<agent-key>.json` plus dependent configs at their virtual paths. Use a fresh output directory to avoid overwriting local edits. Without `--dir`, `--json` returns the template and dependent-config envelope instead. Export captures authoring configuration, not a backup of thread history or runtime state. Inspect the emitted files and dependency references before incorporating them into a managed config directory. Deploy supporting configs first if provisioning a new agent from that exported template; do not treat an export/redeploy as an in-place upgrade.

### User needs help creating or editing the config files first

Route to the `author-agent` skill before deploying. That skill owns:
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
   archastro create threadmember --thread <thread-id> --agent <agent-id>
   ```

3. **Add any other participants**:
   ```
   archastro create threadmember --thread <thread-id> --user <user-id>
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
- If the CLI reports an auth or app error, {{AUTH_ROUTE_SHORT}} or suggest `--app <id>`.
- Keep responses concise — state the outcome, not the process.
