"""Exercise secret creation/migration in isolated temporary checkouts."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

SOURCE = Path(__file__).with_name('setup_blog_env.py')


class SetupEnvironmentTests(unittest.TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        (self.root / 'scripts').mkdir()
        self.script = self.root / 'scripts/setup_blog_env.py'
        shutil.copyfile(SOURCE, self.script)

    def run_setup(self):
        return subprocess.run([sys.executable, str(self.script)], capture_output=True, text=True)

    def test_new_install_generates_private_valid_settings(self):
        result = self.run_setup()
        self.assertEqual(result.returncode, 0, result.stderr)
        data = (self.root / '.env').read_text()
        values = dict(line.split('=', 1) for line in data.splitlines() if '=' in line)
        self.assertGreaterEqual(len(values['DJANGO_SECRET_KEY']), 50)
        self.assertGreaterEqual(len(values['JOURNAL_DB_PASSWORD']), 40)
        self.assertIn(':' + values['JOURNAL_DB_PASSWORD'] + '@journal-db:', values['DATABASE_URL'])
        self.assertNotIn(values['DJANGO_SECRET_KEY'], result.stdout + result.stderr)
        self.assertNotIn(values['JOURNAL_DB_PASSWORD'], result.stdout + result.stderr)
        if os.name != 'nt':
            self.assertEqual((self.root / '.env').stat().st_mode & 0o777, 0o600)

    def test_existing_dotenv_is_never_rotated(self):
        self.run_setup()
        before = (self.root / '.env').read_bytes()
        result = self.run_setup()
        self.assertEqual(result.returncode, 0)
        self.assertEqual((self.root / '.env').read_bytes(), before)

    def test_legacy_migration_preserves_every_byte_and_original(self):
        legacy = b'DJANGO_SECRET_KEY=preserved-key\r\nJOURNAL_DB_PASSWORD=preserved-password\r\nDATABASE_URL=postgresql://journal:preserved-password@journal-db/db\r\nEMAIL_HOST=mail.example.test\r\n'
        (self.root / '.env.blog').write_bytes(legacy)
        result = self.run_setup()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.root / '.env').read_bytes(), legacy)
        self.assertEqual((self.root / '.env.blog').read_bytes(), legacy)
        self.assertNotIn('preserved-password', result.stdout + result.stderr)

    def test_existing_dotenv_takes_precedence_over_legacy(self):
        self.run_setup()
        before = (self.root / '.env').read_bytes()
        (self.root / '.env.blog').write_text('unrelated legacy file')
        self.assertEqual(self.run_setup().returncode, 0)
        self.assertEqual((self.root / '.env').read_bytes(), before)

    def test_incomplete_config_is_reported_without_overwrite(self):
        for filename in ['.env', '.env.blog']:
            with self.subTest(filename=filename):
                file = self.root / filename
                file.write_text('PUBLIC_URL=https://example.test\n')
                before = file.read_bytes()
                result = self.run_setup()
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('Nothing was overwritten', result.stderr)
                self.assertEqual(file.read_bytes(), before)
                if filename == '.env.blog':
                    self.assertFalse((self.root / '.env').exists())
                file.unlink()


if __name__ == '__main__':
    unittest.main()
