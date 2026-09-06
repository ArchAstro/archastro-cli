---
name: manage-platform
description: Manage an ArchAstro developer app, customer organizations, users, teams, access keys, OAuth registrations, domains, sandboxes, secrets, custom objects, files, and artifacts. Use for app administration, customer onboarding, environment selection, or platform data management.
allowed-tools: ["Bash(archastro:*)"]
---

# Manage an ArchAstro App and Its Customers

Use this guide for platform administration and data management. For connecting an agent to a provider, use the `manage-integrations` skill; for agent knowledge ingestion, use the `manage-knowledge` skill.

Install or upgrade `archastro` if missing, and run `archastro auth login` if not authenticated.

## Establish the app, identity, and environment

```sh
archastro auth status
archastro describe me
archastro settings get
archastro help concepts
```

Preserve the selected profile, app, server, and sandbox. App selection and customer ownership are different: `--app` selects the application, while `--org`, `--team`, or `--user` select the relevant tenant or owner on commands that expose those flags. Developer-only commands are public platform features, but require developer authorization; do not treat an organization-user 403 as a reason to broaden access.

- For a new project, inspect `archastro init --help` before running init. Init authenticates and configures the local project; it is not required merely to inspect help.
- For another account/environment, use `archastro help profiles`, `archastro list profiles`, and `archastro describe profile`. Keep `--profile <name>` on related calls. Creating a profile does not activate it.
- Discover known resource flags with `archastro <verb> <resource> --help`. Use `archastro resources` only when the resource/verb is unknown. Use `--output json` for machine-readable resource responses and follow the resource's pagination options; a page is not necessarily the complete result set.
- App creation is not a CLI resource in this release. Use the developer portal for creating an app, then `archastro list apps`, `archastro describe app <id>`, or `--app <id>` for selection.

## Customer organizations and members

Model customer boundaries explicitly: an app contains organizations; users and teams represent identities and collaboration within the intended customer. Do not create an organization or system user for every operation.

```sh
archastro list orgs --help
archastro create org --help
archastro create user --help
archastro create team --help
archastro create teammember --help
```

1. Find the existing customer organization and users first. Organization-user searches require the documented search term; developers have a broader listing surface.
2. Create or update the requested organization and human users. `create user --org <id> --org-role <role>` assigns a user to that organization. Use the role the user requested, not an automatic admin role.
3. Create a team in the correct organization when the collaboration needs one, then manage `teammembers`. Team membership is separate from thread membership; use the `chat` skill for conversations.
4. Describe the resulting records and list members to verify the intended customer/role/ownership outcome.

App collaborators use `appmembers` and `appinvites`; these are different from customer users/team members. Inspect `list appmembers`, `list appinvites`, and their create/update/revoke/refresh help before changing developer access. `create userportalsession --help` exposes temporary customer portal access; treat the returned auto-login URL as a credential.

## Keys, tokens, OAuth, and domains

Choose the credential for the actor that needs access:

- `appkeys` are publishable or secret application keys; `sandboxkeys` belong to a sandbox.
- `usertokens` represent a human or system user. `create user --system-user` creates a non-login identity; mint a token for that identity only when the integration needs it. Check `create usertoken --help` for scopes and expiration choices.
- `appoauthproviders` configure app sign-in providers; `appoauthclients` register OAuth clients. These differ from `integrations`/`credentials`, which connect agents/users to external providers.
- `appdomains` manage verified domains; `appdomainreplyaddresses` manage their reply-address local parts. Describe a domain for DNS instructions, apply DNS through the user's chosen provider, then use the documented validate/refresh operation to check verification.

Inspect the precise create/update/revoke help, perform the requested change, and verify metadata/status. Do not echo secret keys, token values, or auto-login URLs into shared reports or source files. Revocation and access changes should target the exact requested identity/key; keep unrelated access intact.

## Sandboxes and environment variables

```sh
archastro list sandboxes
archastro describe sandbox <id>
archastro activate sandbox --help
archastro activate production --help
```

A CLI profile isolates local credentials/settings; a sandbox selects an app environment. Check both before running changes. Create a sandbox if the user requests a new environment, activate the intended one, and verify state with `auth status`/`settings get`. Returning to production changes the target of subsequent commands, so do so only as part of the requested environment switch.

- Use `sandboxmails` to inspect captured sandbox emails and `sandboxkeys` for sandbox credentials.
- `appenvvars`, `orgenvvars`, and `agentenvvars` have distinct ownership. Inspect their help and choose the narrowest owner that matches the requirement.
- Config secrets use `archastro create config-secret --help` and the `secret_value!` representation returned by the CLI. The command takes plaintext as an argument; do not invent a stdin/file option or write plaintext into tracked YAML. Use the user's approved secret-handling method.
- For config-backed resources, use the `manage-configs` skill so local files and deployed versions stay coherent.

## Custom data, files, and artifacts

Custom objects are schema-backed structured records, files are uploaded content, and artifacts are named/versioned deliverables with ownership and optional thread/agent relationships.

```sh
archastro describe configsample CustomObjectSchema
archastro create custom-object --help
archastro list custom-objects --help
archastro create file --help
archastro create artifact --help
archastro download artifact --help
```

- Deploy a `CustomObjectSchema` config before creating records that use its `--schema-key` or `--config`. `--fields` supplies JSON, and `--team`/`--user` selects ownership. Read the schema before updating fields; don't replace an entire record when a targeted update suffices.
- Files accept `--data-file <path>` (or `-` for stdin), or base64 `--data`. A file's `--share` makes supported image content publicly fetchable through a durable URL; use it only when public sharing is part of the request.
- Artifact creation uses `--file-data` base64 plus metadata, not the file resource's `--data-file` flag. Inspect `update artifact --help` for revisions, and `archive`/`download` for lifecycle operations.
- Describe the created/updated resource, verify owner and content metadata, and return its ID and requested access URL. Preserve privacy across customer and team boundaries.

## Events and webhooks

For event-triggered work, inspect `list events` and `describe event <name>` to get the payload contract. `webhooks` and `webhookevents` configure and inspect incoming provider/generic events; automation webhook signing secrets are a separate resource. Use the `build-workflow` skill to connect an event to an automation, and the `manage-integrations` skill for provider authorization. Do not substitute a guessed event name or signature scheme for the current reference.
