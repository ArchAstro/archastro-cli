---
description: Authenticate with the ArchAstro developer platform
allowed-tools: ["Bash(archastro:*)"]
---

# ArchAstro CLI Authentication

Authenticate the user with the ArchAstro developer platform via browser-based login.

## Instructions

1. **Read the compatibility contract first**:
   - Use `plugin-compatibility.json`.
   - For this command, prefer `plugins.cli.minimumCliVersion` and fall back to the top-level `minimumCliVersion`.
   - Treat that resolved value as the minimum supported CLI version for every check below.

2. **Check the installed CLI version first**:
   ```
   archastro --version
   ```
   If the command is missing, or the version is older than the resolved minimum version, tell the user to run `/cli:install`.

3. **Check if already authenticated**:
   ```
   archastro auth status
   ```
   If the user is already authenticated, show their status and ask if they want to re-authenticate.

4. **Reset any stale settings overrides** that may point to localhost:
   ```
   archastro settings reset
   ```
   This ensures the CLI uses the production URLs.

5. **Start the login flow**:
   ```
   archastro auth login
   ```
   Use `run_in_background: true` so the browser-based auth flow runs while you remain responsive.

   The CLI will open the user's browser to https://developers.archastro.ai for authentication and print a URL in case the browser doesn't open automatically.

6. **Tell the user** the auth flow is running and they should complete login in their browser. Let them know you're available to keep working on other things while waiting.

7. **When the user says they've logged in** (or you're ready to check), wait for the command to finish and then re-check status.

8. **On success**, confirm authentication succeeded and show their status:
   ```
   archastro auth status
   ```

9. **On failure**, show the error and suggest:
   - Check their internet connection
   - Try `archastro settings reset` if URLs look wrong
   - Try again with `archastro auth login`
