#!/usr/bin/env python3
"""
Generate portable skills plus Claude Code and Codex plugins from sources/.

Every skill source also produces skills/archastro-<name>/ with a short entrypoint,
a task reference, and bundled bootstrap instructions and compatibility contract.
Edit sources/, not generated skill directories.

One source file per concept in sources/<name>.md. Each source declares its
output targets (claude-skill, claude-command, codex-skill) via the `targets:`
frontmatter field. The script applies harness-specific substitutions and
conditional blocks, then writes to the declared output paths.

USAGE
    python3 scripts/generate-plugin-content.py           # write outputs
    python3 scripts/generate-plugin-content.py --check   # diff against committed, exit 1 if different

SOURCE FILE FORMAT
    ---
    targets:
      claude-skill: <dirname>      # → .claude-plugins/archastro/skills/<dirname>/SKILL.md
      claude-command: <filename>   # → .claude-plugins/archastro/commands/<filename>
      codex-skill: <dirname>       # → plugins/archastro/skills/<dirname>/SKILL.md
    skill:                         # frontmatter used for any skill target
      name: <name>                 # must match <dirname>
      description: <description>   # natural-language trigger phrases
      allowed-tools: [...]
    command:                       # frontmatter used for claude-command targets
      description: <description>
      allowed-tools: [...]
    ---

    # Body

    Body content with {{SUBSTITUTION}} placeholders and conditional blocks.

SUBSTITUTIONS (resolved per target harness)
    {{HARNESS_NAME}}       "Claude Code" | "Codex"
    {{SESSION}}            "Claude Code session" | "Codex session"
    {{ASSUME_INSTALLED}}   harness-specific CLI install reminder paragraph
    {{INSTALL_ROUTE}}      "direct the user to `/archastro:install`" |
                           "instruct the user to install or upgrade `archastro`"
    {{AUTH_ROUTE}}         "direct the user to `/archastro:auth`" |
                           "instruct the user to run `archastro auth login`"
    {{AUTH_ROUTE_SHORT}}   "route to `/archastro:auth`" | "run `archastro auth login`"

CONDITIONAL BLOCKS (emit only for matching targets)
    {{#SKILL}} ... {{/SKILL}}                  any skill target (claude or codex)
    {{#CLAUDE_COMMAND}} ... {{/CLAUDE_COMMAND}} only claude-command targets

    Limitation: conditional blocks CANNOT nest. The non-greedy regex plus
    backreferenced close-tag means a pattern like
    `{{#A}}before {{#B}}inner{{/B}} after{{/A}}` would treat the outer `A`
    block as matching everything through `{{/A}}`, and the inner `{{#B}}`
    marker would leak into the substituted body as literal text. The
    generator detects unbalanced open/close marker counts and raises at
    generate time rather than silently producing wrong output.

DESIGN NOTE: ASYMMETRY BETWEEN INSTALL/AUTH AND OTHER CONCEPTS
    `install.md` and `auth.md` generate a claude-command + codex-skill, but
    intentionally do NOT generate a claude-skill.

    Why: install and auth are one-shot bootstrap actions. In Claude Code they
    are discovered via `/` autocomplete — a slash command is the right UX.
    Adding a claude-skill with the same name would create a naming collision
    with the claude-command in the Skill tool's dispatch table.

    In Codex there is no slash command concept (verified in
    https://developers.openai.com/codex/plugins/build), so skills are the only
    way to reach install/auth content via natural language. Codex gets a skill
    with trigger phrases; Claude Code gets a command and relies on autocomplete
    discovery.

    Impersonate is different: it has subcommands (start/status/sync/stop) and
    benefits from both explicit invocation (slash command) and conversational
    triggering. It generates claude-skill + claude-command + codex-skill.
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCES_DIR = REPO_ROOT / "sources"
CLAUDE_PLUGIN_ROOT = REPO_ROOT / ".claude-plugins" / "archastro"
CODEX_PLUGIN_ROOT = REPO_ROOT / "plugins" / "archastro"


TargetType = Literal["claude-skill", "claude-command", "codex-skill"]
Harness = Literal["claude", "codex", "portable"]


# Per-harness substitution maps. Keys are placeholders that appear in source
# bodies and frontmatter; values are the harness-specific rendered string.
SUBSTITUTIONS: dict[Harness, dict[str, str]] = {
    "portable": {
        "{{HARNESS_NAME}}": "your coding agent",
        "{{SESSION}}": "current coding-agent session",
        "{{ASSUME_INSTALLED}}": "First complete [bootstrap](bootstrap.md), then resume this task.",
        "{{INSTALL_ROUTE}}": "execute [installation](install.md), verify the version, then resume this task",
        "{{AUTH_ROUTE}}": "run `archastro auth login` and resume after browser authentication completes",
        "{{AUTH_ROUTE_SHORT}}": "run `archastro auth login`",
    },
    "claude": {
        "{{HARNESS_NAME}}": "Claude Code",
        "{{SESSION}}": "Claude Code session",
        "{{ASSUME_INSTALLED}}": (
            "Use the `/archastro:install` and `/archastro:auth` commands in "
            "this same plugin instead of trying to install or authenticate the "
            "CLI manually inside this skill."
        ),
        "{{INSTALL_ROUTE}}": "direct the user to `/archastro:install`",
        "{{AUTH_ROUTE}}": "direct the user to `/archastro:auth`",
        "{{AUTH_ROUTE_SHORT}}": "route to `/archastro:auth`",
    },
    "codex": {
        "{{HARNESS_NAME}}": "Codex",
        "{{SESSION}}": "Codex session",
        "{{ASSUME_INSTALLED}}": (
            "Install or upgrade `archastro` if missing, and run "
            "`archastro auth login` if not authenticated."
        ),
        "{{INSTALL_ROUTE}}": "instruct the user to install or upgrade `archastro`",
        "{{AUTH_ROUTE}}": "instruct the user to run `archastro auth login`",
        "{{AUTH_ROUTE_SHORT}}": "run `archastro auth login`",
    },
}


# Conditional block markers. A block is emitted only if its key is in the
# active set for the current target.
#   - claude-skill  → {"SKILL", "CLAUDE_SKILL"}
#   - codex-skill   → {"SKILL", "CODEX_SKILL"}
#   - claude-command → {"CLAUDE_COMMAND"}
CONDITIONAL_SETS: dict[str, set[str]] = {
    "claude-skill": {"SKILL", "CLAUDE_SKILL"},
    "codex-skill": {"SKILL", "CODEX_SKILL"},
    "claude-command": {"CLAUDE_COMMAND"},
    "portable-skill": {"SKILL", "PORTABLE_SKILL"},
}

CONDITIONAL_RE = re.compile(
    r"\{\{#(?P<key>[A-Z_]+)\}\}(?P<body>.*?)\{\{/(?P=key)\}\}",
    flags=re.DOTALL,
)


@dataclass
class Source:
    path: Path
    targets: dict[str, str]  # target_type → dirname or filename
    skill_frontmatter: dict | None
    command_frontmatter: dict | None
    body: str


def split_frontmatter(text: str) -> tuple[dict, str]:
    """Return (frontmatter_dict, body). Raises ValueError if missing."""
    if not text.startswith("---\n"):
        raise ValueError("no frontmatter block")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("unterminated frontmatter block")
    fm_raw = text[4:end]
    body = text[end + len("\n---\n"):]
    fm = yaml.safe_load(fm_raw)
    if not isinstance(fm, dict):
        raise ValueError("frontmatter is not a mapping")
    return fm, body


def load_source(path: Path) -> Source:
    text = path.read_text(encoding="utf-8")
    fm, body = split_frontmatter(text)
    targets = fm.get("targets") or {}
    if not targets or not isinstance(targets, dict):
        raise ValueError(f"{path}: missing or empty `targets` block")
    for t in targets:
        if t not in ("claude-skill", "claude-command", "codex-skill"):
            raise ValueError(f"{path}: unknown target type {t!r}")
    return Source(
        path=path,
        targets=targets,
        skill_frontmatter=fm.get("skill"),
        command_frontmatter=fm.get("command"),
        body=body,
    )


def apply_substitutions(text: str, harness: Harness) -> str:
    subs = SUBSTITUTIONS[harness]
    for placeholder, value in subs.items():
        text = text.replace(placeholder, value)
    return text


CONDITIONAL_OPEN_RE = re.compile(r"\{\{#[A-Z_]+\}\}")
CONDITIONAL_CLOSE_RE = re.compile(r"\{\{/[A-Z_]+\}\}")


def apply_conditionals(text: str, target: TargetType | Literal["portable-skill"]) -> str:
    """Expand {{#KEY}}...{{/KEY}} blocks, keeping only those matching target.

    Conditional blocks cannot nest. The non-greedy regex with a backreferenced
    close tag would mishandle nesting and silently leak inner markers into the
    output, so we detect unbalanced open/close marker counts up front and raise.

    A post-substitution check catches key-swapped pairs (e.g.
    {{#SKILL}}...{{/CLAUDE_COMMAND}}) where global counts balance but the
    backreference doesn't match, leaving raw markers in the output.
    """
    open_count = len(CONDITIONAL_OPEN_RE.findall(text))
    close_count = len(CONDITIONAL_CLOSE_RE.findall(text))
    if open_count != close_count:
        raise ValueError(
            f"unbalanced conditional markers in source: {open_count} open, "
            f"{close_count} close. Conditional blocks must be paired and "
            f"cannot nest."
        )

    active = CONDITIONAL_SETS[target]

    def replace(match: re.Match) -> str:
        key = match.group("key")
        inner = match.group("body")
        return inner if key in active else ""

    result = CONDITIONAL_RE.sub(replace, text)

    # Post-check: markers surviving substitution indicate mismatched keys
    # (e.g. {{#SKILL}}...{{/CLAUDE_COMMAND}} — balanced globally but the
    # backreference can't pair them).
    remaining = CONDITIONAL_OPEN_RE.findall(result) + CONDITIONAL_CLOSE_RE.findall(result)
    if remaining:
        raise ValueError(
            f"conditional markers survived substitution (likely mismatched "
            f"keys): {remaining}"
        )

    return result


def format_frontmatter(fm: dict) -> str:
    """
    Render frontmatter dict as a YAML block matching the Claude Code plugin
    convention: each key on its own line, string values as plain scalars (no
    quoting), lists as flow-style with double-quoted elements.

    This hand-rolled rendering is intentional — PyYAML's default dumper wraps
    long strings and escapes Unicode, producing output that differs from the
    committed files. The Claude Code and Codex harnesses both accept plain
    scalars for the descriptions we write, so no quoting is needed.

    The output is round-trip validated: the rendered block is re-parsed by
    yaml.safe_load and must equal the input dict. This catches any future
    description that contains YAML-hostile characters (leading `-`, ` : `,
    ` #`, etc.) at generate time, instead of letting the harness silently
    fail to parse the skill.
    """
    lines = ["---"]
    for key, value in fm.items():
        if isinstance(value, list):
            # Flow-style list with double-quoted string elements
            items = ", ".join(f'"{item}"' for item in value)
            lines.append(f"{key}: [{items}]")
        elif isinstance(value, str):
            # Plain scalar — no quoting. Validated by round-trip parse below.
            lines.append(f"{key}: {value}")
        else:
            lines.append(f"{key}: {value}")
    lines.append("---")
    rendered = "\n".join(lines) + "\n"

    # Round-trip validation: re-parse our hand-rolled YAML and assert it
    # matches the input dict. Any divergence means a frontmatter value
    # contained a YAML-hostile pattern that we silently corrupted.
    yaml_body = "\n".join(lines[1:-1])
    try:
        reparsed = yaml.safe_load(yaml_body)
    except yaml.YAMLError as e:
        raise ValueError(
            f"frontmatter round-trip failed: hand-rolled YAML did not parse. "
            f"A frontmatter value likely contains a YAML-hostile character "
            f"(leading `-`, ` : `, ` #`, unbalanced `'` or `\"`, etc.).\n"
            f"  input: {fm!r}\n  parser error: {e}"
        ) from e
    if reparsed != fm:
        raise ValueError(
            f"frontmatter round-trip failed: rendered YAML parses to a "
            f"different dict than the input. A frontmatter value contains "
            f"a character that changes meaning under YAML parsing.\n"
            f"  input:    {fm!r}\n  reparsed: {reparsed!r}"
        )

    return rendered


def render_target(source: Source, target_type: TargetType) -> tuple[Path, str]:
    """Render one (source, target) pair and return (output_path, content)."""
    target_value = source.targets[target_type]

    # Determine harness
    harness: Harness = "codex" if target_type == "codex-skill" else "claude"

    # Resolve output path
    if target_type == "claude-skill":
        output_path = CLAUDE_PLUGIN_ROOT / "skills" / target_value / "SKILL.md"
    elif target_type == "codex-skill":
        output_path = CODEX_PLUGIN_ROOT / "skills" / target_value / "SKILL.md"
    elif target_type == "claude-command":
        output_path = CLAUDE_PLUGIN_ROOT / "commands" / target_value
    else:
        raise ValueError(f"unknown target type: {target_type}")

    # Pick frontmatter block based on target type
    if target_type in ("claude-skill", "codex-skill"):
        if not source.skill_frontmatter:
            raise ValueError(f"{source.path}: {target_type} requires `skill:` frontmatter block")
        fm = dict(source.skill_frontmatter)  # copy
    else:  # claude-command
        if not source.command_frontmatter:
            raise ValueError(f"{source.path}: {target_type} requires `command:` frontmatter block")
        fm = dict(source.command_frontmatter)

    # Apply substitutions to frontmatter string values
    for key, value in list(fm.items()):
        if isinstance(value, str):
            fm[key] = apply_substitutions(value, harness)

    # Render body: conditionals first, then substitutions.
    # Normalize leading blank lines — the source format allows whitespace
    # between the closing frontmatter fence and the body, but the output
    # should have exactly one blank line between fence and first body line.
    body = apply_conditionals(source.body, target_type)
    body = apply_substitutions(body, harness)
    body = body.lstrip("\n")

    # Stitch frontmatter + blank line + body
    content = format_frontmatter(fm) + "\n" + body

    return output_path, content


def render_portable_body(source: Source) -> str:
    """Render a task reference without requiring a plugin or sibling skill."""
    body = apply_substitutions(apply_conditionals(source.body, "portable-skill"), "portable")
    body = body.replace("This skill assumes the ArchAstro CLI is already installed and authenticated. ", "")
    body = body.replace("`plugin-compatibility.json` from the plugin root", "[plugin-compatibility.json](plugin-compatibility.json) beside this reference")
    # Bootstrap content is shared with plugins, but portable installs must execute
    # the recovery themselves rather than send the user to another command.
    body = body.replace("instruct the user to install or upgrade `archastro`", "execute [installation](install.md), then resume authentication")
    body = body.replace("ArchAstro/archastro-cli/", "ArchAstro/archastro/")
    body = body.replace("| bash", "| env ARCHASTRO_INSTALL_SKIP_PATH_UPDATE=true ARCHASTRO_INSTALL_SKIP_COMPLETIONS=true bash")
    body = body.replace(
        "irm https://raw.githubusercontent.com/ArchAstro/archastro/main/install.ps1 | iex",
        "& ([scriptblock]::Create((irm https://raw.githubusercontent.com/ArchAstro/archastro/main/install.ps1))) -SkipPathUpdate",
    )
    for path in SOURCES_DIR.glob("*.md"):
        body = body.replace(f"`{path.stem}` skill", f"[{path.stem} guide]({path.stem}.md)")
    return body.lstrip("\n")


def render_portable_skills(sources: list[Source]) -> dict[Path, str]:
    """Each npx-installable directory carries its own runtime dependencies."""
    install = next(source for source in sources if source.path.stem == "install")
    bootstrap = (SOURCES_DIR / "references" / "bootstrap.md").read_text(encoding="utf-8")
    compatibility = (REPO_ROOT / "plugin-compatibility.json").read_text(encoding="utf-8")
    outputs: dict[Path, str] = {}
    for source in sources:
        if not source.skill_frontmatter:
            continue
        name = "archastro-" + source.skill_frontmatter["name"]
        directory = REPO_ROOT / "skills" / name
        fm = {
            "name": name,
            "description": apply_substitutions(source.skill_frontmatter["description"], "portable"),
        }
        task = render_portable_body(source)
        title = next(line for line in task.splitlines() if line.startswith("# "))
        body = (
            title + "\n\n"
            "1. Read and execute [bootstrap](references/bootstrap.md) before running task commands. "
            "If the CLI is missing or too old, install or upgrade it yourself and resume the requested task.\n"
            "2. Read the [task guide](references/task.md) and complete the user's request. "
            "An explicit upgrade request runs the upgrade steps even when a supported version is present; an install request keeps an already supported version.\n\n"
            "All required setup instructions are bundled here. Do not require another skill, "
            "a plugin slash command, or files from the source repository. "
            "Paths in linked references are relative to the reference file. "
            "Installing this skill with npx copies instructions; the agent executes CLI installation when using the skill.\n"
        )
        outputs[directory / "SKILL.md"] = format_frontmatter(fm) + "\n" + body
        outputs[directory / "references" / "task.md"] = task
        # Follow task-guide links transitively so --skill <one-name> works alone.
        guides = {item.path.stem: item for item in sources}
        pending = re.findall(r"\]\(([^/)]+)\.md\)", task)
        included = {"bootstrap", "install"}
        while pending:
            dependency = pending.pop()
            if dependency in included or dependency not in guides:
                continue
            included.add(dependency)
            reference = render_portable_body(guides[dependency])
            outputs[directory / "references" / f"{dependency}.md"] = reference
            pending.extend(re.findall(r"\]\(([^/)]+)\.md\)", reference))
        outputs[directory / "references" / "bootstrap.md"] = bootstrap
        outputs[directory / "references" / "install.md"] = render_portable_body(install)
        outputs[directory / "references" / "plugin-compatibility.json"] = compatibility
    return outputs


def render_all() -> dict[Path, str]:
    """Render every source to every declared target. Return {path: content}."""
    if not SOURCES_DIR.exists():
        raise FileNotFoundError(f"sources dir not found: {SOURCES_DIR}")

    sources = [load_source(path) for path in sorted(SOURCES_DIR.glob("*.md"))]
    outputs = render_portable_skills(sources)
    for source in sources:
        source_path = source.path
        for target_type in source.targets:
            output_path, content = render_target(source, target_type)  # type: ignore[arg-type]
            if output_path in outputs:
                raise ValueError(
                    f"output collision at {output_path} from {source_path} "
                    f"and a previous source"
                )
            outputs[output_path] = content
    return outputs


def write_outputs(outputs: dict[Path, str]) -> int:
    """Write outputs to disk. Return number of files written."""
    written = 0
    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        existing = path.read_text(encoding="utf-8") if path.exists() else None
        if existing != content:
            path.write_text(content, encoding="utf-8")
            written += 1
    return written


def check_outputs(outputs: dict[Path, str]) -> list[Path]:
    """Compare generator output to committed files. Return list of paths that differ."""
    diffs: list[Path] = []
    for path, content in outputs.items():
        if not path.exists():
            diffs.append(path)
            continue
        if path.read_text(encoding="utf-8") != content:
            diffs.append(path)
    return diffs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Diff generator output against committed files; exit 1 if different",
    )
    args = parser.parse_args()

    try:
        outputs = render_all()
    except (ValueError, FileNotFoundError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    if args.check:
        diffs = check_outputs(outputs)
        if diffs:
            print(
                f"FAIL: {len(diffs)} file(s) are out of sync with sources/. "
                "Run `python3 scripts/generate-plugin-content.py` and commit the result.",
                file=sys.stderr,
            )
            for p in diffs:
                print(f"  {p.relative_to(REPO_ROOT)}", file=sys.stderr)
            return 1
        print(f"OK: {len(outputs)} file(s) in sync with sources/.")
        return 0

    written = write_outputs(outputs)
    print(f"Wrote {written}/{len(outputs)} file(s) (others already up-to-date).")
    if written > 0:
        print(
            "NOTE: content changed — remember to bump the plugin version in "
            "all three manifest files or the plugin caches will not refresh."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
