---
description: Authenticate with the ArchAstro developer platform
allowed-tools: ["Bash(archastro:*)"]
---

# ArchAstro CLI Authentication

Authenticate the user with the ArchAstro developer platform via browser-based login.

## Workflow

1. **Read the compatibility contract first**:
   - Use `plugin-compatibility.json` from the plugin root.
   - Prefer `plugins.archastro.minimumCliVersion`, fall back to the top-level `minimumCliVersion`.
   - Treat the resolved value as the minimum supported CLI version for every check below.

2. **Check the installed CLI version first**:
   ```
   archastro --version
   ```
   If the command is missing, or the version is older than the resolved minimum, tell the user to run `/archastro:install`.

3. **Check whether the user is already authenticated**:
   ```
   archastro auth status
   ```
   If the user is already authenticated, show their status and ask whether they want to re-authenticate.

4. **Preserve the user's configured server**. Reset settings only when the user asks to change them; localhost may be intentional.

5. **Start the login flow**:
   ```
   archastro auth login
   ```
   Keep the session responsive while the browser-based auth flow runs.

6. **Tell the user the auth flow is running** and they should complete login in their browser. The CLI opens the configured portal (default `https://developers.archastro.ai`) and prints a URL if the browser does not open automatically.

7. **When the user says they have logged in**, or when it is time to re-check, wait for the login command to finish and then run:
   ```
   archastro auth status
   ```

8. **On success**, confirm authentication succeeded and show the user their status.

9. **On failure**, show the error and suggest:
   - Check their internet connection.
   - Try `archastro settings reset` if URLs look wrong.
   - Try again with `archastro auth login`.


## Profiles, app selection, and non-browser authentication

- Use `archastro --profile <name> auth status` to inspect a named profile, and pass the same global profile flag on subsequent commands. Profiles separate credentials and settings; do not switch the user's active context implicitly.
- `archastro auth mode` reports developer versus organization mode. Change with `auth mode developer` or `auth mode org` only when the requested account context requires it.
- Use `archastro --app <app-id> <command>` for a one-command app override, or `archastro settings set app <app-id>` when the user wants a persistent default. App selection is separate from successful login.
- For a remote terminal without browser access, `archastro auth login --headless` uses the copy/paste flow. `auth login <email>` supports organization SSO resolution; follow the CLI's actual prompts.
- For CI or a supplied service token, inspect `archastro auth set-credentials --help` or `archastro auth systemuser --help`. Supply only user-authorized tokens through the CLI; do not print credentials or read credential files.
- Sandboxes are app resources: inspect `archastro list sandboxes` and `archastro create sandbox --help` when isolation is requested. Creating a sandbox does not itself switch authentication. `auth set-credentials --sandbox-id <id>` binds provided credentials to sandbox context; verify status and app/profile before continuing.
