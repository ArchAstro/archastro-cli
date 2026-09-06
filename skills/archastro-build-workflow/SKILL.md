---
name: archastro-build-workflow
description: Use when the user wants to create, edit, or deploy a workflow — a multi-step process with branching, loops, HTTP calls, script execution, approvals, or scheduled routines. Trigger phrases include "build a workflow", "create a workflow", "design a workflow", "add a routine", "schedule a task", "automate this process", "set up a cron job", "workflow nodes".
---

# ArchAstro Workflow Builder

1. Read and execute [bootstrap](references/bootstrap.md) before running task commands. If the CLI is missing or too old, install or upgrade it yourself and resume the requested task.
2. Read the [task guide](references/task.md) and complete the user's request. An explicit upgrade request runs the upgrade steps even when a supported version is present; an install request keeps an already supported version.

All required setup instructions are bundled here. Do not require another skill, a plugin slash command, or files from the source repository. Paths in linked references are relative to the reference file. Installing this skill with npx copies instructions; the agent executes CLI installation when using the skill.
