---
targets:
  claude-command: auth.md
  codex-skill: auth
skill:
  name: auth
  description: Use when the user wants to authenticate with or log in to the ArchAstro developer platform, or when the CLI reports an authentication error. Trigger phrases include "authenticate archastro", "archastro auth login", "log in to archastro", "archastro not authenticated", "archastro auth status", "sign in to archastro".
  allowed-tools: ["Bash(archastro:*)"]
command:
  description: Authenticate with the ArchAstro developer platform (org mode by default)
  allowed-tools: ["Bash(archastro:*)"]
---


# ArchAstro CLI Authentication

Authenticate the user with the ArchAstro developer platform via browser-based login. Defaults to org mode (Agent Network).

## Instructions

1. **Read the compatibility contract first**:
   - Use `plugin-compatibility.json`.
   - For this command, prefer `plugins.archastro.minimumCliVersion` and fall back to the top-level `minimumCliVersion`.
   - Treat that resolved value as the minimum supported CLI version for every check below.

2. **Check the installed CLI version first**:
   ```
   archastro --version
   ```
   If the command is missing, or the version is older than the resolved minimum version, {{#CLAUDE_COMMAND}}tell the user to run `/archastro:install`{{/CLAUDE_COMMAND}}{{#SKILL}}instruct the user to install or upgrade `archastro`{{/SKILL}}.

3. **Check if already authenticated**:
   ```
   archastro auth status
   ```
   If the user is already authenticated, show their status and ask if they want to re-authenticate.

4. **Determine the auth mode**:

   The default is **org mode** (Agent Network). Only use developer mode if the user explicitly asks to log in as a developer or app builder.

   - **Org mode** (default): For users within an organization. No app slug needed — defaults to Agent Network.
   - **Developer mode**: For building and managing apps on the platform. Requires the `--dev` flag.

5. **Reset any stale settings overrides** that may point to localhost:
   ```
   archastro settings reset
   ```
   This ensures the CLI uses the production URLs.

6. **Start the login flow**:

   **Org mode (default):**
   ```
   archastro auth login
   ```

   **Org mode for a specific app** (if the user specifies a different app slug):
   ```
   archastro auth login --app <app-slug>
   ```

   **Developer mode** (only if explicitly requested):
   ```
   archastro auth login --dev
   ```

   Use `run_in_background: true` so the browser-based auth flow runs while you remain responsive.

   The CLI will open the user's browser to https://developers.archastro.ai for authentication and print a URL in case the browser doesn't open automatically.

7. **Tell the user** the auth flow is running and they should complete login in their browser. Let them know you're available to keep working on other things while waiting.

8. **When the user says they've logged in** (or you're ready to check), wait for the command to finish and then re-check status.

9. **On success**, confirm authentication succeeded and show their status:
   ```
   archastro auth status
   ```
   For org mode, verify the output shows `Auth mode: org` and the correct app/org name.

10. **On failure**, show the error and suggest:
    - Check their internet connection
    - Try `archastro settings reset` if URLs look wrong
    - `no-access` error means the user doesn't have org access — verify with an org admin for an invite
    - Try again with `archastro auth login`
