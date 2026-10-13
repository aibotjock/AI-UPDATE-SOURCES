#!/usr/bin/env python3
"""Meaningful gate tests plus an optional short offline encode smoke test."""
import datetime as dt
import json
import pathlib
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import render_episode as renderer

HERE = pathlib.Path(__file__).resolve().parent
SAMPLE_AUDIO = HERE / "fixtures" / "voice-sample.wav"
SAMPLE_IMAGE = HERE / "fixtures" / "title-frame.png"


def ensure_samples():
    """Regenerate tiny infrastructure fixtures locally instead of storing binaries."""
    SAMPLE_AUDIO.parent.mkdir(parents=True, exist_ok=True)
    if not SAMPLE_AUDIO.is_file():
        speech = "Welcome to A I Update. I am Doctor Chris. When an A I model tops a leaderboard, how do you know whether it is right for your work?"
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i",
                        "flite=text='" + speech + "':voice=slt", "-ar", "48000", "-ac", "1", str(SAMPLE_AUDIO)], check=True)
    if not SAMPLE_IMAGE.is_file():
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i",
                        "color=c=0x071321:s=1920x1080:d=1", "-vf",
                        "drawtext=font='DejaVu Sans':text='AI UPDATE':fontcolor=0x5fe1e8:fontsize=98:x=(w-tw)/2:y=(h-th)/2",
                        "-frames:v", "1", str(SAMPLE_IMAGE)], check=True)


def fixture(image, audio):
    now = dt.datetime.now(dt.timezone.utc)
    return {"schema_version": 1, "episode_id": "INFRASTRUCTURE-SMOKE-ONLY",
            "title": "Renderer smoke test, not an episode", "fixture_only": True,
            "timezone": "America/New_York", "research_cutoff": now.isoformat(),
            "finalization_date": str(now.astimezone(renderer.ZoneInfo("America/New_York")).date()),
            "claims": [], "central_comparison": {"complete": False, "scene_ids": []},
            "scenes": [{"id": "SMOKE", "scene_type": "branding", "image": str(image),
                "narration_wav": str(audio), "claim_ids": [], "captions_verified": False,
                "captions": [
                    {"start": 0, "end": 2.3, "text": "Welcome to AI Update. I am Doctor Chris."},
                    {"start": 2.3, "end": 4.0, "text": "When an AI model tops a leaderboard,"},
                    {"start": 4.0, "end": 7.59, "text": "how do you know whether it is right for your work?"}]}]}


class Gates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ensure_samples()
        if not SAMPLE_AUDIO.is_file() or not SAMPLE_IMAGE.is_file():
            raise RuntimeError("Existing feasibility sample assets are required")
        cls.scratch = tempfile.TemporaryDirectory(prefix="episode-render-gates-")
        cls.directory = pathlib.Path(cls.scratch.name)
        cls.image = cls.directory / "sample.png"
        cls.image.write_bytes(SAMPLE_IMAGE.read_bytes())

    @classmethod
    def tearDownClass(cls):
        cls.scratch.cleanup()

    def inspect(self, manifest, fixture_mode=False):
        target = self.directory / "manifest.json"
        target.write_text(json.dumps(manifest))
        return renderer.validate(target, fixture=fixture_mode)[1]

    def test_short_fixture_measures_audio(self):
        result = self.inspect(fixture(self.image, SAMPLE_AUDIO), True)
        self.assertTrue(result["valid"], result["errors"])
        self.assertAlmostEqual(result["actual_narration_seconds"], 7.59, places=2)
        self.assertAlmostEqual(result["runtime_seconds"], 7.6, places=2)
        self.assertTrue(result["manual_playback_required"])
        self.assertFalse(result["manual_playback_complete"])

    def test_fixture_cannot_claim_final_episode(self):
        result = self.inspect(fixture(self.image, SAMPLE_AUDIO))
        self.assertFalse(result["valid"])
        self.assertTrue(any("Fixture manifests" in e for e in result["errors"]))
        self.assertTrue(any("below required 600s" in e for e in result["errors"]))
        self.assertTrue(any("comparison is incomplete" in e for e in result["errors"]))

    def test_missing_audio_refuses(self):
        m = fixture(self.image, SAMPLE_AUDIO)
        m["scenes"][0]["narration_wav"] = "missing.wav"
        result = self.inspect(m, True)
        self.assertFalse(result["valid"])
        self.assertTrue(any("missing or empty file" in e for e in result["errors"]))

    def test_stale_cutoff_refuses_final(self):
        m = fixture(self.image, SAMPLE_AUDIO)
        m["fixture_only"] = False
        m["research_cutoff"] = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=2)).isoformat()
        result = self.inspect(m)
        self.assertTrue(any("Source cutoff is stale" in e for e in result["errors"]))

    def test_future_cutoff_refuses(self):
        m = fixture(self.image, SAMPLE_AUDIO)
        m["research_cutoff"] = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=10)).isoformat()
        result = self.inspect(m, True)
        self.assertFalse(result["valid"])
        self.assertTrue(any("research_cutoff is in the future" in e for e in result["errors"]))

    def test_overlapping_captions_refuse(self):
        m = fixture(self.image, SAMPLE_AUDIO)
        m["scenes"][0]["captions"][1]["start"] = 1.0
        result = self.inspect(m, True)
        self.assertFalse(result["valid"])
        self.assertTrue(any("overlapping" in e for e in result["errors"]))

    def test_silent_narration_refuses(self):
        m = fixture(self.image, SAMPLE_AUDIO)
        with patch.object(renderer, "speech_stats", return_value={"peak_dbfs": -90,
                "mean_dbfs": -90, "silence_fraction_at_minus50db": 1.0}):
            result = self.inspect(m, True)
        self.assertFalse(result["valid"])
        self.assertTrue(any("silent or mostly silent" in e for e in result["errors"]))

    def test_no_unjustified_reading_hold(self):
        m = fixture(self.image, SAMPLE_AUDIO)
        m["scenes"][0]["hold_after_seconds"] = 10
        result = self.inspect(m, True)
        self.assertFalse(result["valid"])
        self.assertTrue(any("hold_reason" in e for e in result["errors"]))

    def test_cue_clock_rollover(self):
        self.assertEqual(renderer.clock_text(59.9996), "00:01:00,000")
        self.assertEqual(renderer.clock_text(3661.25, vtt=True), "01:01:01.250")

    def test_identical_prompt_bytes_required(self):
        m = fixture(self.image, SAMPLE_AUDIO)
        m["fixture_only"] = False
        paths = []
        for model, prompt in (("unit-test-a", "same required"), ("unit-test-b", "different prompt")):
            payload = {"model": model, "messages": [{"role": "user", "content": prompt}]}
            canonical = json.dumps(payload["messages"], ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
            record = {"status": "completed", "usable_output": True,
                "provider": "unit-test-only", "requested_model": model, "origin": "live_provider_requests",
                "request_payload": payload, "prompt_sha256": renderer.hashlib.sha256(canonical).hexdigest(),
                "settings_verified": True, "raw_response": "Unit-test record, never model evidence",
                "output_text": "Unit-test record", "usage": {"input_tokens": 10, "output_tokens": 10},
                "cost": {"total_usd": "0.001", "basis": "published_tariff_calculation_only"}}
            path = self.directory / (model + ".json")
            path.write_text(json.dumps(record))
            paths.append(str(path))
        m["central_comparison"]["run_records"] = paths
        result = self.inspect(m)
        self.assertTrue(any("Comparison inputs differ" in e for e in result["errors"]))

    def test_blank_scene_refuses(self):
        blank = self.directory / "blank.png"
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi", "-i",
                        "color=c=black:s=1920x1080:d=0.1", "-frames:v", "1", str(blank)], check=True)
        result = self.inspect(fixture(blank, SAMPLE_AUDIO), True)
        self.assertFalse(result["valid"])
        self.assertTrue(any("blank or nearly uniform" in e for e in result["errors"]))

    def test_in_speech_hold_adds_no_silence(self):
        m = fixture(self.image, SAMPLE_AUDIO)
        m["scenes"][0].update(hold_during_narration=True, reading_hold_seconds_planned=20)
        result = self.inspect(m, True)
        self.assertTrue(result["valid"], result["errors"])
        self.assertEqual(result["reading_hold_seconds"], 0)
        self.assertAlmostEqual(result["runtime_seconds"], 7.6, places=2)

    def test_in_speech_hold_cannot_also_pad_audio(self):
        m = fixture(self.image, SAMPLE_AUDIO)
        m["scenes"][0].update(hold_during_narration=True, hold_after_seconds=20, hold_reason="Comparison held during narration")
        result = self.inspect(m, True)
        self.assertFalse(result["valid"])
        self.assertTrue(any("cannot also add" in e for e in result["errors"]))

    def test_excerpt_captions_clipped_and_shifted(self):
        manifest = {"scenes": [{"start_seconds": 100, "captions": [
            {"start": 0, "end": 3, "text": "Before excerpt"},
            {"start": 4, "end": 8, "text": "At excerpt start"},
            {"start": 10, "end": 16, "text": "At excerpt end"}]}]}
        cues = renderer.write_captions(manifest, self.directory, inpoint=105, duration=8, basename="excerpt-unit-test")
        self.assertEqual(cues, [(0, 3, "At excerpt start"), (5, 8, "At excerpt end")])
        self.assertIn("00:00:05,000 --> 00:00:08,000", (self.directory / "excerpt-unit-test.srt").read_text())


def smoke():
    ensure_samples()
    output = HERE / "smoke-test"
    output.mkdir(exist_ok=True)
    image = output / "sample.png"
    image.write_bytes(SAMPLE_IMAGE.read_bytes())
    manifest = output / "fixture-manifest.json"
    manifest.write_text(json.dumps(fixture(image, SAMPLE_AUDIO), indent=2) + "\n")
    report = renderer.render(manifest, output / "encoded", fixture=True)
    movie = output / "encoded" / "SMOKE_TEST_ONLY.mp4"
    decoded = renderer.probe(movie)
    types = {s["codec_type"] for s in decoded["streams"]}
    assert types == {"video", "audio", "subtitle"}, types
    video = next(s for s in decoded["streams"] if s["codec_type"] == "video")
    assert (video["width"], video["height"]) == (1920, 1080)
    assert abs(float(decoded["format"]["duration"]) - 7.6) < 0.15
    # Decode every frame/sample to catch corrupt streams. This is not human playback.
    renderer.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(movie), "-f", "null", "-"])
    subtitle_text = renderer.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(movie),
                                 "-map", "0:s:0", "-f", "srt", "-"])
    assert "00:00:02,300 --> 00:00:04,000" in subtitle_text
    assert "Welcome to AI Update." in subtitle_text
    print(json.dumps({"smoke_render_success": True, "complete_decode_success": True,
                      "embedded_caption_cues_verified": True, "duration_seconds": decoded["format"]["duration"],
                      "manual_playback_required": True, "movie": str(movie)}, indent=2))


if __name__ == "__main__":
    import sys
    if "--smoke" in sys.argv:
        smoke()
    else:
        unittest.main()
