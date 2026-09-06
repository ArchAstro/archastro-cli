---
name: build-skill
description: Use when the user wants to create, edit, or publish an ArchAstro skill — a reusable package of instructions and supporting files that agents can use. Trigger phrases include "build a skill", "create a skill", "write a skill", "author a skill", "new skill", "skill template", "SKILL.md".
allowed-tools: ["Bash(archastro:*)"]
---

# ArchAstro Skill Builder

Create, edit, and publish skills — reusable instruction packages that agents invoke at runtime.

This skill assumes the ArchAstro CLI is already installed and authenticated. Install or upgrade `archastro` if missing, and run `archastro auth login` if not authenticated.

## What is a Skill?

A skill is a file-backed bundle anchored by a `SKILL.md` root file with optional supporting files. Skills use the same managed virtual-path model as scripts and workflows: skills live under `skills/<slug>/...`, scripts under `scripts/...`, and workflows under `workflows/...`. Agents invoke skills at runtime via the `get_skill` tool to load instructions on demand.

## Always Start with State

Every invocation must begin by understanding the current context:

```
archastro auth status
archastro list skills
```

Determine whether the user wants to:
- create a brand-new skill,
- edit an existing skill,
- or inspect a skill before modifying it.

## Routing

### CLI not installed or too old

Before any skill work, verify the CLI:

- Read `plugin-compatibility.json` from the plugin root.
- Prefer `plugins.archastro.minimumCliVersion`, fall back to the top-level `minimumCliVersion`.
- Run `archastro --version`. If missing or older than the resolved minimum, instruct the user to install or upgrade `archastro`.
- If authentication or app selection is missing, instruct the user to run `archastro auth login`.

### User wants to create a new skill

Walk through the authoring flow step by step.

1. **Gather requirements**:
   - What should the skill do? (purpose and scope)
   - What trigger phrases should activate it? (for the description field)
   - Does it need supporting files (templates, schemas, reference docs)?
   - Which agent(s) will use it?

2. **Choose a slug**: Short, lowercase, hyphen-separated identifier (e.g., `order-lookup`, `weekly-report`). This becomes the skill's permanent key.

3. **Author the SKILL.md file locally**:

   Create a directory structure:
   ```
   skills/<slug>/
   ├── SKILL.md              # Root file (required)
   └── references/            # Optional supporting files
       └── example.md
   ```

   The SKILL.md must have YAML frontmatter:
   ```yaml
   ---
   name: <skill-name>
   description: <One-line description with trigger phrases. Be specific — this is how
     the agent decides when to invoke the skill. Include phrases like "use when...",
     "trigger phrases include...">
   ---

   # Skill Title

   Detailed instructions for the agent...
   ```

4. **Write effective skill instructions**:
   - **Be concrete**: Provide exact CLI commands, API calls, or code patterns the agent should use.
   - **Use phases**: Break complex workflows into numbered phases with clear entry/exit criteria.
   - **Include routing**: Tell the agent how to handle different user intents within the skill's scope.
   - **Add recovery rules**: What to do when things fail.
   - **Set response rules**: How terse or verbose the agent should be.
   - **Keep it narrow**: One skill, one job. If it's doing two things, split into two skills.

5. **Publish the skill to the platform**:

   **Option A — Via `deploy configs`** (recommended when working with a configs/ directory):

   Place the skill directory under `configs/skills/<slug>/` and deploy:
   ```
   archastro deploy configs
   ```
   This automatically creates the skill with name and description from the SKILL.md frontmatter, and publishes all supporting files as File configs. See the `manage-configs` skill for setting up the configs directory.

   **Option B — Via dedicated commands:**
   ```
   archastro create skill -n "<Name>" -d "<Description>" -s <slug> --file ./skills/<slug>/SKILL.md
   ```

   If there are supporting files, add them:
   ```
   archastro create skillfile <slug> references/example.md --file ./skills/<slug>/references/example.md
   ```

6. **Verify the skill was created**:
   ```
   archastro describe skill <slug>
   archastro describe skillfile <slug> SKILL.md
   ```

7. **Link the skill and enable runtime access**. Publishing a skill alone does not attach it to an agent. Both an AgentSkill link and the builtin `skills` tool are required:
   ```
   archastro describe skill <slug> --output json
   archastro list agentskills --agent <agent-id>
   archastro list agenttools --agent <agent-id>
   archastro create agentskill --agent <agent-id> --config <root-config-id>
   archastro create agenttool --agent <agent-id> --kind builtin --builtin-tool-key skills
   ```
   Read `rootConfigId` from the described skill. Reuse existing links and builtin tools instead of duplicating them. The builtin tool exposes `get_skill` at runtime. For deploy-managed agents, declare the skill in the AgentTemplate's `skills` block and include its builtin skills tool; obtain the exact schema with `archastro describe configsample AgentTemplate`.

8. **Verify runtime use**. Check `list agentskills` and `list agenttools`, then use the chat skill to exercise a request that should load the skill and inspect the conversation/tool result. File publication and linking alone do not prove the agent can use the package.

### User wants to edit an existing skill

1. **Inspect the current state**:
   ```
   archastro describe skill <slug>
   archastro describe skillfile <slug> SKILL.md
   ```

2. **Make edits locally**, then update:
   ```
   archastro update skillfile <slug> SKILL.md --file ./skills/<slug>/SKILL.md
   ```

   For supporting files:
   ```
   archastro update skillfile <slug> <path> --file ./local/path
   ```

3. **Verify the update**:
   ```
   archastro describe skillfile <slug> SKILL.md
   ```

### Platform skills versus public coding-agent skills

The commands above publish platform skill files and AgentSkill links. Public skills installed with `npx skills` are local coding-agent instruction packages; `archastro setup` installs the public ArchAstro CLI guidance. Publishing a platform skill does not publish a Git repository or install it into a local coding agent.

### User wants to install a platform skill into their local coding harness

Linked platform skills can be installed locally for Claude Code, Codex, Cursor, or Rovo Dev. Starting an embed also installs linked skills; select the intended harness and scope:

```
archastro embed start <agent-id> --harness codex --install-scope project
archastro embed list skills
archastro embed install skill <skill-config-id> --harness claude
archastro embed install skill <skill-config-id> --harness codex --install-scope project
archastro embed install skill <skill-config-id> --harness cursor
```

Use `--install-scope project` for repository-local installation or `user` for the user profile (the default). Follow the CLI-reported destination; public `npx skills` installation and embed installation are separate flows.

## Skill Authoring Best Practices

- **Narrow scope**: Each skill should do one thing well. Split broad skills into composable pieces.
- **Concrete instructions**: Provide exact commands and patterns, not vague guidance.
- **Trigger phrases**: The description field is how agents route to the skill — make trigger phrases specific and varied.
- **Version awareness**: When updating a skill, keep in mind that running agents pick up changes on next invocation.
- **Review before publishing**: Skills are executable instructions — review them like code.
- **Supporting files**: Use `references/` subdirectories for large reference material the skill can load on demand.

## Recovery Rules

- If `archastro create skill` fails with a duplicate slug error, the skill already exists — offer to update it instead.
- If the user is unsure about the skill format, show them the SKILL.md template above.
- If the user asks for a "sample skill", generate one from the template with placeholder content tailored to their use case.

## Response Rules

- Do not inspect or edit credential files directly — use the CLI only.
- Do not ask the user to pick raw subcommands when intent is clear.
- Keep responses concise and operational.
- Prefer showing the user a concrete SKILL.md draft they can review over abstract guidance.
