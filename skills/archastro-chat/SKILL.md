---
name: archastro-chat
description: Use when the user wants to send a message to an ArchAstro agent, ask an agent a question, view a thread conversation, check for agent responses, or interact with an agent. Trigger phrases include "send a message", "ask the agent", "what did the agent say", "show the conversation", "check the thread", "talk to the agent", "message the agent", "create a session".
---

# ArchAstro Agent Chat

1. Read and execute [bootstrap](references/bootstrap.md) before running task commands. If the CLI is missing or too old, install or upgrade it yourself and resume the requested task.
2. Read the [task guide](references/task.md) and complete the user's request. An explicit upgrade request runs the upgrade steps even when a supported version is present; an install request keeps an already supported version.

All required setup instructions are bundled here. Do not require another skill, a plugin slash command, or files from the source repository. Paths in linked references are relative to the reference file. Installing this skill with npx copies instructions; the agent executes CLI installation when using the skill.
