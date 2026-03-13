---
description: Create threads, manage members, and view thread conversations
allowed-tools: ["Bash(archastro:*)"]
---

# Manage Threads

Create threads, add members, and view conversations.

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

## Creating a Thread

4. **Create the thread**:
   ```
   archastro create thread --title "..." --user <user-id>
   ```
   The `--user` is the thread owner. Note the thread ID (`thr_...`) from the output.

5. **Add members** — agents and users who participate in the thread:
   ```
   archastro create threadmember --thread <thread-id> --agent-id <agent-id>
   archastro create threadmember --thread <thread-id> --user-id <user-id>
   ```
   Add all participants before sending messages. A thread typically has at least one agent and one user.

## Viewing a Thread

6. **Fetch messages with full content**:
   ```
   archastro list threadmessages --thread <thread-id> --full
   ```
   Always use `--full` — the default table view truncates content to 60 characters.

   For programmatic processing, use JSON output:
   ```
   archastro list threadmessages --thread <thread-id> --json
   ```

7. **List thread members**:
   ```
   archastro list threadmembers --thread <thread-id>
   ```

8. **Present the conversation** to the user:
   - Summarize the overall conversation flow (who said what, key decisions)
   - For each message, show the sender and a concise summary of the content
   - Highlight agent feedback, action items, or decisions
   - Offer to expand any individual message on request
