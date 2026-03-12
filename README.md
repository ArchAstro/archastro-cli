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

## Claude Code Plugins

Add the marketplace and install the public plugins:

```text
/plugin marketplace add archastro/archastro-cli
/plugin install cli@archastro
/plugin install agents@archastro
```

The `helper` plugin remains in `ArchAstro/claude-plugins`.
