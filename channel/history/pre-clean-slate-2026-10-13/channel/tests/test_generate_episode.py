import importlib.util
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path


spec = importlib.util.spec_from_file_location("generate_episode", Path(__file__).parents[1] / "generate_episode.py")
episode = importlib.util.module_from_spec(spec)
spec.loader.exec_module(episode)
GENERATED = datetime.fromisoformat("2026-10-13T09:00:00-04:00")
CHECKED = datetime.fromisoformat("2026-10-13T16:00:00-04:00")


class EpisodeTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        for name in episode.REFERENCES:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            content = json.dumps({"schema_version": 1, "series_version": "1.0.0"}) if name.endswith(".json") else "Canonical reference text.\n"
            path.write_text(content, encoding="utf-8")
        self.folder = episode.generate(self.root, self.root / "episodes", "01", now=GENERATED)

    def status(self):
        return episode.read_json(self.folder / "episode-status.json")

    def save_status(self, value):
        episode.write_json(self.folder / "episode-status.json", value)

    def research(self):
        episode.write_json(self.folder / "evidence-ledger.json", {
            "schema_version": 1, "episode_date": "2026-10-13",
            "research_started_at": "2026-10-13T09:10:00-04:00",
            "research_completed_at": "2026-10-13T10:00:00-04:00",
            "sources": [{"title": "Original benchmark", "url": "https://example.com/benchmark",
                         "kind": "benchmark", "claims": ["Measured result"],
                         "content_verified": True, "authority_note": "Original measurement with disclosed method.",
                         "independent_validation": "Compared against the original result table.",
                         "regularly_updated_verified": True, "recent_maintenance_verified": True,
                         "update_cadence": "Observed weekly releases in the update history.",
                         "update_history_url": "https://example.com/benchmark/history",
                         "last_updated_at": "2026-10-12", "maintenance_checked_at": "2026-10-13T09:30:00-04:00",
                         "published_date": "2026-10-01", "original_benchmark_date": "2026-10-01",
                         "verified_at": "2026-10-13T09:30:00-04:00"}],
        })
        status = self.status()
        status["stage"] = "researched"
        self.save_status(status)

    def finalize(self):
        self.research()
        episode.write_json(self.folder / "same-prompt-comparison.json", {
            "schema_version": 1, "episode_date": "2026-10-13", "comparison_reviewed_at": "2026-10-13T10:10:00-04:00",
            "prompt": "The same prompt", "runs": [
                {"provider": "Provider A", "model": "Tool A", "version": "2026-10-01", "mode": "standard",
                 "run_at": "2026-10-13T10:05:00-04:00", "evidence_origin": "new_run",
                 "settings": {}, "result": "Recorded output A", "usage_cost": {
                     "usage": "Provider does not expose usage", "cost_basis": "unavailable", "total": None,
                     "currency": None, "note": "Existing authorized account; usage and per-prompt cost unavailable."}},
                {"provider": "Provider B", "model": "Tool B", "version": "2026-10-02", "mode": "standard",
                 "run_at": "2026-10-13T10:06:00-04:00", "evidence_origin": "new_run",
                 "settings": {}, "result": "Recorded output B", "usage_cost": {
                     "usage": "Provider does not expose usage", "cost_basis": "subscription_not_allocated",
                     "total": None, "currency": None, "note": "Existing subscription; no per-prompt allocation."}}],
            "observations": ["A was clearer on the tested criterion."], "choice": "A for this task",
        })
        script = self.folder / "script.txt"
        script.write_text("A test fixture, not a production script.", encoding="utf-8")
        status = self.status()
        status.update(stage="script_finalized", script_path="script.txt", script_sha256=episode.digest(script),
                      script_created_at="2026-10-13T10:20:00-04:00",
                      script_finalized_at="2026-10-13T11:00:00-04:00", duration_seconds=720)
        self.save_status(status)

    def render(self):
        self.finalize()
        video = self.folder / "fixture.mp4"
        video.write_bytes(b"Test artifact; validator does not inspect video content.")
        status = self.status()
        status.update(stage="rendered", video_path="fixture.mp4", video_sha256=episode.digest(video),
                      render_script_sha256=status["script_sha256"], playback_video_sha256=episode.digest(video),
                      rendered_at="2026-10-13T12:00:00-04:00",
                      playback_verified_at="2026-10-13T12:30:00-04:00",
                      playback_method="manual_full_playback",
                      playback_notes="Fixture attestation only: validator cannot perform playback.")
        self.save_status(status)

    def test_local_date_rolls_at_new_york_midnight(self):
        before = datetime(2026, 10, 14, 3, 59, tzinfo=timezone.utc)
        after = datetime(2026, 10, 14, 4, 0, tzinfo=timezone.utc)
        self.assertEqual(episode.local_now(before).date().isoformat(), "2026-10-13")
        self.assertEqual(episode.local_now(after).date().isoformat(), "2026-10-14")
        next_folder = episode.generate(self.root, self.root / "episodes", "02", now=after)
        self.assertEqual(next_folder.parent.name, "2026-10-14")
        self.assertEqual(next_folder.name, "02")
        winter = datetime(2026, 12, 2, 4, 59, tzinfo=timezone.utc)
        self.assertEqual(episode.local_now(winter).date().isoformat(), "2026-12-01")

    def test_cli_has_no_backdate_option(self):
        with self.assertRaises(SystemExit) as caught:
            episode.main(["generate", "--episode", "00", "--date", "2020-01-01"])
        self.assertEqual(caught.exception.code, 2)
        self.assertFalse((self.root / "episodes" / "2020-01-01").exists())

    def test_same_day_duplicate_cannot_overwrite(self):
        original = (self.folder / "prompt.md").read_bytes()
        with self.assertRaises(FileExistsError):
            episode.generate(self.root, self.root / "episodes", "01", now=GENERATED)
        self.assertEqual((self.folder / "prompt.md").read_bytes(), original)
        self.assertEqual(self.status()["episode_id"], "01")

    def test_distinct_episode_ids_can_share_actual_generation_day(self):
        second = episode.generate(self.root, self.root / "episodes", "02", now=GENERATED)
        self.assertEqual(second.parent, self.folder.parent)
        self.assertEqual(second.name, "02")
        self.assertEqual(episode.read_json(second / "episode-status.json")["episode_id"], "02")

    def test_large_resource_catalog_is_snapshotted_without_inline_prompt_bloat(self):
        marker = "A_RESOURCE_ASSET_MARKER_" * 10000
        (self.root / "library/asset-index.json").write_text(json.dumps({"assets": [marker]}))
        another = episode.generate(self.root, self.root / "compact-episodes", "02", now=GENERATED)
        prompt = (another / "prompt.md").read_text()
        self.assertNotIn(marker, prompt)
        self.assertIn("reference-snapshot/library/asset-index.json", prompt)
        self.assertLess(len(prompt), 15000)
        self.assertIn(marker, (another / "reference-snapshot/library/asset-index.json").read_text())

    def test_optional_lesson_is_omitted_by_default(self):
        self.assertFalse(self.status()["practical_lesson_included"])
        self.assertNotIn("Practical lesson selected:", (self.folder / "prompt.md").read_text())
        another = episode.generate(self.root, self.root / "lesson-episodes", "02", True, GENERATED)
        self.assertIn("Practical lesson selected:", (another / "prompt.md").read_text())

    def test_generated_scaffolds_do_not_claim_research_or_final_artifacts(self):
        self.assertEqual(episode.validate(self.folder, CHECKED), "prompt_generated")
        (self.folder / "script.txt").write_text("Unreviewed draft.")
        (self.folder / "draft.mp4").write_bytes(b"Artifact alone does not change stage.")
        self.assertEqual(episode.validate(self.folder, CHECKED), "prompt_generated")
        status = self.status()
        for stage in episode.STAGES[1:]:
            status["stage"] = stage
            self.save_status(status)
            with self.subTest(stage=stage), self.assertRaises(ValueError):
                episode.validate(self.folder, CHECKED)

    def test_reference_snapshots_survive_canonical_changes_and_detect_tampering(self):
        (self.root / episode.REFERENCES[0]).write_text("Changed canonical registry.")
        self.assertEqual(episode.validate(self.folder, CHECKED), "prompt_generated")
        (self.folder / "reference-snapshot" / episode.REFERENCES[0]).write_text("Changed frozen registry.")
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            episode.validate(self.folder, CHECKED)

    def test_source_and_evolution_policies_are_frozen_and_embedded(self):
        status = self.status()
        prompt = (self.folder / "prompt.md").read_text()
        for policy in ("channel/source-review-policy.md", "channel/evolution-policy.md"):
            with self.subTest(policy=policy):
                self.assertIn(policy, episode.REFERENCES)
                snapshot = self.folder / "reference-snapshot" / policy
                self.assertEqual(status["reference_sha256"][policy], episode.digest(snapshot))
                self.assertIn("### " + policy, prompt)

    def test_generated_comparison_template_separates_review_and_original_run(self):
        comparison = episode.read_json(self.folder / "same-prompt-comparison.json")
        self.assertIsNone(comparison["comparison_reviewed_at"])
        self.assertNotIn("compared_at", comparison)
        template = comparison["run_record_template"]
        for field in ("run_at", "evidence_origin", "evidence_reference", "reuse_review_note"):
            self.assertIsNone(template[field])

    def test_archive_validation_uses_generation_day_not_today(self):
        self.research()
        self.assertEqual(episode.validate(self.folder, datetime.fromisoformat("2026-10-20T12:00:00-04:00")), "researched")
        status = self.status()
        status["episode_date"] = "2026-10-12"
        self.save_status(status)
        with self.assertRaisesRegex(ValueError, "generated_at"):
            episode.validate(self.folder, CHECKED)

    def test_repeated_benchmark_needs_original_date_and_today_verification(self):
        self.research()
        self.assertEqual(episode.validate(self.folder, CHECKED), "researched")
        path = self.folder / "evidence-ledger.json"
        ledger = episode.read_json(path)
        ledger["sources"][0]["original_benchmark_date"] = None
        episode.write_json(path, ledger)
        with self.assertRaisesRegex(ValueError, "original date"):
            episode.validate(self.folder, CHECKED)
        ledger["sources"][0]["original_benchmark_date"] = "2026-10-01"
        ledger["sources"][0]["verified_at"] = "2026-10-12T09:30:00-04:00"
        episode.write_json(path, ledger)
        with self.assertRaisesRegex(ValueError, "local date"):
            episode.validate(self.folder, CHECKED)

    def test_access_check_without_content_verification_is_insufficient(self):
        self.research()
        path = self.folder / "evidence-ledger.json"
        ledger = episode.read_json(path)
        ledger["sources"][0]["content_verified"] = False
        episode.write_json(path, ledger)
        with self.assertRaisesRegex(ValueError, "content verification"):
            episode.validate(self.folder, CHECKED)

    def test_maintenance_evidence_is_required_for_researched_stage(self):
        self.research()
        path = self.folder / "evidence-ledger.json"
        original = episode.read_json(path)
        for field in ("regularly_updated_verified", "recent_maintenance_verified", "update_cadence",
                      "update_history_url", "last_updated_at", "maintenance_checked_at"):
            ledger = json.loads(json.dumps(original))
            ledger["sources"][0][field] = None
            episode.write_json(path, ledger)
            with self.subTest(field=field), self.assertRaises(ValueError):
                episode.validate(self.folder, CHECKED)
        original["sources"][0]["update_history_url"] = None
        original["sources"][0]["maintenance_evidence"] = [{"date": "2026-10-12", "note": "Observed new benchmark release."}]
        episode.write_json(path, original)
        self.assertEqual(episode.validate(self.folder, CHECKED), "researched")

    def test_script_cannot_precede_research(self):
        self.finalize()
        status = self.status()
        status["script_created_at"] = "2026-10-13T09:45:00-04:00"
        self.save_status(status)
        with self.assertRaisesRegex(ValueError, "before script creation"):
            episode.validate(self.folder, CHECKED)

    def test_comparison_rejects_a_conflicting_run_prompt(self):
        self.finalize()
        path = self.folder / "same-prompt-comparison.json"
        comparison = episode.read_json(path)
        comparison["runs"][0]["prompt"] = "A different prompt"
        episode.write_json(path, comparison)
        with self.assertRaisesRegex(ValueError, "exactly the shared prompt"):
            episode.validate(self.folder, CHECKED)

    def test_approved_reuse_preserves_original_run_date_with_today_review(self):
        self.finalize()
        path = self.folder / "same-prompt-comparison.json"
        comparison = episode.read_json(path)
        original = "2026-10-01T14:25:00+00:00"
        comparison["runs"][0].update(
            evidence_origin="reused_run", run_at=original,
            evidence_reference="library/retained-runs/tool-a-original.json",
            reuse_review_note="Reviewed original evidence today: identical shared prompt and task; "
                              "model version, standard mode and recorded settings remain valid.")
        episode.write_json(path, comparison)
        self.assertEqual(episode.validate(self.folder, CHECKED), "script_finalized")
        self.assertEqual(episode.read_json(path)["runs"][0]["run_at"], original)

    def test_reuse_requires_retained_evidence_and_current_validity_note(self):
        self.finalize()
        path = self.folder / "same-prompt-comparison.json"
        comparison = episode.read_json(path)
        run = comparison["runs"][0]
        run.update(evidence_origin="reused_run", run_at="2026-10-01T10:00:00-04:00")
        for reference, note in ((None, "Configuration and task remain valid."), ("retained-original", None),
                                ("retained-original", "  ")):
            run.update(evidence_reference=reference, reuse_review_note=note)
            episode.write_json(path, comparison)
            with self.subTest(reference=reference, note=note), self.assertRaisesRegex(ValueError, "Reused runs require"):
                episode.validate(self.folder, CHECKED)

    def test_new_runs_cannot_relabel_historical_or_preproduction_evidence(self):
        self.finalize()
        path = self.folder / "same-prompt-comparison.json"
        comparison = episode.read_json(path)
        for stamp in ("2026-10-12T10:00:00-04:00", "2026-10-13T09:05:00-04:00"):
            comparison["runs"][0]["run_at"] = stamp
            episode.write_json(path, comparison)
            with self.subTest(stamp=stamp), self.assertRaises(ValueError):
                episode.validate(self.folder, CHECKED)

    def test_original_run_requires_aware_timestamp_before_review(self):
        self.finalize()
        path = self.folder / "same-prompt-comparison.json"
        comparison = episode.read_json(path)
        for origin in ("new_run", "reused_run"):
            comparison["runs"][0].update(evidence_origin=origin, evidence_reference="retained-original",
                                        reuse_review_note="Configuration and task remain valid.")
            for stamp in (None, "2026-10-13T10:05:00", "2026-10-13T10:15:00-04:00"):
                comparison["runs"][0]["run_at"] = stamp
                episode.write_json(path, comparison)
                with self.subTest(origin=origin, stamp=stamp), self.assertRaises(ValueError):
                    episode.validate(self.folder, CHECKED)

    def test_comparison_review_must_be_today_and_before_script_creation(self):
        self.finalize()
        path = self.folder / "same-prompt-comparison.json"
        comparison = episode.read_json(path)
        for stamp in ("2026-10-12T10:10:00-04:00", "2026-10-13T09:05:00-04:00", "2026-10-13T10:30:00-04:00"):
            comparison["comparison_reviewed_at"] = stamp
            episode.write_json(path, comparison)
            with self.subTest(stamp=stamp), self.assertRaises(ValueError):
                episode.validate(self.folder, CHECKED)

    def test_naive_and_future_timestamps_fail(self):
        self.research()
        path = self.folder / "evidence-ledger.json"
        ledger = episode.read_json(path)
        for stamp in ("2026-10-13T09:30:00", "2026-10-13T17:00:00-04:00"):
            ledger["sources"][0]["verified_at"] = stamp
            episode.write_json(path, ledger)
            with self.subTest(stamp=stamp), self.assertRaises(ValueError):
                episode.validate(self.folder, CHECKED)

    def test_finalization_requires_completed_research_shared_prompt_and_duration(self):
        self.finalize()
        self.assertEqual(episode.validate(self.folder, CHECKED), "script_finalized")
        status = self.status()
        for seconds in (599, 901):
            status["duration_seconds"] = seconds
            self.save_status(status)
            with self.subTest(seconds=seconds), self.assertRaises(ValueError):
                episode.validate(self.folder, CHECKED)
        status.update(duration_seconds=960, duration_extension_reason="Rare launch episode with justified extra comparison.")
        self.save_status(status)
        self.assertEqual(episode.validate(self.folder, CHECKED), "script_finalized")
        path = self.folder / "same-prompt-comparison.json"
        comparison = episode.read_json(path)
        comparison["runs"][0]["usage_cost"]["cost_basis"] = "estimated"
        episode.write_json(path, comparison)
        with self.assertRaisesRegex(ValueError, "numeric totals"):
            episode.validate(self.folder, CHECKED)

    def test_authorized_paid_api_run_preserves_measured_usage_cost(self):
        self.finalize()
        path = self.folder / "same-prompt-comparison.json"
        comparison = episode.read_json(path)
        comparison["runs"][0]["usage_cost"] = {
            "usage": {"input_tokens": 1000, "output_tokens": 250}, "cost_basis": "measured",
            "total": 0.03, "currency": "USD", "note": "Measured in authorized existing API account usage."}
        episode.write_json(path, comparison)
        self.assertEqual(episode.validate(self.folder, CHECKED), "script_finalized")
        comparison["runs"][1]["usage_cost"]["total"] = 0.01
        episode.write_json(path, comparison)
        with self.assertRaisesRegex(ValueError, "unallocated per-prompt costs"):
            episode.validate(self.folder, CHECKED)

    def test_decoder_integrity_check_cannot_complete_manual_playback(self):
        self.render()
        status = self.status()
        status["playback_method"] = "decoder_verification"
        self.save_status(status)
        with self.assertRaisesRegex(ValueError, "manual full watch/listen"):
            episode.validate(self.folder, CHECKED)

    def test_render_requires_playback_record_and_unchanged_video(self):
        self.render()
        self.assertEqual(episode.validate(self.folder, CHECKED), "rendered")
        status = self.status()
        status["playback_verified_at"] = None
        self.save_status(status)
        with self.assertRaisesRegex(ValueError, "playback_verified_at"):
            episode.validate(self.folder, CHECKED)
        status["playback_verified_at"] = "2026-10-13T12:30:00-04:00"
        self.save_status(status)
        (self.folder / "fixture.mp4").write_bytes(b"Changed after recorded playback.")
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            episode.validate(self.folder, CHECKED)
        status["video_sha256"] = episode.digest(self.folder / "fixture.mp4")
        self.save_status(status)
        with self.assertRaisesRegex(ValueError, "verified video hash"):
            episode.validate(self.folder, CHECKED)


if __name__ == "__main__":
    unittest.main()
