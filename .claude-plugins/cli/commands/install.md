---
description: Install the ArchAstro developer platform CLI
allowed-tools: ["Bash(archastro:*)", "Bash(brew:*)", "Bash(curl:*)", "Bash(bash:*)", "Bash(sh:*)", "Bash(pwsh:*)", "Bash(powershell:*)"]
---

# Install ArchAstro CLI

Install or upgrade the public `archastro` binary from Homebrew or GitHub Releases.

## Instructions

1. **Read the compatibility contract first**:
   - Use `plugin-compatibility.json`.
   - For this command, prefer `plugins.cli.minimumCliVersion` and fall back to the top-level `minimumCliVersion`.
   - Treat that resolved value as the minimum supported CLI version for every check below.

2. **Check whether the CLI is already installed**:
   ```
   archastro --version
   ```
   If this succeeds, record the version.

3. **If the CLI is present and meets the resolved minimum version**, confirm the version and stop unless the user explicitly asked to upgrade.

4. **If the CLI is missing or older than the resolved minimum version**, install it using the public distribution path:
   - On macOS, if Homebrew is available:
     ```
     brew install ArchAstro/tools/archastro
     ```
     If the formula is already installed, run:
     ```
     brew upgrade ArchAstro/tools/archastro
     ```
   - On Linux or macOS without Homebrew:
     ```
     curl -fsSL https://raw.githubusercontent.com/ArchAstro/archastro-cli/main/install.sh | bash
     ```
   - On Windows PowerShell:
     ```powershell
     irm https://raw.githubusercontent.com/ArchAstro/archastro-cli/main/install.ps1 | iex
     ```

5. **Verify installation**:
   ```
   archastro --version
   ```
   Confirm that the version now meets the resolved minimum version.

6. **On success**, tell the user the CLI is ready and suggest `/cli:auth`.

7. **On failure**, help troubleshoot the public install path:
   - missing `brew` is expected on Linux and some macOS setups; fall back to `install.sh`
   - `Permission denied` usually means they need `--install-dir` or a user-writable target directory
   - `command not found: archastro` after install usually means the install directory is not on `PATH`
   - release download failures usually mean the target release asset has not been published yet
