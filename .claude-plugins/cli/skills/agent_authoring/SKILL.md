---
name: agent_authoring
description: Use when the user wants to create or edit an ArchAstro agent's config files before deployment, including AgentTemplate files, Script configs, custom tools, routines, and environment setup. Trigger phrases include "build this agent", "write the template", "create the scripts", "set up the routines", "author this agent config".
allowed-tools: ["Bash(archastro:*)"]
---

# ArchAstro Agent Authoring

Create or update the config files for a config-driven ArchAstro agent before deployment.

This skill depends on the `cli` plugin for CLI installation and authentication. Use that plugin's commands instead of trying to install or authenticate the CLI manually inside this skill.

## Always Start with State

Every invocation must begin by understanding the current project state:

```
archastro auth status
```

If the user is in a repo, inspect whether a `configs/` directory already exists and whether the agent already has Script or AgentTemplate files.

## Routing

### CLI not installed or too old

Before any authoring work, verify the CLI:

- Read `plugin-compatibility.json` from the plugin root.
- Prefer `plugins.cli.minimumCliVersion`, fall back to the top-level `minimumCliVersion`.
- Run `archastro --version`. If missing or older than the resolved minimum, direct the user to `/cli:install`.
- If authentication or app selection is missing, direct the user to `/cli:auth`.

### User wants to author or modify agent configs

1. **Start from CLI-backed templates, not memory**:
   - For new config objects, use:
     ```
     archastro configs sample <Kind>
     ```
   - For Script configs, always use:
     ```
     archastro configs script-reference
     archastro configs sample Script
     ```
     The script reference is the live source of truth. Do not invent or paraphrase the language from memory.

2. **Use the standard config-driven model**:
   - Script logic lives in `kind: Script` configs.
   - Agent behavior lives in an `AgentTemplate`.
   - Custom tools should use `kind: custom`, `handler_type: script`, and `config_ref` pointing at Script configs.

3. **Validate early**:
   ```
   archastro configs validate
   ```
   Run validation before deploy whenever the user changes Script or template files.

4. **Deploy through the normal flow after authoring**:
   - First:
     ```
     archastro configs deploy
     ```
   - Then route to the `agent_deploy` skill for:
     ```
     archastro deploy agent <yaml-file>
     ```

## Authoring Rules

### Script configs

- Treat the script language as a functional expression language, not a general-purpose imperative language.
- Use `archastro configs script-reference` for exact syntax and available namespaces.
- If a script fails validation, prefer rewriting toward the sample/reference instead of trial-and-error improvisation.

### Routine configs inside templates

- Scheduled routines need both:
  - `schedule: "<cron>"`
  - `event_type: schedule.cron`
- Do not put schedules under nested `event_config.schedule`.

### Config references

- Prefer human-readable `config_ref` values that match deployed config lookup keys.
- Do not convert refs to raw `cfg_...` IDs unless explicitly debugging a broken environment.

### Environment variables

- For org users, prefer org-scoped environment variables when they are sufficient for the agent's needs.
- Do not default users into app-scoped env-var flows unless the use case truly requires app scope.

## Recovery Rules

- If the user asks for a brand-new Script and the language shape is unclear, run `archastro configs script-reference` before drafting.
- If validation fails, surface the exact failing field or syntax problem. Do not immediately switch to lower-level provisioning commands.
- If the user asks to "just create the agent" while configs are still incomplete, finish authoring and validation first, then route to `agent_deploy`.

## Response Rules

- Do not inspect or edit credential files directly — use the CLI only.
- Do not ask the user to pick raw subcommands when intent is clear.
- Keep responses concise and operational.
- Prefer the golden path over fallback commands.
