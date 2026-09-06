---
targets:
  claude-skill: chat
  codex-skill: chat
skill:
  name: chat
  description: Use when the user wants to send a message to an ArchAstro agent, ask an agent a question, view a thread conversation, check for agent responses, or interact with an agent. Trigger phrases include "send a message", "ask the agent", "what did the agent say", "show the conversation", "check the thread", "talk to the agent", "message the agent", "create a session".
  allowed-tools: ["Bash(archastro:*)"]
---


# ArchAstro Agent Chat

Send messages to agents and view their responses.

This skill assumes the ArchAstro CLI is already installed and authenticated. {{ASSUME_INSTALLED}}

## Quick Reference

| Task | Command |
|------|---------|
| Ask agent a question | `archastro create agentsession --agent <id> --instructions "..." --wait` |
| Create a thread | `archastro create thread --title "..." --owner-type agent --owner-id <agent-id> --json` |
| Create a test user | `archastro create user --system-user --name "..." --json` |
| Add member to thread | `archastro create threadmember --thread <id> --user <id> --json` |
| Add agent to thread | `archastro create threadmember --thread <id> --agent <id> --json` |
| Send message (wait for reply) | `archastro create threadmessage --thread <id> --user <id> -c "..." --wait --json` |
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
archastro create agentsession --agent <agent-id> --thread <thread-id> --idle
archastro exec agentsession <session-id> -m "What are the open issues?" --wait
```
`exec --wait` blocks and streams the agent's response in real-time. Without `--wait`, exec returns immediately after sending.

### Threads (for multi-participant conversations)

Threads support multiple users and agents. Use when you need ongoing conversation context or multiple participants. Agent membership alone does not start a reply: the agent needs a configured message-handling routine. If `--wait` times out, inspect the agent and its routines rather than posting the same message repeatedly.

`list threadmessages` returns the newest page first (25 messages by default). Use `--page` / `--limit` for older history; `--full` expands content but does not fetch every page. `create thread` also supports `--member-user` and `--member-agent` to add participants atomically.

## Routing

### CLI not installed or too old

Before any chat work, verify the CLI:

- Read `plugin-compatibility.json` from the plugin root.
- Prefer `plugins.archastro.minimumCliVersion`, fall back to the top-level `minimumCliVersion`.
- Run `archastro --version`. If missing or older than the resolved minimum, {{INSTALL_ROUTE}}.
- If authentication or app selection is missing, {{AUTH_ROUTE}}.

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

1. **Determine the sender identity**: Reuse the authenticated app user when available. A developer-account User ID from `auth status` is not necessarily a user in the target app. Use `archastro list users --help` and select an existing app user, or create a system user only when a test participant is needed.

2. **Send the message and wait for the response**:
   ```
   archastro create threadmessage --thread <thread-id> --user <user-id> --content "..." \
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
   archastro create threadmember --thread <thread-id> --user <user-id> --json
   ```

3. Send a message and wait for the agent to respond:
   ```
   archastro create threadmessage --thread <thread-id> --user <user-id> -c "Hello" --wait --json
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
   archastro create threadmember --thread <thread-id> --agent <agent-id> --json
   ```

## Response Rules

- Do not inspect or edit credential files directly — use the CLI only.
- Do not ask the user to pick a subcommand — infer the action from their message.
- If the CLI reports an auth or app error, {{AUTH_ROUTE_SHORT}} or suggest `--app <id>`.
- Keep responses concise — state the outcome, not the process.
- **Prefer agent sessions over threads** for simple question/answer interactions.
- **Always use `--wait`** when the user expects to see the agent's response.
