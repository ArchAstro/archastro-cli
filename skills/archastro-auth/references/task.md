# ArchAstro CLI Authentication

Authenticate the user with the ArchAstro developer platform via browser-based login.

## Workflow

1. **Read the compatibility contract first**:
   - Use [plugin-compatibility.json](plugin-compatibility.json) beside this reference.
   - Prefer `plugins.archastro.minimumCliVersion`, fall back to the top-level `minimumCliVersion`.
   - Treat the resolved value as the minimum supported CLI version for every check below.

2. **Check the installed CLI version first**:
   ```
   archastro --version
   ```
   If the command is missing, or the version is older than the resolved minimum, execute [installation](install.md), then resume authentication.

3. **Check whether the user is already authenticated**:
   ```
   archastro auth status
   ```
   If already authenticated, show the status and finish unless the user explicitly requested re-authentication. Otherwise continue to login; do not ask to repeat a successful login.

4. **Preserve the user's configured server**. Reset settings only when the user asks to change them; localhost may be intentional.

5. **Start the login flow**:
   ```
   archastro auth login
   ```
   Keep the session responsive while the browser-based auth flow runs.

6. **Tell the user the auth flow is running** and they should complete login in their browser. The CLI opens `https://developers.archastro.ai` and prints a URL if the browser does not open automatically.

7. **When the user says they have logged in**, or when it is time to re-check, wait for the login command to finish and then run:
   ```
   archastro auth status
   ```

8. **On success**, confirm authentication succeeded and show the user their status.

9. **On failure**, show the error and suggest:
   - Check their internet connection.
   - Try `archastro settings reset` if URLs look wrong.
   - Try again with `archastro auth login`.
