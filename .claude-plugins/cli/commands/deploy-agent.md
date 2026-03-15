---
description: Deploy an agent and add it to a thread
allowed-tools: ["Bash(archastro:*)"]
---

# Deploy an Agent

Deploy an agent from a YAML template and add it to a thread.

## Instructions

1. **Read the compatibility contract first**:
   - Use `plugin-compatibility.json`.
   - For this command, prefer `plugins.cli.minimumCliVersion` and fall back to the top-level `minimumCliVersion`.
   - Treat that resolved value as the minimum supported CLI version for every check below.

2. **Check the installed CLI version first**:
   ```
   archastro --version
   ```
   If the command is missing, or the version is older than the resolved minimum version, tell the user to run `/cli:install`.

3. **Check authentication**:
   ```
   archastro auth status
   ```
   If not authenticated, tell the user to run `/cli:auth`.

4. **Deploy the agent**:
   ```
   archastro deploy agent <yaml-file>
   ```
   This creates the full agent stack in one step: app config, agent record, routines, and installations. Note the agent ID (`agi_...`) from the output.

   **Important:** Use `deploy agent`, not `create agent`. The `create agent` command only creates the agent record without provisioning routines or installations.

5. **Verify the agent was created**:
   ```
   archastro list agents
   ```

6. **Add the agent to a thread**:

   If a thread already exists:
   ```
   archastro create threadmember --thread <thread-id> --agent-id <agent-id>
   ```

   If a new thread is needed, use `/cli:threads` to create one first, then add the agent as a member.

7. **Test the agent** by sending a message using `/cli:send-message`.
