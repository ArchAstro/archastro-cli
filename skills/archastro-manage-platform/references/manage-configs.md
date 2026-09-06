# ArchAstro Local Config Management

Set up and manage a local `configs/` directory for editing agent configs as files, syncing with the server, and deploying changes.

First complete [bootstrap](bootstrap.md), then resume this task.

## What is Local Config Management?

Instead of creating and editing configs one-by-one through CLI CRUD commands, you can manage them as local files in a `configs/` directory. This enables:
- **Edit configs in your editor** with syntax highlighting and version control
- **Batch deploy** all changes in dependency order
- **Sync** server configs down to local files
- **Browser editor** for visual editing of individual configs

The CLI tracks the mapping between local files and server configs in a manifest file.

## Always Start with State

Every invocation must begin by understanding the current project state:

```
archastro auth status
ls configs/ 2>/dev/null || echo "No configs directory"
```

Determine:
- Does a `configs/` directory already exist?
- Is the user starting a new project or working with an existing one?
- Do they want to pull configs from the server or push local changes?

## Routing

### CLI not installed or too old

Before any config work, verify the CLI:

- Read [plugin-compatibility.json](plugin-compatibility.json) beside this reference.
- Prefer `plugins.archastro.minimumCliVersion`, fall back to the top-level `minimumCliVersion`.
- Run `archastro --version`. If missing or older than the resolved minimum, execute [installation](install.md), verify the version, then resume this task.
- If authentication or app selection is missing, run `archastro auth login` and resume after browser authentication completes.

### User wants to set up a configs directory for the first time

1. **Initialize the config directory**:
   ```
   archastro init --enable-configs
   ```
   This enables local config management and creates the configured `configs/` directory if needed. It does not automatically sync remote configs; use `archastro sync configs` next when you want local files.

2. **Explain the layout**: After init, the directory looks like:
   ```
   configs/
   ├── .archastro-manifest.json    # Maps local files to server configs (do not edit manually)
   ├── agents/                     # AgentTemplate configs
   ├── skills/                     # Skill bundles
   ├── scripts/                    # Script configs
   ├── workflows/                  # Workflow configs
   └── ...                         # Other config kinds
   ```

   Managed virtual paths also follow these prefixes on the server: `skills/`, `scripts/`, and `workflows/`.

3. **Offer next steps**: Ask if the user wants to create a new config (`archastro describe configsample <Kind>`) or sync existing configs from the server.

### App context and owner-pinned directories

Inspect the project config to discover configured directories instead of assuming `configs/`. For noninteractive setup, use `archastro init --app-id <app-id> --enable-configs --no-samples`; `--app-id current` keeps app selection portable.

Each directory has one owner. `--config-dir <path>` follows the signed-in identity; explicit `--config-dir configs/org=org=<org-id>` pins an organization. Supported owners are system, org, user, team, and agent. Use `archastro create configdir --help` to add another directory. Sync and deploy resolve scope per directory, preventing one owner's config set from being treated as another's.

### User wants to pull configs from the server

Sync server configs to local files:
```
archastro sync configs
```

This downloads configs visible to each configured directory's resolved owner — including skills, scripts, and workflows — and writes them as local files in the correct directories. The manifest tracks the file-to-config mapping.

Use `sync configs --dry-run` before reviewing incoming changes. Conflicts default to failure; select `--on-conflict overwrite|skip|fail` deliberately. `--prune-local` deletes tracked local files removed remotely.

After syncing, the directory structure reflects server state:
```
configs/
├── agents/                     # AgentTemplate configs (.yaml)
├── skills/my-skill/            # Skill bundles (SKILL.md + supporting files)
├── scripts/                    # Script configs (.aascript)
├── workflows/                  # Workflow configs (.json)
└── ...                         # Other config kinds
```

You can then edit any file locally and run `archastro deploy configs` to push changes back.

### User wants to create a new config locally

For **scripts**, **skills**, and **workflows**, prefer the dedicated commands or create files directly in the correct directory:

- **Script**: Write a `.agentscript` file in `configs/scripts/`:
  ```
  configs/scripts/my-script.agentscript
  ```
- **Skill**: Create a `SKILL.md` (with frontmatter) in `configs/skills/<slug>/`:
  ```
  configs/skills/my-skill/SKILL.md
  configs/skills/my-skill/prompts/greeting.liquid   # optional supporting files
  ```
- **Workflow**: Write a `.json` file in `configs/workflows/`:
  ```
  configs/workflows/my-workflow.json
  ```

For **other config kinds** (AgentTemplate, Persona, etc.), get a sample:
```
archastro list configkinds
archastro describe configsample <Kind> --to-file ./configs/<category>/<name>.yaml
```

You can also use the browser editor. Its path is relative to the configured config directory (or use an absolute path), not the project root:
```
archastro edit config <category>/<name>.yaml
```

### User wants to validate local configs

Validate a specific config file:
```
archastro validate config -k <Kind> -f ./configs/<category>/<name>.yaml
```

For scripts specifically, use the dedicated validator:
```
archastro validate script --file ./configs/scripts/my-script.agentscript
```

### User wants to deploy local changes

Push all local config changes to the server:
```
archastro deploy configs
```

Deployment considers all configured directories, not only the customer currently being discussed. Before a customer-scoped change, preview the complete diff and verify every pending owner. If unrelated customer edits would also deploy, use a separate project/config registration containing only the intended owner and its required dependencies; do not assume `--app` or changing working subdirectories filters owner directories. Do not use `--take-ownership` to make a scope conflict disappear.

Use `deploy configs --dry-run` to preview, or `--validate-only` to validate against the target server without uploading. `--prune` archives remotely tracked configs removed locally; ordinary deploy does not prune.

This:
- Compares local files against the manifest
- Uploads new and changed configs in dependency order
- Updates the manifest with new server IDs

#### Managed directory conventions

`deploy configs` enforces conventions for three managed directories:

| Directory | Convention |
|-----------|-----------|
| `skills/<slug>/` | `SKILL.md` becomes a `Skill` config; supporting files become `File` configs. The root metadata comes from YAML frontmatter. |
| `scripts/` | `.aascript` / `.agentscript` files become `Script`; `.test.aascript` / `.test.agentscript` become `ScriptTest`. YAML/JSON wrappers must declare `kind: Script` or `kind: ScriptTest`. Other file types are rejected. |
| `workflows/` | Only `.json` files and `.yaml` with a `Workflow*` kind are allowed. Other file types are rejected. |

Files outside these directories use standard kind inference from file extension or YAML content.

**Important**: `deploy configs` syncs config files only. It does not create agents. To provision an agent from a template, use `archastro deploy agent <file>` separately.

### User wants to move or rename a config file

If a local config file is moved or renamed:
```
archastro update configpath <old-path> <new-path>
```

This updates the manifest mapping without affecting the server config.

### User has manifest issues

If the manifest gets out of sync:
```
archastro validate configmanifest
```

This re-normalizes the manifest and resolves any inconsistencies.

## Typical Workflows

### New project from scratch
```
archastro init --enable-configs
archastro describe configsample AgentTemplate --to-file ./configs/agents/my-agent.yaml
# Edit the file...
archastro validate config -k AgentTemplate -f ./configs/agents/my-agent.yaml
archastro deploy configs
archastro deploy agent ./configs/agents/my-agent.yaml
```

### Create a skill via local files
```
archastro init --enable-configs
mkdir -p configs/skills/my-skill
# Write SKILL.md with frontmatter (name, description)
# Add supporting files (prompts, references, etc.)
archastro deploy configs
# Skill is now visible via: archastro list skills
```

### Create a script via local files
```
archastro init --enable-configs
# Write script source directly
echo 'println("hello")' > configs/scripts/my-script.agentscript
archastro deploy configs
# Script is now visible via: archastro describe script my-script
```

### Pull existing project and make changes
```
archastro init --enable-configs
archastro sync configs
# Edit files locally...
archastro deploy configs
```

### Quick edit via browser
```
archastro edit config agents/my-agent.yaml
# Opens in browser with live validation
# Changes are saved locally; deploy afterward to update the server
archastro deploy configs
```

## Response Rules

- Do not inspect or edit credential files directly — use the CLI only.
- Do not manually edit `.archastro-manifest.json` — use CLI commands.
- Do not ask the user to pick raw subcommands when intent is clear.
- Keep responses concise and operational.
- Always recommend `deploy configs` over individual `create config` calls when working with local files.
