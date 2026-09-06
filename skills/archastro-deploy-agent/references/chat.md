# ArchAstro Agent Chat

Send messages to agents and view their responses.

First complete [bootstrap](bootstrap.md), then resume this task.

## Quick Reference

| Task | Command |
|------|---------|
| Ask agent a question | `archastro create agentsession --agent <id> --instructions "..." --wait` |
| Create a thread | `archastro create thread --title "..." --owner-type agent --owner-id <agent-id> --json` |
| Create a test user | `archastro create user --system-user --name "..." --json` |
| Add member to thread | `archastro create threadmember --thread <id> --user-id <id> --json` |
| Add agent to thread | `archastro create threadmember --thread <id> --agent-id <id> --json` |
| Send message (wait for reply) | `archastro create threadmessage --thread <id> --user-id <id> -c "..." --wait --json` |
| View conversation | `archastro list threadmessages --thread <id> --full` |
| List agent sessions | `archastro list agentsessions --agent <id> --json` |

Use `--help` on any command for full options.

## Always Start with State

Every invocation must begin by understanding the current context. Determine:

1. Does the user want a quick one-off question (use agent session) or an ongoing conversation (use thread)?
2. Do they have an existing session or thread, or need a new one?

## Two Interaction Models

### Agent Sessions (recommended for most use cases)

Direct 1:1 conversation with an agent. Use `--wait` to stream the response via SSE.

**One-shot question** — put the question in `--instructions` and use `--wait`:
```
archastro create agentsession --agent <agent-id> --instructions "What are the open issues?" --wait
```
The agent processes the instructions as its task. `--wait` streams updates until completion.

**Multi-turn conversation** — create session, send messages with `exec --wait`:
```
archastro create agentsession --agent <agent-id> --thread-id <thread-id> --instructions "Respond to messages"
archastro exec agentsession <session-id> -m "What are the open issues?" --wait
```
`exec --wait` blocks and streams the agent's response in real-time. Without `--wait`, exec returns immediately after sending.

### Threads (for multi-participant conversations)

Threads support multiple users and agents. Use when you need ongoing conversation context or multiple participants.

## Routing

### CLI not installed or too old

Before any chat work, verify the CLI:

- Read [plugin-compatibility.json](plugin-compatibility.json) beside this reference.
- Prefer `plugins.archastro.minimumCliVersion`, fall back to the top-level `minimumCliVersion`.
- Run `archastro --version`. If missing or older than the resolved minimum, execute [installation](install.md), verify the version, then resume this task.
- If authentication or app selection is missing, run `archastro auth login` and resume after browser authentication completes.

### User wants to ask an agent a question

**Preferred: agent session with `--wait`**

```
archastro create agentsession --agent <agent-id> --instructions "<question>" --wait
```
This creates the session, processes the question, and streams the result — all in one command.

For longer timeouts:
```
archastro create agentsession --agent <agent-id> --instructions "<question>" --wait --timeout 300
```

**Alternative: exec with `--wait`**

If you need to send follow-up messages to an existing session:
```
archastro exec agentsession <session-id> -m "<question>" --wait
```

**Without `--wait`** (fire-and-forget):
```
archastro create agentsession --agent <agent-id> --instructions "<question>"
archastro describe agentsession <session-id> --follow
```
Use `describe --follow` to stream updates on a session created without `--wait`.

### User wants to send a thread message

1. **Determine the sender ID**: Get the user's ID from `archastro auth status`.

2. **Send the message and wait for the response**:
   ```
   archastro create threadmessage --thread <thread-id> --user-id <user-id> --content "..." \
     --wait --wait-timeout 300
   ```

3. **When the response arrives**, read the full content:
   ```
   archastro list threadmessages --thread <thread-id> --full
   ```

### User wants to view a conversation

```
archastro list threadmessages --thread <thread-id> --full
```
Always use `--full` — the default table view truncates content.

### User needs a new thread

**Agent-owned thread** (recommended when an agent should participate):

1. Create the thread owned by the agent:
   ```
   archastro create thread --title "..." --owner-type agent --owner-id <agent-id> --json
   ```

2. Create a test user (if needed) and add them to the thread:
   ```
   archastro create user --system-user --name "Test User" --json
   archastro create threadmember --thread <thread-id> --user-id <user-id> --json
   ```

3. Send a message and wait for the agent to respond:
   ```
   archastro create threadmessage --thread <thread-id> --user-id <user-id> -c "Hello" --wait --json
   ```

4. View the conversation:
   ```
   archastro list threadmessages --thread <thread-id> --full
   ```

**User-owned thread** (when a user starts the conversation):

1. Create the thread:
   ```
   archastro create thread --title "..." --user <user-id> --json
   ```

2. Add the agent:
   ```
   archastro create threadmember --thread <thread-id> --agent-id <agent-id> --json
   ```

## Response Rules

- Do not inspect or edit credential files directly — use the CLI only.
- Do not ask the user to pick a subcommand — infer the action from their message.
- If the CLI reports an auth or app error, run `archastro auth login` or suggest `--app <id>`.
- Keep responses concise — state the outcome, not the process.
- **Prefer agent sessions over threads** for simple question/answer interactions.
- **Always use `--wait`** when the user expects to see the agent's response.
