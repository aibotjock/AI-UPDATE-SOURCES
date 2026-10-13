# Narration-led renderer

This is a still-frame and fade assembly foundation using existing checked scene images and actual narration WAV files. It creates no episode facts, comparison outputs, voice recording, or sources. It uses only Python's standard library, FFmpeg and FFprobe. Fields such as `visual_action` and `animation_timing` are production plans. This tool does not implement the full animated explainer treatment or platform recordings.

```bash
python render_episode.py validate /absolute/path/episode-manifest.json --output /absolute/path/diagnostics
python render_episode.py render-final /absolute/path/episode-manifest.json --output /absolute/path/exports --excerpt-start 280
python -m unittest -v test_renderer.py
python test_renderer.py --smoke
```

Paths inside a manifest resolve relative to the manifest file. The final renderer refuses incomplete evidence, stale date fields, missing files, empty or nearly uniform scenes, silent or mostly silent narration, incomplete comparisons, unverified caption timing, and a runtime below 600 seconds. A runtime above 900 seconds needs a nonempty `extension_reason` (`runtime_extension_reason` is also accepted). Silent reading holds require a reason and total at most 60 seconds or 10% of narration duration overall. Reading holds during narration add no silent duration and have no arbitrary per-scene cap. Only actual measured audio and justified silent holds count toward runtime. Planned durations do not affect rendering.

The final gate checks declarations and retained artifacts. It does not independently establish source truth or that a model produced a recorded output. Research and factual review remain necessary. If export crosses local midnight, the renderer marks the result invalid and requires refreshed changeable evidence before delivery. `hold_during_narration=true` describes a static reading hold while speech continues and adds no silent duration. Use `hold_after_seconds` only for a separately justified silent reading hold.

## Manifest

```json
{
  "schema_version": 1,
  "episode_id": "01",
  "title": "AI Benchmarks Explained",
  "timezone": "America/New_York",
  "research_cutoff": "2026-10-13T05:00:00-04:00",
  "finalization_date": "2026-10-13",
  "claims": [{
    "id": "C001",
    "source_url": "https://original-publisher.example/methodology",
    "verified_at": "2026-10-13T04:55:00-04:00",
    "changeable": true,
    "reviewed": true,
    "evidence_type": "independent-methodology"
  }],
  "central_comparison": {
    "complete": false,
    "scene_ids": ["S13"],
    "benchmark_claim_ids": ["C001"],
    "run_records": []
  },
  "scenes": [{
    "id": "S13",
    "scene_type": "factual",
    "image": "scenes/S13.png",
    "narration_wav": "audio/S13.wav",
    "claim_ids": ["C001"],
    "captions_verified": false,
    "captions": [{"start": 0.0, "end": 3.5, "text": "Caption matching the actual narration."}],
    "hold_after_seconds": 2,
    "hold_reason": "Readable completed comparison",
    "sfx": [{"file": "audio/reveal.wav", "offset_seconds": 1.2, "gain_db": -18}]
  }]
}
```

The example deliberately cannot pass final production. It has no actual comparison test runs, incomplete comparison and unreviewed captions. Replace paths, dates and contents with genuine checked artifacts.

Central-comparison `run_records` is a list of paths to original attempt JSON files written by `compare.py`. At least two different provider/model configurations are required. Each record must contain completed usable output, retained `request_payload.messages`, matching `prompt_sha256`, `provider`, `requested_model`, `settings_verified=true`, raw response and output text, original usage counts and supported `cost.total_usd`/`cost.basis`. The renderer recomputes prompt hashes from original messages and checks they are identical. Declared live-request or actual provider-export origin is required. Older live records can retain origin in sibling `started.json`. Calculated tariff costs remain labelled as calculations and do not establish actual bills. Include all attempts and preserve retry/failure accounting in the comparison evidence; a selected attempt cost alone does not establish total task cost. `scene_ids` identify the held simultaneous comparison. `benchmark_claim_ids` reference compatible benchmark evidence. Artifacts may use an `artifact_path` instead of `source_url` in a claim record, with an exact `verified_at` timestamp.

Every factual scene needs valid claim IDs. Branding and editorial scenes may use `scene_type` of `branding` or `editorial`. Every scene needs genuine nonempty image and narration files and nonempty readable captions. Explicit captions use times relative to the narration WAV and must remain inside it. Set `captions_verified=true` only after checking alignment to the actual recording. A `caption_text` field can generate estimated word-weighted cues for fixture previews, but estimated timing cannot pass final rendering.

## Outputs and review

Final rendering produces `episode-1080p.mp4`, a 120-second `excerpt-120s.mp4` extracted at the selected inpoint, narration and SFX stems, final mixed WAV, SRT/VTT, SFX cue sheet, resolved manifest, diagnostics, scene cache and exact assembly commands. The excerpt derives from the settled movie and includes no separately authored facts. Its inpoint must leave 120 seconds in the full episode. Captions travel inside the main MP4 as a selectable subtitle track, with separate SRT/VTT files.

Images preserve their aspect ratio and fit inside a full 1920×1080 frame. Fades remain within scenes, with no overlap between different scenes' narration or evidence. There is a 0.18-second entrance fade and a matching exit fade only when a reading hold leaves room. Narration receives per-scene loudness normalization to -18 LUFS, a -2 dB true-peak target and a limiter during the final mix. These settings help control levels but do not certify intelligibility or listening quality. Separate stems retain editability.

`manual_playback_required` always remains true in machine reports. Machine decoding, audio-level checks, measured duration and frame dimensions do not prove complete playback, pronunciation, voice naturalness, factual correctness, transcript/audio agreement, caption synchronization or readability. Watch and listen to the entire final MP4 and record the checks actually performed before publication.

The separate `render-fixture` command requires `fixture_only=true`, permits at most 60 seconds and names the movie `SMOKE_TEST_ONLY.mp4`. It exists solely to validate infrastructure, never to substitute for a complete episode. The offline smoke test uses locally regenerated free infrastructure fixtures, decodes every frame/sample, checks 1080p dimensions and inspects embedded caption timing. No ten-minute fake episode is created.
