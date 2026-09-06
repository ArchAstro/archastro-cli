#!/usr/bin/env python3
"""Check documented command paths/options against the supported public CLI.

ARCHASTRO_CLI=/absolute/path/to/archastro python3 scripts/test_skill_commands.py
Only --help runs: this proves command compatibility, not backend behavior.
"""
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parent.parent
CLI = os.environ.get('ARCHASTRO_CLI') or shutil.which('archastro')


def examples():
    # Rendered task references contain no harness conditionals. Continuations
    # retain flags that would otherwise hide on the next line of an example.
    for path in sorted((ROOT / 'skills').glob('*/references/task.md')):
        text = re.sub(r'\\\n\s*', ' ', path.read_text())
        for number, line in enumerate(text.splitlines(), 1):
            if line.strip().startswith('archastro '):
                yield path, number, shlex.split(line.strip())


class SkillCommandCompatibilityTest(unittest.TestCase):
    def test_core_resource_inventory_has_a_skill_owner(self):
        self.assertTrue(CLI, 'Set ARCHASTRO_CLI to the supported release binary')
        result = subprocess.run([CLI, 'resources'], capture_output=True, text=True, check=True)
        resources = set(re.findall(r'^(\S+)\s{2,}(?:list|describe|create|update|delete|export|refresh|activate|test|validate|run)\b', result.stdout, re.M))
        self.assertTrue(resources, 'The CLI resource inventory could not be read')
        covered = set()
        for line in (ROOT / 'SKILL_COVERAGE.md').read_text().splitlines():
            if line.startswith('| [archastro-'):
                skill_path = re.search(r'\]\(([^)]+)\)', line).group(1)
                self.assertTrue((ROOT / skill_path).is_file(), skill_path)
                covered.update(re.findall(r'`([^`]+)`', line.split('|')[-2]))
        self.assertEqual(resources, covered, f'Missing coverage: {resources - covered}; stale entries: {covered - resources}')

    def test_documented_commands_and_flags_exist_in_supported_cli(self):
        self.assertTrue(CLI, 'Set ARCHASTRO_CLI to the supported release binary')
        root_help = subprocess.run([CLI, '--help'], capture_output=True, text=True, check=True).stdout
        global_options = root_help.split('Options:', 1)[1].split('\n\n', 1)[0]
        global_flags = set(re.findall(r'--[a-z][a-z0-9-]*', global_options))
        checked = {}
        count = 0
        for path, line, words in examples():
            args = words[1:]
            # Select only the command path. Positional examples are never executed.
            if args[0].startswith('-'):
                continue
            command = args[:2] if len(args) > 1 and not args[1].startswith('-') else args[:1]
            if command[0] in {'resources', 'init', 'astrodev', 'astrorun', 'astroimage'}:
                command = command[:1]
            if command[0] == 'embed' and len(args) > 2 and command[1] in {'list', 'run', 'install'}:
                command = args[:3]
            if command[0] == 'settings' and len(command) > 1 and command[1] in {'get', 'set', 'reset'}:
                command = command[:2]
            if command[0] == 'help':
                # Topic text is offline; --help would only validate the help command.
                probe = command
            else:
                probe = [*command, '--help']
            key = tuple(probe)
            if key not in checked:
                checked[key] = subprocess.run([CLI, *probe], capture_output=True, text=True)
            result = checked[key]
            with self.subTest(file=str(path.relative_to(ROOT)), line=line, command=command):
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertNotIn('Unknown command', result.stdout + result.stderr)
                if command[0] != 'help':
                    # Commander can print root help and exit zero for a removed
                    # command when --help is present. Check the selected path too.
                    usage = re.search(r'^Usage: archastro (.+)$', result.stdout, re.M)
                    self.assertIsNotNone(usage, result.stdout)
                    parts = usage.group(1).split()
                    for expected, actual in zip(command, parts):
                        # Resource aliases also accept hyphenated spellings;
                        # the CLI's Usage line displays canonical spellings.
                        self.assertIn(expected.replace('-', ''), [part.replace('-', '') for part in actual.split('|')], result.stdout)
                    self.assertGreaterEqual(len(parts), len(command))
                flags = set(re.findall(r'--[a-z][a-z0-9-]*', result.stdout)) | global_flags
                for word in args:
                    if re.fullmatch(r'--[a-z][a-z0-9-]*(?:=.*)?', word):
                        self.assertIn(word.split('=', 1)[0], flags, result.stdout)
            count += 1
        self.assertGreater(count, 0, 'No documented commands were checked')
        print(f'Checked {count} documented examples against {len(checked)} public CLI help paths.')


if __name__ == '__main__':
    unittest.main()
