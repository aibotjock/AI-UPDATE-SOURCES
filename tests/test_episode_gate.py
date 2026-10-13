import datetime as dt
import importlib.util
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("episode_gate", Path(__file__).parents[1] / "tools" / "episode_gate.py")
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class EvidenceGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.now = dt.datetime.fromisoformat("2026-10-13T12:00:00-04:00")
        self.manifest = {
            "timezone": "America/New_York", "research_cutoff": "2026-10-13T11:00:00-04:00",
            "claims": [{"id": "C1", "source_url": "https://example.org/price", "reviewed": True,
                        "changeable": True, "verified_at": "2026-10-13T10:00:00-04:00",
                        "evidence_type": "provider-reported"}],
            "central_comparison": {"complete": True, "run_records": ["a.json", "b.json"]}}
        # These are synthetic unit-test fixtures. They never represent real model runs.
        for name, model in [("a.json", "fixture-a"), ("b.json", "fixture-b")]:
            messages = [{"role": "user", "content": "unit-test prompt"}]
            prompt_hash = hashlib.sha256(json.dumps(messages, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            (self.base / name).write_text(json.dumps({"status": "completed", "raw_response": {"fixture": True},
                "prompt_sha256": prompt_hash, "provider": "unit-test-only", "requested_model": model,
                "request_payload": {"messages": messages}, "settings_verified": True,
                "origin": "live_provider_requests", "observed_at_utc": "2026-10-13T10:00:00-04:00",
                "usage": {"raw": {"prompt_tokens": 5, "completion_tokens": 2}, "input_tokens": 5, "output_tokens": 2},
                "cost": {"total_usd": 0.001, "basis": "published_tariff_calculation_only"}}))

    def tearDown(self):
        self.temp.cleanup()

    def errors(self, stage="research"):
        return gate.check(self.manifest, self.base, stage, self.now)["errors"]

    def test_valid_research_fixture(self):
        # Structural validity of hypothetical metadata is not an authenticity claim.
        self.assertEqual(self.errors(), [])

    def test_explicit_test_fixture_is_rejected(self):
        path = self.base / "a.json"
        record = json.loads(path.read_text())
        record["test_fixture"] = True
        path.write_text(json.dumps(record))
        self.assertTrue(any("real provider" in s for s in self.errors()))

    def test_verification_after_cutoff_is_rejected(self):
        self.manifest["claims"][0]["verified_at"] = "2026-10-13T11:30:00-04:00"
        self.assertTrue(any("mutable claim" in s for s in self.errors()))

    def test_complete_flag_cannot_replace_runs(self):
        self.manifest["central_comparison"]["run_records"] = []
        self.assertTrue(any("two original" in s for s in self.errors()))

    def test_utc_date_does_not_replace_eastern_date(self):
        self.manifest["research_cutoff"] = "2026-10-13T01:00:00+00:00"
        self.assertTrue(any("today's local" in s for s in self.errors()))

    def test_stale_claim_and_future_cutoff_rejected(self):
        self.manifest["claims"][0]["verified_at"] = "2026-10-12T22:00:00-04:00"
        self.manifest["research_cutoff"] = "2026-10-14T10:00:00-04:00"
        self.assertTrue(any("mutable claim" in s for s in self.errors()))
        self.assertTrue(any("future" in s for s in self.errors()))

    def test_different_prompt_rejected(self):
        path = self.base / "b.json"
        record = json.loads(path.read_text())
        record["prompt_sha256"] = "different"
        path.write_text(json.dumps(record))
        self.assertTrue(any("identical prompt" in s for s in self.errors()))

    def test_missing_cost_rejected(self):
        path = self.base / "a.json"
        record = json.loads(path.read_text())
        record["cost"]["total_usd"] = None
        path.write_text(json.dumps(record))
        self.assertTrue(any("supported task cost" in s for s in self.errors()))

    def test_no_final_without_playback_and_actual_files(self):
        errors = self.errors("final")
        self.assertTrue(any("Measured runtime" in s for s in errors))
        self.assertTrue(any("mp4" in s for s in errors))
        self.assertTrue(any("full_video_watch_and_listen" in s for s in errors))


if __name__ == "__main__":
    unittest.main()
