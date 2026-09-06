# ArchAstro Agent Authoring

Create or update the config files for a config-driven ArchAstro agent before deployment.

First complete [bootstrap](bootstrap.md), then resume this task.

## Always Start with State

Every invocation must begin by understanding the current project state:

```
archastro auth status
```

If the user is in a repo, inspect whether a `configs/` directory already exists and whether the agent already has Script or AgentTemplate files.

## Routing

### CLI not installed or too old

Before any authoring work, verify the CLI:

- Read [plugin-compatibility.json](plugin-compatibility.json) beside this reference.
- Prefer `plugins.archastro.minimumCliVersion`, fall back to the top-level `minimumCliVersion`.
- Run `archastro --version`. If missing or older than the resolved minimum, execute [installation](install.md), verify the version, then resume this task.
- If authentication or app selection is missing, run `archastro auth login` and resume after browser authentication completes.

### Local config directory not initialized

If the user doesn't have a `configs/` directory set up yet, route to the [manage-configs guide](manage-configs.md) first. That skill owns `archastro init --enable-configs`, local file layout, and the sync/deploy workflow.

### User wants to author or modify agent configs

1. **Start from CLI-backed templates, not memory**:
   - For new config objects, use:
     ```
     archastro describe configsample <Kind>
     ```
   - For Script configs, always use:
     ```
     archastro describe scriptdocs
     archastro describe configsample Script
     ```
     The script docs are the live source of truth. Do not invent or paraphrase the language from memory.

2. **Use the standard config-driven model**:
   - Script logic lives in `kind: Script` configs.
   - Agent behavior lives in an `AgentTemplate`.
   - Custom tools in templates should use `tool_type: custom`, `handler_type: script`, and `config_ref` pointing at Script configs.
   - When creating configs outside a project directory, use `-f` to read from a file:
     ```
     archastro create config -k AgentTemplate -f configs/agents/my-agent.yaml
     ```

3. **Validate early**:
   ```
   archastro validate config -k <Kind> -f <path>
   ```
   Run validation before deploy whenever the user changes Script or template files.

4. **Deploy through the normal flow after authoring**:
   - If the agent has Script configs or other supporting files, sync them first:
     ```
     archastro deploy configs
     ```
     This pushes local config files (Scripts, templates) but does not create agents.
     Skip this step if the agent only has a single AgentTemplate file — `deploy agent` handles its own config upload.
   - For a **new agent**, provision it from its template:
     ```
     archastro deploy agent <yaml-file>
     ```
     This uploads the template config and creates the agent with its routines, tools, and installations.
   - **Important:** `deploy configs` and `deploy agent` are different commands.
     Use `deploy configs` to sync a directory of config files; use `deploy agent` to create an agent from a template.

### Updating an existing agent from edited YAML

Uploading configs does not apply changed template components to a running agent. Resolve the existing agent ID and, after `deploy configs`, inspect the upgrade diff:

```
archastro upgrade agent <agent-id> --template <template-id-or-key> --dry-run
```

Review the returned changes and follow the [deploy-agent guide](deploy-agent.md) to apply the supported in-place upgrade with its review fingerprint. `deploy agent` creates an agent; it is not the update command. Do not automatically use `--recreate`: it replaces the agent and can delete associated threads. If the existing agent cannot use the supported upgrade path, inspect its provenance and available component update commands rather than deleting it.

## Authoring Rules

For a directly provisioned agent without Solution upgrade support, keep the edited YAML as authoring intent and apply only the requested component change through its supported resource command. For a new daily routine, upload/validate its supporting Script config, inspect `list agentroutines --agent <id>`, then `create agentroutine` if absent or `update agentroutine <id>` if it exists. Follow the [build-workflow guide](build-workflow.md) for the handler, activation, and scheduled-run proof. Match the runtime routine to the YAML definition and record the resulting ID; do not claim uploading the YAML automatically reconciled it. Use `update agent --help` for requested agent fields rather than recreating the agent.

### Script configs

- **Load the [build-script guide](build-script.md) for detailed script authoring guidance**, including syntax examples, common mistakes, and the validation/test/deploy workflow.
- Treat the script language as a functional expression language, not a general-purpose imperative language.
- Use `archastro describe scriptdocs` for exact syntax and available namespaces.
- If a script fails validation, prefer rewriting toward the sample/reference instead of trial-and-error improvisation.

### Complete the agent's operating setup

Use `archastro describe configsample AgentTemplate` to discover current fields for identity/instructions, tools, routines, skills, installations, and model settings. Inspect the user's existing template and preserve its ownership and references. Do not infer supported fields from another product's agent format.

- **Tools**: inspect the tool catalog and `archastro create agenttool --help`; use builtin keys for platform capabilities and script/workflow handlers for custom logic. Direct commands take `--config <id>`; template authoring uses its schema's `config_ref`.
- **Skills**: publishing files does not link them to an agent. Declare template skill references and the builtin `skills` tool; follow the [build-skill guide](build-skill.md) for the direct AgentSkill link and runtime verification.
- **Routines**: choose script, workflow graph, preset, or chain according to the job. Presets handle agent reasoning; chains combine named steps. Follow the [build-workflow guide](build-workflow.md) for event filters, input shapes, and execution verification.
- **Installations and secrets**: discover the exact integration settings before adding installations; use CLI environment-variable resources for secret values, not committed templates.

After deployment, verify the actual agent's tools, skills, and routine status. Directly created routines default to draft and need activation when intended to run. Exercise a real chat/tool request or routine trigger and inspect its result; config validation alone does not establish runtime behavior.

### Models, structured results, and storage

Read `archastro help models` before choosing a model; `archastro list aimodels` returns current supported IDs. Keep the fully qualified model ID and the template's actual model fields rather than assuming a provider's raw model name works. Check model capabilities for the requested reasoning, tool use, or output behavior.

For structured output and field guards, inspect `archastro describe configsample AgentTemplate` and `archastro describe configkind AgentTemplate`. Use the current response-schema and field-guard fields, and test valid/invalid outputs against the caller's contract; instructions asking for JSON alone do not establish schema enforcement.

Working memory, knowledge sources, custom objects, and script KV storage solve different persistence needs. Use the [manage-knowledge guide](manage-knowledge.md) for retrieval, the [manage-platform guide](manage-platform.md) for schema-backed records, and `describe scriptdocs` for the current storage namespace and ownership. Inspect agent memory through the [operate-agents guide](operate-agents.md) rather than treating it as a local file.

### Routine configs inside templates

- Scheduled routines need both:
  - `schedule: "<cron>"`
  - `event_type: schedule.cron`
- Do not put schedules under nested `event_config.schedule`.
- To discover valid event types and their payload schemas:
  ```
  archastro list events
  archastro describe event <event-name>
  ```
  The payload schema from `describe event` shows what `$` contains in the routine's script handler.

### Config references

- Prefer human-readable `config_ref` values that match deployed config lookup keys.
- Do not convert refs to raw `cfg_...` IDs unless explicitly debugging a broken environment.

### Environment variables

- For org users, prefer org-scoped environment variables when they are sufficient for the agent's needs.
- Do not default users into app-scoped env-var flows unless the use case truly requires app scope.

## Recovery Rules

- If the user asks for a brand-new Script and the language shape is unclear, run `archastro describe scriptdocs` before drafting.
- If validation fails, surface the exact failing field or syntax problem. Do not immediately switch to lower-level provisioning commands.
- If the user asks to "just create the agent" while configs are still incomplete, finish authoring and validation first, then route to `deploy-agent`.

## Command Conventions

- All config commands are **verb-first**: `archastro list configs`, `archastro create config`, `archastro deploy configs`, `archastro sync configs`, `archastro validate config`, etc.
- There is no `archastro configs` namespace. Do not use `archastro configs <verb>` — always put the verb first.

## Response Rules

- Do not inspect or edit credential files directly — use the CLI only.
- Do not ask the user to pick raw subcommands when intent is clear.
- Keep responses concise and operational.
- Prefer the golden path over fallback commands.
