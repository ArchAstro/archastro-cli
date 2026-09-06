# Prepare the ArchAstro CLI

1. Read [plugin-compatibility.json](plugin-compatibility.json) beside this file. Use `plugins.archastro.minimumCliVersion`, falling back to `minimumCliVersion`.
2. Run `archastro --version`. Compare semantic version components numerically with the minimum. If the command is missing or too old, **execute the [installation instructions](install.md) yourself**, verify the resulting version, and resume the original task. Do not stop at telling the user to install it or invoke another skill.
3. If installation puts the binary outside the current process's `PATH`, use the installed absolute path for subsequent commands or add its directory to this session's `PATH`. Do not assume installer changes update the parent shell. Do not rewrite the user's shell configuration without a request.
4. For an install-only request, setup is complete; authentication is unnecessary. For the `archastro-auth` task, stop bootstrap after version verification and let its task guide own authentication status and login. For other work that uses the platform, run `archastro auth status`. If authentication or app selection is missing, run `archastro auth login`, let the user finish browser sign-in, then verify status and resume the task. Keep valid authentication and the user's configured server; do not reset settings as routine setup.
5. If an installer or login fails, report the actual error and the missing prerequisite. Never claim success from a downloaded skill alone.

Do not inspect credential files. Use CLI commands for authentication and discovery. Only fetch the task-specific live reference when the task guide calls for it.
