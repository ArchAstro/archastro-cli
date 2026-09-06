# Manage ArchAstro Work

First complete [bootstrap](bootstrap.md), then resume this task.

## Choose the work surface

| User outcome | Surface |
|---|---|
| Track shared work, owners, blockers, comments | Platform tasks |
| Run an interactive or one-shot local coding session | AstroDev |
| Discover work and review local harness output | Astrorun |
| Execute a durable workflow's agent handoff | Work items |
| Generate image assets from the CLI | Astroimage |

Tasks, Astrorun's local manual tasks, and workflow work items are different records.
Do not substitute one for another or claim work merely to inspect its status.
Use `archastro auth status` and command-specific `--help` before selecting the
app, owner, agent, or execution. Run local coding commands from the intended repo.

## Platform tasks

Tasks belong to a team or a user. `--team` and `--user` select the owning list;
`--owner-user` / `--owner-agent` select an assignee. With neither scope flag,
the list defaults to the signed-in user (`me`). Task CLI writes require a user
session; if prompted, use `archastro auth login <email>` rather than substituting
a developer credential or fabricating a user identity.

```bash
archastro list tasks --team <team-id> --status open --json
archastro describe task <task-id> --json
archastro create task --team <team-id> --name "Draft release notes" --priority 2 --json
archastro update task <task-id> --owner-agent <agent-id> --status in_progress --json
```

Statuses are `open`, `in_progress`, and `done`; priority is 0 (highest) through 4.
Read `create task --help` and `update task --help` for due dates, tags, metadata,
and related links. Updates to tags, metadata, and links replace those fields;
inspect existing values before changing them. Nullable fields use `none` to clear
where documented by help.

### Subtasks, dependencies, and history

```bash
archastro create task --team <team-id> --name "Collect changes" --parent <task-id> --json
archastro update task <task-id> --add-blocker <prerequisite-id> --json
archastro list task-blockers <task-id> --json
archastro list task-blocking <task-id> --json
archastro list task-subtasks <task-id> --json
archastro list task-activity <task-id> --json
archastro list task-comments <task-id> --json
```

`--add-blocker` makes the target task depend on the supplied prerequisite.
`--remove-blocker` removes that relationship. A blocked flag reflects unfinished
prerequisites; it does not itself prevent status changes. Use `list task-cycles
--help` for diagnosing dependency cycles in the selected owner scope. Use
`create task-comment --help` when the user requests a progress comment.

### Coding-session leases

A lease coordinates the coding session currently working on a task; assignment
alone is not a lease. Inspect before claiming:

```bash
archastro describe task-lease <task-id> --json
archastro claim task <task-id> --lease-id <lease-uuid> --session-id <session-uuid> --session-name "Release notes" --harness <harness-name> --json
```

Use the real coding session's UUID and harness identity. Generate a UUID for a
new lease and preserve it paired with that session; verify the returned lease.
Renew during work before its expiry, using that same identity:

```bash
archastro renew task-lease <task-id> --lease-id <lease-uuid> --session-id <session-uuid> --json
```

Inspect the renewed expiry and continue renewing while working; a successful
initial claim alone does not preserve ownership. If the lease expires, ownership
is lost, or renewal conflicts, stop task execution and completion updates until
ownership is resolved. Do not overwrite another session's lease or invent a new
identity to evade a conflict. Lease-aware `update task` and `release task-lease`
also take the same `--lease-id` and `--session-id`. Complete the task while holding
the lease, then release it; completion and release are separate operations.
Task leases use **renew**; durable workflow work items below use **heartbeat**.

## AstroDev: local coding execution

AstroDev ships in the CLI and can run standalone or with a deployed agent's
identity, tools, and linked skills. It can edit files and execute shell commands.
Use the user's authorized directory and task, preserving its permission controls.

```bash
archastro astrodev
archastro astrodev --agent <agent-id> --print "Explain this repository" --output-format json
archastro astrodev --resume <session-id>
```

Use exact `--agent` IDs or lookup keys for deterministic selection. The positional
agent argument seeds the interactive selector. Read `astrodev --help` for model
selection, turn limits, configured `--review` / `--workflow` execution, workflow
input, and review target. Configured local workflows are not automatically the
same as platform workflow IDs. Do not replace the requested workflow with a
new remote agent session; local file context and execution ownership differ.

## Astrorun: discovery, execution, and review

From a linked project, `archastro astrorun` opens the local queue. It discovers
thread activity and durable workflow handoffs and supports local manual tasks.
Processors include AstroDev and separately installed coding harnesses. Headless
execution needs no tmux; supported live sessions do.

Review is required by default: enqueue a candidate, inspect the draft and proposed
action, then approve or send correction feedback. Thread approval posts as the
selected agent; a manual task's approval marks local work complete. Do not turn
off review or post a drafted reply without authorization for that behavior.

`archastro astrorun attach` lists live sessions; add the returned ID to attach.
Detaching leaves a live process running. Quitting the dashboard retains stored
work. `astrorun --cleanup` kills live Astrorun tmux sessions, while `astrorun clear`
also clears work/history; neither is an ordinary diagnostic or restart step.

## Durable workflow work items

A work item is an agent handoff owned by a durable workflow execution. Listing
is read-only; claiming reserves it for a worker and returns its lease identity.

```bash
archastro list workitems --agent <agent-id> --execution <execution-id> --json
archastro claim workitem --agent <agent-id> --execution <execution-id> --json
archastro start workitem <work-item-id> --lease-owner <returned-token> --json
archastro heartbeat workitem <work-item-id> --lease-owner <returned-token> --json
archastro submit workitem <work-item-id> --lease-owner <returned-token> --result '{"summary":"Completed requested work"}' --json
```

Carry the claim's exact lease-owner token through start, heartbeat, and submission.
To resume a specific item, supply its ID and original `--lease-owner` to claim.
Read the work payload and required output contract before execution; the example
result above is not a universal schema. Heartbeat during owned work according to
the lease duration. Submit actual output to wake the workflow, or use `fail
workitem --help` to report a JSON failure. A lease conflict means ownership must
be resolved before continuing; never submit with a fabricated replacement token.

## CLI image generation

When the user requests image assets, `archastro astroimage --help` describes the
CLI route. Discover available models with `astroimage models` and supported
parameters with `astroimage options --help` before selecting model-specific
size, quality, or format inputs.

```bash
archastro astroimage "A watercolor mountain landscape" --output-dir ./assets --output-format json
```

Generation calls a platform model and writes local files. Preserve existing files
unless overwrite is requested. Report the returned paths and inspect generated
images when visual verification is available; a successful request alone does
not establish that the image satisfies the brief.

For a requested embedding comparison, inspect `archastro run embeddingcomparison --help`; it compares two text values using the platform embedding model. Keep that diagnostic separate from image generation or a claim that an agent's knowledge retrieval is correct.
