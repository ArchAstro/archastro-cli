---
name: archastro-install
description: Use when the user wants to install, upgrade, or bootstrap the ArchAstro CLI. Trigger phrases include "install archastro", "install the archastro CLI", "set up archastro", "upgrade archastro", "archastro not found", "archastro command not found", "install the CLI", "get archastro running".
---

# Install ArchAstro CLI

1. Read and execute [bootstrap](references/bootstrap.md) before running task commands. If the CLI is missing or too old, install or upgrade it yourself and resume the requested task.
2. Read the [task guide](references/task.md) and complete the user's request. An explicit upgrade request runs the upgrade steps even when a supported version is present; an install request keeps an already supported version.

All required setup instructions are bundled here. Do not require another skill, a plugin slash command, or files from the source repository. Paths in linked references are relative to the reference file. Installing this skill with npx copies instructions; the agent executes CLI installation when using the skill.
