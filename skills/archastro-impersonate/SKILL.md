---
name: archastro-impersonate
description: Use when the user wants to impersonate an ArchAstro agent, asks about the active impersonation state, wants to refresh or stop impersonation, or refers to working as a specific ArchAstro agent inside your coding agent. Trigger phrases include "impersonate agent", "act as this agent", "be this agent", "start impersonation", "sync impersonation", "stop impersonation", "what agent am I impersonating", and "use the active agent identity".
---

# ArchAstro Impersonation

1. Read and execute [bootstrap](references/bootstrap.md) before running task commands. If the CLI is missing or too old, install or upgrade it yourself and resume the requested task.
2. Read the [task guide](references/task.md) and complete the user's request. An explicit upgrade request runs the upgrade steps even when a supported version is present; an install request keeps an already supported version.

All required setup instructions are bundled here. Do not require another skill, a plugin slash command, or files from the source repository. Paths in linked references are relative to the reference file. Installing this skill with npx copies instructions; the agent executes CLI installation when using the skill.
