---
targets:
  claude-skill: manage-solutions
  codex-skill: manage-solutions
skill:
  name: manage-solutions
  description: Find and install ArchAstro starter samples; scaffold, validate, lint, package, import, install, and upgrade reusable Solutions containing agent, tool, routine, skill, or automation templates.
---

# Manage ArchAstro samples and Solutions

{{ASSUME_INSTALLED}}

## Select the workflow

1. **Run a starter agent:** discover catalog samples and install the requested sample.
2. **Reuse a Solution:** import its templates into the intended owner, then install
   the selected template to provision an agent/automation or attach capabilities.
3. **Author a bundle:** scaffold, edit, validate, lint, and package the local Solution.

Keep catalog import, runtime installation, and authoring separate. Import makes
templates available; it does not grant provider access or complete runtime setup.

## Install a starter sample

```bash
archastro list agentsamples
archastro install agentsample --help
archastro install agentsample <slug-or-slug@version>
```

The install fetches the release bundle and executes its declared deployment steps.
Review the chosen sample and intended app before installing. Capture the created
resources and follow their returned setup requirements.

## Import and install a Solution

Inspect the current command contracts and existing imports:

```bash
archastro list solutions
archastro import solution --help
archastro install solution --help
```

Import accepts a catalog slug/version, local checkout, or `.tar.gz` bundle:

```bash
archastro import solution <source>
archastro describe solution <solution-id-or-key>
```

Choose the intended `--org`, `--team`, or `--user` scope when required by the task.
Inspect available templates before installing a multi-template Solution:

```bash
archastro install solution <solution-id-or-key> --template <template-id-or-key>
```

Tool, routine, and skill templates require the intended `--target` agent.
Agent and automation templates provision their own runtime resources. Use returned
IDs and documented options instead of treating every Solution as an AgentTemplate.
`--allow-auto-import` can combine tenant adoption with installation; for developer
callers it must name the intended tenant using `--org`.

## Build and package a Solution

Use the public scaffold rather than handwritten bundle metadata:

```bash
archastro create solution --help
archastro create solution <slug> --target-dir <parent-directory>
archastro validate solution --help
archastro lint solution --help
archastro package solution --help
```

Edit the scaffolded `sample.yaml`, `solution.yaml`, templates, and README to describe
the actual job and setup. For config schemas use `describe configsample <Kind>`;
for scripts use `describe scriptdocs`. Keep dependencies and deployment order in
the bundle rather than requiring undocumented manual provisioning.

```bash
archastro validate solution <bundle-path> --schema-only
archastro validate solution <bundle-path>
archastro lint solution <bundle-path> --strict
archastro package solution <bundle-path> --output-dir <release-directory>
```

Schema-only validation is offline. Full validation includes the semantic script
sweep; do not describe a schema-only pass as equivalent. Packaging validates and
writes a versioned tarball; it does not publish a catalog release.

For a repository publishing multiple samples/Solutions, `archastro create solutionmanifest --help` describes generation of the catalog manifest from its `agents/` and `solutions/` directories. Generate it after the bundles are valid; do not hand-maintain a conflicting list of templates or versions.

## Upgrade existing imports

```bash
archastro upgrade solution --help
archastro upgrade solution <solution-id-or-key> <source> --dry-run
```

Review the diff against the requested version before applying the same upgrade
without `--dry-run`. Do not silently allow downgrades. Check the installed runtime
resources afterward; an updated imported Solution is not proof every previously
provisioned agent has already changed.

## Verify and report

For authoring, report schema/semantic validation, strict lint, and the package path.
For installation, inspect the created resource, tools/routines, and pending provider
connections; run the requested first task when authorized. Report the selected
version, owner, template, target, and outstanding setup. Do not claim that packaging
alone proves a live installation or external provider access.
