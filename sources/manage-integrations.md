---
targets:
  claude-skill: manage-integrations
  codex-skill: manage-integrations
skill:
  name: manage-integrations
  description: Connect ArchAstro agents to external services through personal OAuth, shared GitHub or Slack integrations, MCP providers, and private services; diagnose installation and Slack delivery issues.
---

# Manage ArchAstro integrations

{{ASSUME_INSTALLED}}

## Start with the connection model

Read the installed CLI's guide before choosing provider flags:

```bash
archastro help integrations
archastro create agentinstallation --help
```

An integration holds an external connection. An agent installation attaches a
capability to an agent. A standalone connection is not proof the agent can use it.
Identify the target agent, organization, provider, and intended account or workspace.
Inspect existing state before creating duplicate connections:

```bash
archastro list agentinstallations --agent <agent-id> --json
```

For an unfamiliar provider, discover current server-supported kinds and providers:

```bash
archastro list agentinstallationkinds
archastro list integrationproviders
archastro create integration --help
```

## Personal OAuth versus shared app bindings

1. **One agent's personal account:** create an `integration/*` installation,
   then follow its returned authorization and activation state. For example:

   ```bash
   archastro create agentinstallation --agent <agent-id> --kind integration/gmail
   archastro authorize agentinstallation <installation-id>
   archastro activate agentinstallation <installation-id>
   ```

2. **Shared organization GitHub App or Slack bot:** configure the shared integration
   with an authorized org administrator, then bind agents through `enablement/*`.
   Use the platform integration ID, not GitHub's numeric installation ID:

   ```bash
   archastro create agentinstallation --agent <agent-id> --kind enablement/github_app --shared-integration <integration-id>
   ```

3. A pending `configure_shared_integration` action means the shared connection is
   missing, inaccessible, or ambiguous. Inspect that connection; recreating the
   agent or substituting personal OAuth does not repair the binding.
4. When credentials were explicitly provided for a supported headless create flow,
   inspect the result before running OAuth again. An already active token-backed
   installation does not need browser authorization.

Keep tokens, refresh tokens, and enrollment material out of messages and files
intended for sharing. Do not read credential stores or change authentication scope
to bypass a permission failure.

## Stored credentials

Use `archastro list credentials --help` and `archastro create credential --help` only when the provider contract calls for a stored credential. Inspect metadata and ownership before attaching it to an integration. A credential record is not itself an agent installation; verify the connection and attachment separately. Prefer the provider's supported OAuth flow when no credential has been supplied, and never invent or expose credential values.

## MCP and private services

MCP provider keys identify remote MCP integrations, not native GitHub App installs.
Use `help integrations` and the discovered provider's required authentication model;
do not invent provider keys or assume every service needs MCP.

For a callable behind a private connector, inspect the supported create contracts:

```bash
archastro create privateservice --help
archastro create privateserviceenrollment --help
```

Private service definitions are immutable JSON function definitions. Enrollment is
a separate one-time connector credential. Create these only for the requested org
and actual connector setup; a definition alone does not establish connectivity.
Use the returned connector instructions rather than inventing an execution command.

## Slack routing and delivery

A bot installation and a channel binding solve different problems. Discover the
binding command before choosing its workspace, channel, team, and explicit agents:

```bash
archastro create slack-channel-binding --help
archastro assign slack-channel-binding --help
archastro list slack-delivery-outcomes --help
```

Creating a binding enrolls the allowed agents in the bound team. `assign` replaces
the channel's sole resident; do not use it as an additive operation. Shared channels
need a customer team binding, and private channels require in-channel evidence.
Preserve those requirements and existing conversation settings.

For a missing reply, inspect delivery outcomes for the channel and distinguish a
withheld reply from a failed provider call before changing configuration.

## Verify the requested outcome

Inspect the resulting installation and its next action. Confirm the intended
provider/account and attachment are active. If knowledge ingestion is involved,
also verify its source and results using the `manage-knowledge` skill. Report pending
OAuth, connector, or routing steps explicitly; creation alone is not completion.
