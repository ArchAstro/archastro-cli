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
curl -fsSL https://raw.githubusercontent.com/ArchAstro/archastro-cli/main/install.sh | bash
```

### Linux

Use the installer script:

```bash
curl -fsSL https://raw.githubusercontent.com/ArchAstro/archastro-cli/main/install.sh | bash
```

### Windows

Use the PowerShell installer:

```powershell
irm https://raw.githubusercontent.com/ArchAstro/archastro-cli/main/install.ps1 | iex
```

## Claude Code Plugin

Add the marketplace and install the `archastro` plugin:

```text
/plugin marketplace add archastro/archastro-cli
/plugin install archastro@archastro
```

The `archastro` plugin bundles everything: CLI install/auth commands, agent authoring, deployment, chat, and impersonation. The `helper` plugin remains in `ArchAstro/claude-plugins`.
