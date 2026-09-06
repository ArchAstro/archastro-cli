---
name: build-workflow
description: Use when the user wants to create, edit, or deploy a workflow — a multi-step process with branching, loops, HTTP calls, script execution, approvals, or scheduled routines. Trigger phrases include "build a workflow", "create a workflow", "design a workflow", "add a routine", "schedule a task", "automate this process", "set up a cron job", "workflow nodes".
allowed-tools: ["Bash(archastro:*)"]
---

# ArchAstro Workflow Builder

Create, edit, and deploy workflows — multi-step processes that agents execute via routines.

This skill assumes the ArchAstro CLI is already installed and authenticated. Use the `/archastro:install` and `/archastro:auth` commands in this same plugin instead of trying to install or authenticate the CLI manually inside this skill.

## What is a Workflow?

A workflow is a directed graph of nodes that defines a multi-step process. Use the dedicated top-level workflow resource for authoring: `archastro list workflows`, `describe workflow`, `create workflow`, `update workflow`, `validate workflow`, and `describe workflowdocs`. Workflows are then attached to agent routines for execution.

## Always Start with State

Every invocation must begin by understanding the current context:

```
archastro auth status
archastro list agents
```

Determine:
- Which agent will run this workflow?
- Is this a new workflow or an update to an existing one?
- What trigger should start it? (schedule, webhook, manual, message event)

## Routing

### CLI not installed or too old

Before any workflow work, verify the CLI:

- Read `plugin-compatibility.json` from the plugin root.
- Prefer `plugins.archastro.minimumCliVersion`, fall back to the top-level `minimumCliVersion`.
- Run `archastro --version`. If missing or older than the resolved minimum, direct the user to `/archastro:install`.
- If authentication or app selection is missing, direct the user to `/archastro:auth`.

### User wants to create a new workflow

**Phase 1: Gather requirements**

Understand the workflow before writing any config:
- What triggers it? (cron schedule, webhook, message, manual)
- What are the steps? (in plain language)
- Are there branches or conditions?
- Does it need to call external APIs?
- Does it need to send emails, Slack messages, or other notifications?
- Does it loop over a collection?

**Discover available events** to understand what can trigger the workflow and what data the trigger provides:
```
archastro list events
```

Once the user picks an event type, show them the payload schema so they know what `$` contains in downstream scripts:
```
archastro describe event <event-name>
```

This returns the JSON schema and a sample payload. The payload fields are accessible via `$` in scripts (e.g., `$.thread_id`, `$.message.content`).

**Phase 2: Scaffold the workflow**

Use the top-level workflow commands, not `describe configsample`/`validate config`, for the normal authoring loop.

Create a workflow from a local JSON file:
```
archastro create workflow --id my-workflow --file ./workflows/my-workflow.json
```

Or let the CLI start from its built-in sample if you do not pass `--graph` or `--file`:
```
archastro create workflow --id my-workflow
```

**Phase 3: Author the workflow**

A workflow is a `WorkflowGraph` JSON config under the hood, but the user-facing authoring path should go through the top-level workflow commands.

Start with the graph returned by `create workflow --id my-workflow` when no file is supplied, inspect it with `describe workflow my-workflow --output json`, and edit its graph locally. This creates a persisted scaffold; use `update workflow` for subsequent changes rather than creating it again. Keep the graph schema, node kinds, edges, and embedded data references aligned with the live reference.

Use the live workflow docs when the graph shape is unclear:
```
archastro describe workflowdocs
```

If a command is missing, verify the CLI version and upgrade through the installation route before continuing.

### Available node types

Do not hard-code a node taxonomy in this skill. The supported graph/node model is owned by the workflow implementation and `archastro describe workflowdocs`.

**Phase 4: Write supporting scripts**

If the workflow needs script logic, author and validate that script first. Route to the `build-script` skill for detailed script authoring guidance, or get the reference directly:
```
archastro describe scriptdocs
archastro describe configsample Script
```

**Phase 5: Validate**

Validate the workflow graph through the dedicated workflow command:
```
archastro validate workflow --file ./workflows/my-workflow.json
```

Validate any referenced scripts:
```
archastro validate script --file ./scripts/my-script.agentscript
```

Fix any validation errors before deploying.

**Phase 6: Deploy**

The scaffold already exists from Phase 2. Persist the validated changes with an update:
```
archastro update workflow my-workflow --file ./workflows/my-workflow.json
```

For a config-managed repository, use the `manage-configs` deploy flow instead of creating duplicate standalone resources.

**Phase 7: Attach to a routine**

Workflows can run directly or through agent routines and automations. For an agent routine, get `configId` from `archastro describe workflow <id> --output json`, then create or update the routine to use it:

For a **scheduled** routine (cron):
```
archastro create agentroutine --agent <agent-id> \
  --name "Daily report" \
  --event-type schedule.cron \
  --schedule "0 9 * * *" \
  --handler-type workflow_graph \
  --config <workflow-config-id>
```

For a **webhook-triggered** routine, discover its real event name with `list events` and `describe event`. Generic webhook events use the `webhook.external` envelope; provider integrations have their own event families. Select the actual event and scope its filters before creating the routine:
```
archastro create agentroutine --agent <agent-id> \
  --name "Inbound webhook handler" \
  --event-type <discovered-webhook-event> \
  --handler-type workflow_graph \
  --config <workflow-config-id>
```

To update an existing routine to use a workflow:
```
archastro update agentroutine <routine-id> \
  --handler-type workflow_graph \
  --config <workflow-config-id>
```

**Phase 8: Test, activate, and monitor**

Execute a graph with representative input before attaching live triggers:

```
archastro run workflow --file ./workflows/my-workflow.json --payload '{"example":true}'
```

This executes on the platform and can perform real side effects. Use test inputs and explicit test integrations. A direct workflow run verifies graph behavior; it does not prove the routine's event binding.

Routine creation defaults to draft. When the user intends the schedule or event handler to go live:

```
archastro activate agentroutine <routine-id>
```

Then exercise the intended event or schedule and inspect the resulting run:
```
archastro list agentroutineruns --routine <routine-id>
archastro describe agentroutinerun <run-id>
archastro describe agentroutinerun <run-id> --journal
```

Use `println()` in scripts for debugging output.

### User wants to edit an existing workflow

1. **Inspect the current workflow**:
   ```
   archastro list workflows
   archastro describe workflow <id>
   ```

2. **Edit locally**, then validate and update:
   ```
   archastro validate workflow --file ./workflows/my-workflow.json
   archastro update workflow <id> --file ./workflows/my-workflow.json
   ```

   The workflow resource versions on update; the agent picks up the linked workflow config on the next run.

### User wants to set up a simple scheduled routine (no workflow)

Not everything needs a full workflow graph. For simple scheduled tasks, a routine can use a script directly.

**Reference a script resource** (preferred for production):
```
archastro create script --id daily-check --file ./scripts/daily-check.agentscript
archastro create agentroutine --agent <agent-id> \
  --name "Daily check" \
  --event-type schedule.cron \
  --schedule "0 9 * * *" \
  --handler-type script \
  --config <script-config-id>
```
Get the config ID from `archastro describe script daily-check --output json` (the `configId` field).

**Or inline for quick prototyping:**
```
archastro create agentroutine --agent <agent-id> \
  --name "Daily check" \
  --event-type schedule.cron \
  --schedule "0 9 * * *" \
  --handler-type script \
  --script 'println("hello")'
```

Or include the routine in the AgentTemplate:
```yaml
routines:
  - name: daily-check
    event_type: schedule.cron
    schedule: "0 9 * * *"
    handler_type: script
    config_ref: daily-check-script
```

Confirm the requested time and timezone before choosing cron. These routine/automation cron commands do not expose a timezone flag; do not assume the coding agent's local timezone applies or confuse them with separate agent schedules that may carry timezone state. Verify the actual scheduled timestamp/run against the requested wall-clock time, including daylight-saving requirements.

**Important**: Scheduled routines need both `schedule` and `event_type: schedule.cron`. Do not put schedules under nested `event_config.schedule`.

## Other routine handlers and event selection

Use `archastro create agentroutine --help` for the supported handler contract. A routine can run a script, workflow graph, built-in preset, or linear chain. Presets include `do_task`, `send_message`, `participate`, `triage`, and `auto_memory_capture`; choose a preset when the task needs agent reasoning and tools. `--preset-instructions`, model selection, and session settings configure the supported preset.

A chain (`--handler-type chain --steps '<JSON>'`) combines named script, workflow, and stateless `do_task`/`send_message` steps. Read the CLI's full step schema before authoring: runtime step references use `config`, while portable templates resolve config refs. Chain scripts and workflows receive `{trigger, inputs}`; read `$.trigger` for the original event and `$.inputs.<step_name>` for upstream output.

For event-driven work, use `--event-filter` to scope events, `--event-dedupe-key-path` for event identity, and `--event-cue` for text matching when supported. Use either convenience flags or `--event-config` JSON, never both. Inspect `describe event` before selecting fields; do not assume all events share a payload shape.

## Automations: run workflows without an agent routine

Choose an automation when a workflow itself is the scheduled, event-triggered, or explicitly invoked unit. First validate the graph, persist it, and get its `configId` with `describe workflow`. Then create the matching automation:

```
archastro create automation --name "Daily report" --type scheduled --schedule "0 9 * * *" --config <workflow-config-id>
archastro create automation --name "Event handler" --type trigger --trigger <discovered-event-name> --config <workflow-config-id>
archastro create automation --name "On-demand report" --type invoked --invoke-auth user --config <workflow-config-id>
```

These are alternatives, not three required resources. Choose execution identity deliberately with `--run-as-user` or `--run-as-agent` when needed; they are mutually exclusive. For reusable declarative definitions, inspect `describe configsample AutomationTemplate` and use `create automation --template <template-id-or-key>`. Invoked automations can validate payloads with `--input-schema-config` and lock input/participant values with `--prefills`; inspect their help before configuring them.

Inspect the created resource and activate when it should run. To switch to another workflow config, update the reference, then verify the next execution:

```
archastro describe automation <automation-id>
archastro update automation <automation-id> --config <workflow-config-id>
archastro activate automation <automation-id>
archastro invoke automation <invoked-automation-id> --payload '{"example":true}' --wait
archastro list automationruns --automation <automation-id>
archastro describe automationrun <run-id>
archastro describe automationrun <run-id> --journal
```

`invoke automation` is for the invoked type. For scheduled or triggered automations, exercise their actual schedule/event and inspect the resulting run. `--idempotency-key` can deduplicate an invocation; `--participants` supplies named agent participants required by the graph. Runs execute real work. Confirm terminal status and the intended output, not only acceptance. To stop future activation:

```
archastro pause automation <automation-id>
```

## Generic inbound webhooks and delivery proof

A webhook resource configures inbound delivery and signature verification; it is distinct from an integration provider or an automation. For generic delivery use a lookup key; for provider-specific delivery use `--provider github` or `--provider slack`. `--provider` and `--lookup-key` are mutually exclusive, and both modes require a signing secret.

```
archastro create webhook --lookup-key <webhook-key> --signing-secret <signing-secret>
archastro describe webhook <webhook-id>
archastro list webhookevents --webhook <webhook-id>
```

Use the returned/configured endpoint with the sender and its documented signing protocol. Keep the secret out of committed files and reports. Add `--provision-context-source` only when a webhook/inbound context source is needed. Delivery alone does not create a workflow trigger: discover the actual event envelope with `list events`/`describe event`, attach the routine or automation to that event, and verify both the recorded webhook event and the resulting run. Do not substitute an OAuth provider credential for the webhook signing secret.

## Preset discovery and schedule observability

Before choosing a routine preset, run `archastro list agentroutinepresets` for its allowed events, uniqueness, session, and chain constraints. Then use `create agentroutine --help` for its configuration fields.

For a scheduled routine, inspect `describe agentroutine` for the cron and status, then look for its actual `agentroutineruns`. Agent schedule resources are a separate surface; when the agent uses them, inspect their state directly:

```
archastro list agentschedules --agent <agent-id>
archastro describe agentschedule <schedule-id> --agent <agent-id>
```

For a scheduled automation, inspect `describe automation` and `list automationruns --automation <id>`. A visible cron or active status is configuration evidence, not proof that an execution completed.

## Workflow Design Best Practices

- **Start simple**: Begin with a linear flow, add branching only when needed.
- **Name nodes clearly**: Use descriptive IDs (`fetch_orders`, `check_status`) not generic ones (`step1`, `step2`).
- **Handle errors**: Follow the real graph schema from `workflowdocs` and the sample config. Don't assume every HTTP call succeeds.
- **Use scripts for logic**: Keep business logic in Script resources or embedded workflow script data instead of improvising unsupported fields.
- **Test scripts independently**: Use `archastro run script --file <path>` to test scripts before wiring them into a workflow.
- **Cron syntax**: Standard 5-field cron. Use https://crontab.guru for help.

## Recovery Rules

- If workflow validation fails, show the exact error — it usually points to a specific node or field.
- If a routine run fails, check `archastro list agentroutineruns` for the error details.
- If a workflow depends on script logic that does not exist yet, create and validate that script first.
- If the user is unsure about workflow vs. simple routine, ask how many steps the process has. One step = simple routine. Multiple steps with branching = workflow.

## Response Rules

- Do not inspect or edit credential files directly — use the CLI only.
- Do not ask the user to pick raw subcommands when intent is clear.
- Keep responses concise and operational.
- When authoring workflows, show the user a concrete JSON graph draft they can review.
- Prefer showing the full workflow structure over explaining node types abstractly.

### Rotate a webhook automation's signing secret

Team-owned webhook Automations have their own signing secret, separate from a
provider/generic `webhooks` record. Inspect the automation and command contract:

```sh
archastro describe automation <automation-id> --json
archastro refresh automation-webhook-secret --help
```

This command requires organization authentication for the owning team. Use the intended org session, and preserve unrelated profile settings.

For a requested rotation, run `archastro refresh automation-webhook-secret <automation-id>`.
Treat the returned signing material as a secret, update the authorized sender's
configuration, and verify a signed delivery produces the intended automation run.
Do not rotate merely to diagnose an unrelated run failure; replacing a provider
webhook record does not rotate this automation-specific secret.
