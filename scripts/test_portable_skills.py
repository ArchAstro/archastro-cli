#!/usr/bin/env python3
"""Real npx packaging proof; requires Node/npm and registry access.

Run: python3 scripts/test_portable_skills.py
This tests discovery and copied skill payloads, not an LLM or browser login.
"""
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"


class PortableSkillsTest(unittest.TestCase):
    def npx(self, project, *args):
        result = subprocess.run(
            ["npx", "--yes", "skills@1.5.23", "add", str(SKILLS), *args],
            cwd=project,
            env={**os.environ, "DISABLE_TELEMETRY": "1"},
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout

    def assert_self_contained(self, directory):
        self.assertTrue((directory / "SKILL.md").is_file())
        for path in directory.rglob("*.md"):
            text = path.read_text()
            self.assertNotIn("/archastro:", text, str(path))
            self.assertNotIn("plugin root", text, str(path))
            self.assertNotIn("{{", text, str(path))
            for target in re.findall(r"\]\(([^)]+)\)", text):
                if "://" in target or target.startswith("#"):
                    continue
                resolved = (path.parent / target.split("#")[0]).resolve()
                self.assertTrue(resolved.is_relative_to(directory.resolve()), str(resolved))
                self.assertTrue(resolved.is_file(), f"Missing dependency: {path} -> {target}")
        contract = json.loads((directory / "references/plugin-compatibility.json").read_text())
        self.assertEqual(contract, json.loads((ROOT / "plugin-compatibility.json").read_text()))
        self.assertNotIn("allowed-tools", (directory / "SKILL.md").read_text())

    def test_agent_can_install_one_task_with_its_bootstrap_and_guides(self):
        # A clean consumer project has no plugin and installs only one task.
        with tempfile.TemporaryDirectory(prefix="archastro-one-skill-") as tmp:
            project = Path(tmp)
            self.npx(project, "--agent", "codex", "--skill", "archastro-deploy-agent", "--yes", "--copy")
            # Cross the real npm CLI boundary, then inspect the consumer payload.
            installed = project / ".agents/skills/archastro-deploy-agent"
            self.assert_self_contained(installed)
            self.assertTrue((installed / "references/author-agent.md").is_file())
            self.assertTrue((installed / "references/build-script.md").is_file())
            self.assertEqual(len(list((project / ".agents/skills").iterdir())), 1)
            # The agent has executable official install instructions after copying.
            install = (installed / "references/install.md").read_text()
            self.assertIn("https://raw.githubusercontent.com/ArchAstro/archastro/main/install.sh", install)
            self.assertIn("archastro --version", install)
            self.assertIn("ARCHASTRO_INSTALL_SKIP_PATH_UPDATE=true", install)
            self.assertIn("ARCHASTRO_INSTALL_SKIP_COMPLETIONS=true", install)
            self.assertIn("-SkipPathUpdate", install)
            self.assertIn("resume the original task", (installed / "references/bootstrap.md").read_text())

    def test_catalog_lists_and_installs_only_portable_tasks_for_two_agents(self):
        with tempfile.TemporaryDirectory(prefix="archastro-all-skills-") as tmp:
            project = Path(tmp)
            names = {directory.name for directory in SKILLS.iterdir() if directory.is_dir()}
            listing = self.npx(project, "--list")
            for name in names:
                self.assertIn(name, listing)
            # Real discovery and installation, including the Claude consumer path.
            self.npx(project, "--agent", "codex", "claude-code", "--skill", "*", "--yes", "--copy")
            installed = project / ".agents/skills"
            self.assertEqual({directory.name for directory in installed.iterdir()}, names)
            for name in names:
                self.assert_self_contained(installed / name)
                self.assert_self_contained(project / ".claude/skills" / name)


if __name__ == "__main__":
    unittest.main()
