import contextlib
import io
import json
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import tomllib
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_adapters import END, START, rendered_adapters, rule_block
from install import install


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="phurti user's ")
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.codex = self.home / '.codex'

    def install(self, agent='all', codex=None):
        with contextlib.redirect_stdout(io.StringIO()):
            install(self.home, codex or self.codex, agent)

    def test_clean_install_and_repeat(self):
        self.install()
        for directory in (self.home / '.claude/skills', self.home / '.agents/skills'):
            self.assertEqual(len(list(directory.glob('*/SKILL.md'))), 5)
            self.assertTrue((directory / 'phurti-memory/agents/openai.yaml').is_file())
        self.assertEqual(len(list((self.codex / 'agents').glob('*.toml'))), 6)
        before = {p: p.read_bytes() for p in self.home.rglob('*') if p.is_file()}
        self.install()
        after = {p: p.read_bytes() for p in self.home.rglob('*') if p.is_file()}
        self.assertEqual(before, after)
        settings = json.loads((self.codex / 'hooks.json').read_text())
        count = sum(len(group['hooks']) for groups in settings['hooks'].values() for group in groups)
        self.assertEqual(count, 4)
        for groups in settings['hooks'].values():
            for group in groups:
                for handler in group['hooks']:
                    result = subprocess.run(shlex.split(handler['command']), input='{}', text=True, capture_output=True, cwd=self.home)
                    self.assertEqual(result.returncode, 0, result.stderr)

    def test_rules_refresh_without_changing_personal_content(self):
        self.codex.mkdir()
        original = f'Personal prefix\n\n{START}\nOld rule\n{END}\n\nPersonal suffix\n'
        (self.codex / 'AGENTS.md').write_text(original)
        self.install('codex')
        actual = (self.codex / 'AGENTS.md').read_text()
        self.assertTrue(actual.startswith('Personal prefix\n\n'))
        self.assertTrue(actual.endswith('\n\nPersonal suffix\n'))
        self.assertIn(rule_block((ROOT / 'AGENTS.md').read_text()), actual)
        self.assertNotIn('Old rule', actual)
        self.assertEqual((self.codex / 'AGENTS.md.phurti-backup').read_text(), original)

    def test_existing_settings_and_custom_hooks_preserved(self):
        claude = self.home / '.claude'
        claude.mkdir()
        custom = {'type': 'command', 'command': 'echo personal-hook'}
        old = {'type': 'command', 'command': 'python3 ~/.claude/hooks/protect-tests.py'}
        settings = {'model': 'personal-choice', 'permissions': {'ask': ['Read(private.txt)']}, 'hooks': {'PreToolUse': [{'matcher': 'Edit|Write', 'hooks': [custom, old]}]}}
        (claude / 'settings.json').write_text(json.dumps(settings))
        self.install('claude')
        actual = json.loads((claude / 'settings.json').read_text())
        self.assertEqual(actual['model'], 'personal-choice')
        self.assertIn('Read(private.txt)', actual['permissions']['ask'])
        handlers = [h for group in actual['hooks']['PreToolUse'] for h in group['hooks']]
        self.assertIn(custom, handlers)
        self.assertNotIn(old, handlers)
        self.assertEqual(len(handlers), 3)
        self.assertFalse(self.codex.exists())

    def test_codex_only_leaves_claude_and_config_untouched(self):
        self.codex.mkdir()
        config = 'model = "personal-model"\n[agents]\nenabled = false\n'
        (self.codex / 'config.toml').write_text(config)
        self.install('codex')
        self.assertFalse((self.home / '.claude').exists())
        self.assertEqual((self.codex / 'config.toml').read_text(), config)
        settings = json.loads((self.codex / 'hooks.json').read_text())
        self.assertNotIn('permissions', settings)

    def test_custom_codex_home_keeps_skills_in_user_location(self):
        destination = self.home / 'custom-config'
        self.install('codex', destination)
        self.assertTrue((destination / 'AGENTS.md').exists())
        self.assertTrue((destination / 'hooks.json').exists())
        self.assertTrue((self.home / '.agents/skills/phurti-feature/SKILL.md').exists())
        self.assertFalse(self.codex.exists())

    def test_malformed_settings_stop_before_any_changes(self):
        self.codex.mkdir()
        path = self.codex / 'hooks.json'
        path.write_text('{invalid')
        with self.assertRaises(ValueError):
            self.install()
        self.assertEqual(path.read_text(), '{invalid')
        self.assertFalse((self.home / '.claude').exists())

    def test_malformed_rule_block_is_not_overwritten(self):
        self.codex.mkdir()
        path = self.codex / 'AGENTS.md'
        path.write_text('Personal instructions\n' + START)
        with self.assertRaises(ValueError):
            self.install('codex')
        self.assertEqual(path.read_text(), 'Personal instructions\n' + START)
        self.assertFalse((self.codex / 'hooks.json').exists())

    def test_codex_custom_hook_is_preserved(self):
        self.codex.mkdir()
        handler = {'type': 'command', 'command': 'python3 /personal/protect-tests.py'}
        source = {'description': 'Personal hooks', 'hooks': {'PreToolUse': [{'matcher': 'Bash', 'hooks': [handler]}]}}
        (self.codex / 'hooks.json').write_text(json.dumps(source))
        self.install('codex')
        result = json.loads((self.codex / 'hooks.json').read_text())
        self.assertEqual(result['description'], 'Personal hooks')
        self.assertEqual(result['hooks']['PreToolUse'][0]['hooks'], [handler])

    def test_review_agents_parse_and_preserve_domain_instructions(self):
        self.install('codex')
        for path in (self.codex / 'agents').glob('*.toml'):
            agent = tomllib.loads(path.read_text())
            original = (ROOT / 'agents' / (path.stem + '.md')).read_text().split('---', 2)[2].strip()
            self.assertEqual(agent['name'], path.stem)
            self.assertEqual(agent['developer_instructions'], original)
            self.assertTrue(agent['description'])

    def test_adapters_match_sources(self):
        for path, expected in rendered_adapters().items():
            self.assertEqual(path.read_text(), expected, str(path))

    def test_cli_staging_and_update(self):
        for script in ('install.sh', 'update.sh'):
            result = subprocess.run(['bash', str(ROOT / script), '--agent', 'codex', '--home', str(self.home)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.codex / 'hooks.json').exists())
        self.assertFalse((self.home / '.claude').exists())


if __name__ == '__main__':
    unittest.main()
