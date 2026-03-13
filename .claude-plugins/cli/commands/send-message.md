---
description: Send a message in a thread and wait for the agent's response
allowed-tools: ["Bash(archastro:*)"]
---

# Send Message and Wait for Response

Send a message to a thread and wait for the agent's reply.

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

4. **Determine the sender ID**:

   **Org mode** (authenticated as an app user): The user's ID is shown in `archastro auth status`. Use that as `--user-id`.

   **Developer mode** (authenticated as a developer): Look up thread members to find the correct sender:
   ```
   archastro list threadmembers --thread <thread-id>
   ```

5. **Send the message and wait for the response**:
   ```
   archastro create threadmessage --thread <thread-id> --user-id <user-id> --content "..." \
     --wait --wait-timeout 300
   ```
   Use `run_in_background: true` so you remain responsive while waiting.

   - `--wait-settle 5` (default) waits 5 seconds after the last message before returning, in case the agent sends multiple messages.
   - Set `--wait-timeout` generously — agent responses often take 30–90 seconds, sometimes longer.

6. **Tell the user** the message was sent and the agent is processing. Let them know you're available to keep working on other things while waiting.

7. **When the response arrives**, read the full content:
   ```
   archastro list threadmessages --thread <thread-id> --full
   ```
   The default table view truncates content to 60 characters — always use `--full` when reading responses.

8. **Present the response** to the user:
   - Summarize key points from the agent's reply
   - Highlight any action items, decisions, or questions
   - Offer to send a follow-up message if appropriate
