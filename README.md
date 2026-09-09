# ArchAstro CLI

Public distribution repository for the ArchAstro CLI.

## Install

GitHub Releases are the canonical distribution path.

### macOS

Prefer Homebrew when available:

```bash
brew install ArchAstro/tools/archastro
```

Fallback to the installer script:

```bash
curl -fsSL https://raw.githubusercontent.com/ArchAstro/archastro/main/install.sh | bash
```

### Linux

Use the installer script:

```bash
curl -fsSL https://raw.githubusercontent.com/ArchAstro/archastro/main/install.sh | bash
```

### Windows

Use the PowerShell installer:

```powershell
irm https://raw.githubusercontent.com/ArchAstro/archastro/main/install.ps1 | iex
```

## Agent skills (npx skills)

Install the portable skills for Codex, Claude Code, and other supported agents:

```bash
npx skills add https://github.com/ArchAstro/archastro/tree/main/skills
```

Select your agent and skills interactively, or install all skills for Codex without prompts:

```bash
npx skills add https://github.com/ArchAstro/archastro/tree/main/skills --agent codex --skill '*' --yes
```

Use `--global` for a user-wide installation. To install only one task, pass e.g. `--skill archastro-build-script`; its bootstrap and referenced guides are included. Use `--list` to inspect available skills.

The `/skills` source selects the portable catalog. The bare repository also contains legacy plugin skills with unprefixed names; use the URL above to avoid those plugin-specific variants.

The skill installer copies instructions; it does not install the ArchAstro binary. When an agent uses a skill, it checks `archastro --version`, installs or upgrades the CLI if necessary, verifies it, and resumes the requested task. Platform work starts browser authentication when needed. Install-only requests do not require login.

### Skill organization

Each `archastro-<task>` skill has a short entrypoint and detailed references loaded on demand. Task descriptions handle discovery; references hold longer authoring guides. Every installable directory includes its own bootstrap, compatibility contract, and linked task guides, so a skill never depends on another installed skill or a plugin command.

Canonical content lives in `sources/`; `scripts/generate-plugin-content.py` generates both portable `skills/` bundles and the existing plugin outputs. After editing sources or `plugin-compatibility.json`, run:

```bash
python3 scripts/generate-plugin-content.py
python3 scripts/generate-plugin-content.py --check
python3 scripts/test_portable_skills.py
```

## Claude Code Plugin

Add the marketplace and install the `archastro` plugin:

```text
/plugin marketplace add archastro/archastro
/plugin install archastro@archastro
```

The `archastro` plugin bundles everything: CLI install/auth commands, agent authoring, deployment, chat, and impersonation. The `helper` plugin remains in `ArchAstro/claude-plugins`.
