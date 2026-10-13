"""Check consequential clean-slate behavior without asserting finished production."""
import importlib.util
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1]/'generate_episode.py'
spec = importlib.util.spec_from_file_location('generate_episode',MODULE)
generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)


class CleanSlatePlanTests(unittest.TestCase):
    def test_only_new_brief_is_copied_and_existing_episode_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)/'repo'
            (repo/'channel').mkdir(parents=True)
            (repo/'channel/production-brief.txt').write_text('CURRENT RULES')
            (repo/'channel/series-master-prompt.txt').write_text('OBSOLETE AUDIO RULES')
            folder = generator.generate(repo,repo/'episodes','intro',now=datetime(2026,10,13,17,tzinfo=timezone.utc))
            self.assertEqual((folder/'production-brief-snapshot.txt').read_text(),'CURRENT RULES')
            self.assertNotIn('OBSOLETE',(folder/'prompt.md').read_text())
            self.assertIn('no factual or playback',generator.validate(folder))
            with self.assertRaises(FileExistsError):
                generator.generate(repo,repo/'episodes','intro',now=datetime(2026,10,13,17,tzinfo=timezone.utc))
            self.assertEqual((folder/'production-brief-snapshot.txt').read_text(),'CURRENT RULES')
            (folder/'production-brief-snapshot.txt').write_text('TAMPERED')
            with self.assertRaises(ValueError):
                generator.validate(folder)

    def test_date_uses_new_york_and_invalid_request_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo/'channel').mkdir()
            (repo/'channel/production-brief.txt').write_text('CURRENT')
            folder = generator.generate(repo,repo/'episodes','late',now=datetime(2026,10,14,1,tzinfo=timezone.utc))
            self.assertEqual(folder.parent.name,'2026-10-13')
            full = generator.generate(repo,repo/'episodes','full',scope='full_episode')
            self.assertEqual(json.loads((full/'episode-status.json').read_text())['requested_duration_seconds'],720)
            with self.assertRaises(ValueError):
                generator.generate(repo,repo/'episodes','../unsafe')
            with self.assertRaises(ValueError):
                generator.generate(repo,repo/'episodes','bad',duration=-1)


if __name__ == '__main__':
    unittest.main()
