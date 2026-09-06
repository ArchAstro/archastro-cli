# Core skill coverage

Audited 2026-09-06 against the public **ArchAstro CLI 0.61.0** release, its
`resources` and `--help` output, maintained CLI topic guides, and implementation
in `ArchAstro/firstlanding/src/ts/developer-platform-cli`. This is a coverage map,
not a claim that every backend/provider workflow was executed.

The skills teach user workflows and route exact field/schema questions to the
installed CLI. Resource groups below cover the public developer and organization
surfaces; developer-only does not mean private/internal. ArchDev Factory/daemon
internals are outside this collection.

| Skill | Core workflow | Resource inventory |
|---|---|---|
| [archastro-install](skills/archastro-install/SKILL.md) | CLI installation and upgrades | Standalone CLI commands |
| [archastro-auth](skills/archastro-auth/SKILL.md) | Identity, app selection, profiles and browser/headless login | `me`, `profiles`, `apps` |
| [archastro-manage-configs](skills/archastro-manage-configs/SKILL.md) | Owner-pinned config lifecycle and project hooks | `configdir`, `configdirs`, `configeditor`, `configkinds`, `configmanifest`, `configpath`, `configs`, `configsamples`, `systemconfigs` |
| [archastro-author-agent](skills/archastro-author-agent/SKILL.md) | Agent templates, models, tools, output schemas and environment | `aimodels`, `agenttools`, `agenttoolkinds`, `agentenvvars` |
| [archastro-build-script](skills/archastro-build-script/SKILL.md) | Script authoring, execution, modules and tests | `script`, `scripts`, `scriptdocs` |
| [archastro-build-workflow](skills/archastro-build-workflow/SKILL.md) | Graphs, routines, automations, event triggers and runs | `workflowdocs`, `workflows`, `automations`, `automationruns`, `agentroutines`, `agentroutinepresets`, `agentroutineruns`, `agentschedules`, `events`, `automation-webhook-secret` |
| [archastro-build-skill](skills/archastro-build-skill/SKILL.md) | Platform skills, files and agent attachments | `skills`, `skillfiles`, `agentskills` |
| [archastro-deploy-agent](skills/archastro-deploy-agent/SKILL.md) | Provisioning agents, upgrades and export | `agent`, `agents` |
| [archastro-chat](skills/archastro-chat/SKILL.md) | Threads, membership, messages and multi-turn sessions | `threads`, `threadmembers`, `threadmessages`, `agentsessions` |
| [archastro-impersonate](skills/archastro-impersonate/SKILL.md) | Local embed identity, tools and linked skills | Standalone CLI commands |
| [archastro-manage-integrations](skills/archastro-manage-integrations/SKILL.md) | Provider OAuth, shared integrations, Slack, MCP and private services | `integrations`, `integrationproviders`, `credentials`, `agentinstallationkinds`, `agentinstallations`, `privateservices`, `privateserviceenrollments`, `slack-channel-bindings`, `slack-delivery-outcomes` |
| [archastro-manage-knowledge](skills/archastro-manage-knowledge/SKILL.md) | Sources, ingestion, retrieval and document maintenance | `knowledgesourcekinds`, `knowledgesources`, `agentinstallationsources`, `knowledgeingestions`, `knowledgeitems`, `knowledgedocuments` |
| [archastro-manage-solutions](skills/archastro-manage-solutions/SKILL.md) | Samples, bundle validation, packaging, import, install and upgrade | `agentsamples`, `solutions`, `solutionmanifest` |
| [archastro-operate-agents](skills/archastro-operate-agents/SKILL.md) | Readiness, run diagnostics, memory, computers and human review | `agenthealthactions`, `agentcomputers`, `agentworkingmemories`, `activityfeed`, `manualreviewitems`, `notification`, `notifications` |
| [archastro-manage-work](skills/archastro-manage-work/SKILL.md) | Tasks, dependencies, leases, AstroDev, Astrorun and images | `tasks`, `task-activity`, `task-blockers`, `task-blocking`, `task-comments`, `task-cycles`, `task-leases`, `task-subtasks`, `workitems`, `embeddingcomparison` |
| [archastro-manage-platform](skills/archastro-manage-platform/SKILL.md) | Customer administration, access, environments, data and files | `orgs`, `users`, `teams`, `teammembers`, `appmembers`, `appinvites`, `appkeys`, `appoauthclients`, `appoauthproviders`, `appdomains`, `appdomainreplyaddresses`, `appenvvars`, `orgenvvars`, `sandboxes`, `sandboxkeys`, `sandboxmails`, `production`, `usertokens`, `userportalsessions`, `config-secret`, `custom-objects`, `files`, `artifacts`, `webhooks`, `webhookevents` |

## Audit result

- 98 public resource families map to 16 task skills; six domain skills were added.
- Fixed removed embed commands, renamed CLI flags, config editor/deployment ownership,
  script response handling and syntax claims, routine activation, and existing-agent
  upgrade sequencing. Added explicit provider/knowledge, Solutions, operations, work,
  and platform administration flows.
- Offline verification passed for 295 documented examples across 165 command/help
  paths, plus the resource coverage check, both npx installation proofs, 105 existing
  repository tests, all 16 skill frontmatters, and generator/repository checks.
- Independent coverage review and four cross-skill forward scenarios passed after
  corrections. Those scenarios were offline instruction walkthroughs, not live
  execution tests.

## Verification and remaining boundaries

- `scripts/test_portable_skills.py` is the canonical packaging proof. Its single-task
  test crosses the real npx installer boundary and verifies a deployment skill's
  required references. Its whole-catalog test verifies every skill's installed
  payload for Codex and Claude. It does not execute backend operations.
- `scripts/test_skill_commands.py` checks documented command paths and flags against
  a real release binary using offline help only. CI installs the minimum supported
  release for this check. This catches removed commands and renamed options without
  logging in or creating resources.
- The compatibility contract now requires 0.61.0. For a release upgrade, review this
  map against `archastro resources`, update affected workflows, then regenerate and
  run both checks. An inventory match is necessary coverage evidence, not proof of
  semantic completeness.
- The separate cold-install proof successfully installed and ran public Darwin ARM64
  CLI 0.61.0 with no preinstalled CLI. Provider OAuth, live deployments, script and
  workflow execution, customer mutations, and Windows/Linux runtime journeys have
  not been executed in this audit. Their guides require explicit outcome checks;
  future integration runs should exercise them in disposable authorized environments.
- The installed skill named `archastro-impersonate` remains for compatibility but
  documents the current `archastro embed` command. It does not invoke the removed
  `archastro impersonate` command.
