---
name: build-script
description: Use when the user wants to write, test, or deploy an ArchAstro script — custom logic for agent tools, workflow nodes, and routines. Trigger phrases include "build a script", "write a script", "create a script", "test a script", "script syntax", "script reference", "script language".
allowed-tools: ["Bash(archastro:*)"]
---

# ArchAstro Script Builder

Write, test, and deploy scripts — custom logic that powers agent tools, workflow nodes, and routines.

This skill assumes the ArchAstro CLI is already installed and authenticated. Install or upgrade `archastro` if missing, and run `archastro auth login` if not authenticated.

## What is a Script?

Scripts are expression-oriented custom logic written in the ArchAstro script language. They can be used as:
- **Custom tool handlers**: Agent calls a tool → script runs → result returned to agent
- **Workflow graph script steps**: Script logic used inside a workflow graph
- **Routine handlers**: A scheduled routine runs the script directly

Scripts are first-class resources with their own CRUD, validation, and execution commands.
Use the dedicated top-level script resource for the normal authoring loop: `archastro list scripts`, `describe script`, `create script`, `update script`, `validate script`, `run script`, and `describe scriptdocs`.

## Always Start with State

Every invocation must begin by understanding the current context:

```
archastro auth status
archastro list scripts
```

Determine:
- Is the user creating a new script or editing an existing one?
- What will this script be used for? (tool, workflow node, routine)
- What external APIs or data does it need to access?

## Routing

### CLI not installed or too old

Before any script work, verify the CLI:

- Read `plugin-compatibility.json` from the plugin root.
- Prefer `plugins.archastro.minimumCliVersion`, fall back to the top-level `minimumCliVersion`.
- Run `archastro --version`. If missing or older than the resolved minimum, instruct the user to install or upgrade `archastro`.
- If authentication or app selection is missing, instruct the user to run `archastro auth login`.

### User wants to write a new script

**Phase 1: Get the language reference**

Always start by fetching the live reference — do not write scripts from memory:
```
archastro describe scriptdocs
```

Use the top-level script commands, not `describe configsample`/`validate config`, for the normal authoring loop.

Create a script from a local source file:
```
archastro create script --id my-script --file ./scripts/my-script.agentscript
```

Or let the CLI start from its built-in sample if you do not pass `--source` or `--file`:
```
archastro create script --id my-script
```

**Phase 2: Understand the requirements**

Ask the user:
- What should the script do?
- What inputs will it receive? (accessible via `$` JSONPath)
- Does it need environment variables? (accessible via `env.KEY`)
- Does it need to make HTTP calls?

If the script will handle a routine event, discover what `$` contains by checking the event's payload schema:
```
archastro list events
archastro describe event <event-name>
```

`describe event` returns the JSON schema and a sample payload. Every field in the payload is accessible via `$` in the script (e.g., `$.thread_id`, `$.message.content`). Always check the event schema before writing scripts that consume routine payloads — do not guess the shape from memory.

**Phase 3: Author the script**

Key language concepts:

- **Input**: Access via `$` (JSONPath). E.g., `$.order_id`, `$.user.email`
- **Environment**: Access via `env.KEY`. E.g., `env.API_TOKEN`
- **Imports**: `import("requests")`, `import("array")`, `import("string")`, etc.
- **Error handling**: `unwrap(result)` or `unwrap(result, default_value)`
- **No loops**: Use `array.map`, `array.filter`, `array.reduce`
- **Expression-oriented**: The last expression in the script is the return value
- **Debugging**: Use `println()` to inspect values

Example — HTTP lookup script:
```
let http = import("requests")
let arr = import("array")

let response = http.get(env.API_URL + "/orders/" + $.order_id, {
  headers: { "Authorization": "Bearer " + env.API_TOKEN }
})
let body = unwrap(response).body

{
  order_id: $.order_id,
  status: body.status,
  items: arr.map(body.line_items, fn(item) {
    { name: item.name, qty: item.quantity }
  })
}
```

Available namespaces:
- `requests` — HTTP client (`get`, `post`, `put`, `patch`, `delete`)
- `array` — Collection operations (`map`, `filter`, `reduce`, `find`, `flat`)
- `string` — String operations (`split`, `trim`, `lowercase`, `uppercase`, `includes`)
- `map` — Object operations (`keys`, `values`, `merge`, `get`)
- `datetime` — Date/time operations (`now`, `format`, `parse`, `add`)
- `math` — Math operations (`round`, `floor`, `ceil`, `abs`)
- `result` — Result type operations (`ok`, `err`, `isOk`, `isErr`)
- `email` — Email sending
- `jwt` — JWT token operations
- `slack` — Slack API operations

**Phase 4: Validate**

Validate the script syntax:
```
archastro validate script --file ./scripts/my-script.agentscript
```

Or validate as a config:
```
archastro validate config -k Script -f ./configs/scripts/my-script.yaml
```

Fix any validation errors before proceeding.

**Phase 5: Test**

Execute the local source on the platform with test input (this is not an offline sandbox; external calls and writes are real):
```
archastro run script --file ./scripts/my-script.agentscript --input '{"order_id": "ORD-123"}'
```

For scripts that need env vars, ensure they are set on the platform:
```
archastro list orgenvvars
archastro create orgenvvar -k API_TOKEN -v "sk-..."
```

**Phase 6: Deploy**

Scripts can be deployed two ways:

**As a standalone script resource:**
```
archastro create script --id order-lookup -n "Order Lookup" --file ./scripts/my-script.agentscript
```

Update an existing script resource:
```
archastro update script order-lookup --file ./scripts/my-script.agentscript
```

**Via `deploy configs`** (for config-managed repos):

Place `.agentscript` files in `configs/scripts/` and deploy:
```
archastro deploy configs
```

Production sources can use `.aascript` or `.agentscript`. Test sources use `.test.aascript` or `.test.agentscript` and deploy as `ScriptTest`; structured YAML/JSON wrappers use the matching config kind. See the `manage-configs` skill for setting up the configs directory.

**Phase 7: Wire it up**

Connect the script to where it will be used:

**As a custom tool on an agent:**

The API requires `--config` pointing at the script's config ID even for script-handler tools:
```
archastro create agenttool --agent <agent-id> \
  --kind custom \
  --name "lookup_order" \
  --description "Look up an order by ID" \
  --handler-type script \
  --config <script-config-id> \
  --instruction "Use this tool when the user asks to look up an order." \
  --parameters '{"type":"object","properties":{"order_id":{"type":"string"}},"required":["order_id"]}'
```

Get the script's config ID from `archastro describe script <id> --output json` (the `configId` field).

**In a workflow graph:** Follow the real `WorkflowGraph` shape from `archastro describe workflowdocs` and the `build-workflow` skill.

**As a routine handler** (reference by config ID — preferred for production):
```
archastro create agentroutine --agent <agent-id> \
  --name "My scheduled script" \
  --event-type schedule.cron \
  --schedule "0 9 * * 1-5" \
  --handler-type script \
  --config <script-config-id>
```

Get the script's config ID from `archastro describe script <id> --output json` (the `configId` field).

Or inline for quick prototyping:
```
archastro create agentroutine --agent <agent-id> \
  --name "Quick test" \
  --event-type schedule.cron \
  --schedule "0 9 * * 1-5" \
  --handler-type script \
  --script 'println("hello")'
```

Prefer `--config` for production — it keeps the routine linked to a versioned script resource that can be updated independently.

### Repeatable script tests and execution context

Use ScriptTest for assertions, not only successful execution:

```
archastro test script --file configs/scripts/order-lookup.test.aascript
archastro test script order-lookup-tests
archastro test scripts
```

Read `archastro test script --help` and `archastro describe scriptdocs` before authoring. The `test` namespace provides `describe`, `it`, `expect`, hooks, `mock`, `spy`, and `withInput`. Mock side-effecting namespace calls explicitly: tests do not automatically isolate network or storage. Inside a configs project, `test script --file` overlays local script imports before deployed sources. Import shared script modules with `import("script:<lookup_key>")`.

Consult the live reference for optional type annotations, `input` declarations, structured logging, and storage. For custom tools, `$` contains tool arguments; `threads.current()` accesses the calling thread when available. Single-handler routines receive the event at `$`. Chain steps receive `{trigger, inputs}`, so use `$.trigger.<field>` and `$.inputs.<step_name>`.

For deployed routines, activate when ready and verify an actual run:

```
archastro activate agentroutine <routine-id>
archastro list agentroutineruns --routine <routine-id>
archastro describe agentroutinerun <run-id>
```

Routine creation defaults to draft. Creating its script does not activate it.

### User wants to edit an existing script

1. **Inspect the current script**:
   ```
   archastro list scripts
   archastro describe script <id>
   ```

2. **Edit locally**, validate, and update:
   ```
   archastro validate script --file ./scripts/my-script.agentscript
   archastro update script <id> --file ./scripts/my-script.agentscript
   ```

## Common Mistakes

**Object keys may be unquoted identifiers or quoted strings.** Both `{ status: "ok" }` and `{ "status": "ok" }` are valid.

**Do not use `return` — the last expression is the return value:**
```
// WRONG
return { status: "ok" }

// CORRECT
{ status: "ok" }
```

**Built-in namespaces support direct calls**, such as `array.map(...)` and `string.uppercase(...)`. Import bindings are also supported; use `import("requests")` for HTTP and consult the live reference for app-specific namespaces.

**No imperative loops — use array functions:**
```
// WRONG — for/while don't exist
for item in items { ... }

// CORRECT
let arr = import("array")
arr.map(items, fn(item) { ... })
```

## Script Authoring Rules

- **Always fetch `archastro describe scriptdocs` before writing scripts.** Do not invent syntax from memory.
- Prefer the dedicated top-level script commands over the generic `configs` resource unless the user explicitly wants config-managed files.
- Treat the language as functional and expression-oriented, not imperative.
- The last expression is the return value — there is no `return` keyword.
- Use `unwrap()` for error handling — never assume HTTP calls succeed.
- Use `println()` liberally while debugging, remove before deploying.
- If validation fails, rewrite toward the sample/reference instead of trial-and-error.

## Recovery Rules

- If a script fails validation, show the exact error. Common issues: missing imports, wrong function signatures, trying to use imperative loops.
- If `archastro run script` fails at runtime, check: are env vars set? Is the input JSON valid? Is the API reachable?
- If the user is unsure about syntax, always fall back to `archastro describe scriptdocs`.

## Response Rules

- Do not inspect or edit credential files directly — use the CLI only.
- Do not ask the user to pick raw subcommands when intent is clear.
- Keep responses concise and operational.
- Show the user a concrete script draft they can review, not abstract syntax explanations.
