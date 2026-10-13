#!/usr/bin/env python3
"""Evidence-gated, narration-led episode assembly. Python stdlib + FFmpeg only.

The renderer validates declared provenance, files and timing. It cannot independently
verify the truth of source claims or replace a complete human watch/listen review.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import pathlib
import re
import shlex
import subprocess
import sys
import textwrap
from zoneinfo import ZoneInfo

FPS = 30
WIDTH, HEIGHT = 1920, 1080
RATE = 48000


class RenderError(Exception):
    pass


def run(args: list[str], *, stderr=False) -> str:
    result = subprocess.run(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode:
        raise RenderError(f"Command failed ({result.returncode}): {shlex.join(args[:6])}\n{result.stderr[-6000:]}")
    return result.stderr if stderr else result.stdout


def probe(path: pathlib.Path) -> dict:
    return json.loads(run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)]))


def path_for(base: pathlib.Path, value: object, label: str) -> pathlib.Path:
    if not isinstance(value, str) or not value.strip():
        raise RenderError(f"{label}: missing path")
    p = pathlib.Path(value)
    p = p.resolve() if p.is_absolute() else (base / p).resolve()
    if not p.is_file() or p.stat().st_size == 0:
        raise RenderError(f"{label}: missing or empty file: {p}")
    return p


def sha256(path: pathlib.Path) -> str:
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def number(value: object, label: str, *, minimum=0.0) -> float:
    if isinstance(value, bool):
        raise RenderError(f"{label}: expected a number")
    try:
        result = float(value)
    except (ValueError, TypeError):
        raise RenderError(f"{label}: expected a number")
    if not math.isfinite(result) or result < minimum:
        raise RenderError(f"{label}: expected finite value >= {minimum}")
    return result


def timestamp(value: object, label: str) -> dt.datetime:
    try:
        parsed = dt.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        raise RenderError(f"{label}: expected ISO 8601 timestamp")
    if parsed.tzinfo is None:
        raise RenderError(f"{label}: timestamp must include timezone offset")
    return parsed


def speech_stats(path: pathlib.Path, duration: float) -> dict:
    output = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af",
                  "silencedetect=noise=-50dB:d=0.5,volumedetect", "-f", "null", "-"], stderr=True)
    max_match = re.search(r"max_volume: ([-\w.]+) dB", output)
    mean_match = re.search(r"mean_volume: ([-\w.]+) dB", output)
    peak = float(max_match.group(1)) if max_match else float("-inf")
    mean = float(mean_match.group(1)) if mean_match else float("-inf")
    silence = sum(float(v) for v in re.findall(r"silence_duration: ([\d.]+)", output))
    return {"peak_dbfs": peak, "mean_dbfs": mean, "silence_fraction_at_minus50db": min(1.0, silence / duration)}


def image_luminance_range(path: pathlib.Path) -> float:
    output = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-vf",
                  "scale=480:-1,signalstats,metadata=print", "-frames:v", "1", "-f", "null", "-"], stderr=True)
    low = re.search(r"lavfi.signalstats.YMIN=([\d.]+)", output)
    high = re.search(r"lavfi.signalstats.YMAX=([\d.]+)", output)
    if not low or not high:
        raise RenderError(f"Image blank-frame check failed: {path}")
    return float(high.group(1)) - float(low.group(1))


def make_caption_cues(text: str, duration: float) -> list[dict]:
    words = text.split()
    if not words:
        raise RenderError("Empty caption_text")
    chunks, current = [], []
    for word in words:
        candidate = " ".join(current + [word])
        if current and len(candidate) > 76:
            chunks.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        chunks.append(" ".join(current))
    total = sum(len(chunk.split()) for chunk in chunks)
    elapsed, result = 0.0, []
    for chunk in chunks:
        end = elapsed + duration * len(chunk.split()) / total
        result.append({"start": elapsed, "end": min(duration, end), "text": chunk})
        elapsed = end
    return result


def validate(manifest_path: pathlib.Path, *, fixture=False, now=None) -> tuple[dict, dict]:
    base = manifest_path.resolve().parent
    try:
        manifest = json.loads(manifest_path.read_text())
    except (OSError, json.JSONDecodeError) as e:
        raise RenderError(f"Cannot read manifest: {e}")
    errors, warnings = [], []
    try:
        tz = ZoneInfo(manifest.get("timezone", "America/New_York"))
    except Exception:
        raise RenderError("Invalid timezone")
    clock = now or dt.datetime.now(dt.timezone.utc)
    today = clock.astimezone(tz).date()
    if fixture and manifest.get("fixture_only") is not True:
        errors.append("Fixture mode requires fixture_only=true")
    if not fixture and manifest.get("fixture_only"):
        errors.append("Fixture manifests cannot render a final episode")
    for field in ("episode_id", "title"):
        if not isinstance(manifest.get(field), str) or not manifest[field].strip():
            errors.append(f"Missing {field}")
    cutoff = None
    try:
        cutoff = timestamp(manifest.get("research_cutoff"), "research_cutoff")
        if cutoff > clock:
            errors.append("research_cutoff is in the future")
        if not fixture and cutoff.astimezone(tz).date() != today:
            errors.append(f"Source cutoff is stale: expected local date {today}")
    except RenderError as e:
        errors.append(str(e))
    if not fixture and manifest.get("finalization_date") != str(today):
        errors.append(f"finalization_date must be actual local date {today}")
    claims = manifest.get("claims", [])
    if not isinstance(claims, list):
        errors.append("claims must be a list")
        claims = []
    claim_map = {}
    for c in claims:
        if not isinstance(c, dict):
            errors.append("Invalid claim record")
            continue
        cid = c.get("id")
        if not cid or cid in claim_map:
            errors.append(f"Missing or duplicate claim id: {cid}")
            continue
        claim_map[cid] = c
        if not fixture and (c.get("reviewed") is not True or not c.get("evidence_type")):
            errors.append(f"Claim {cid} lacks completed review or evidence origin")
        if not c.get("source_url") and not c.get("artifact_path"):
            errors.append(f"Claim {cid} lacks source_url or reproducible artifact_path")
        if c.get("artifact_path"):
            try:
                path_for(base, c["artifact_path"], f"Claim {cid}")
            except RenderError as e:
                errors.append(str(e))
        try:
            verified = timestamp(c.get("verified_at"), f"Claim {cid} verified_at")
            if cutoff and verified > cutoff:
                errors.append(f"Claim {cid} verification occurs after source cutoff")
            if not fixture and c.get("changeable", True) and verified.astimezone(tz).date() != today:
                errors.append(f"Changeable claim {cid} is not verified today")
        except RenderError as e:
            errors.append(str(e))
    if not fixture and not claims:
        errors.append("Final episode requires a nonempty claim ledger")
    scenes = manifest.get("scenes", [])
    if not isinstance(scenes, list) or not scenes:
        errors.append("scenes must be a nonempty list")
        scenes = []
    prepared, scene_ids = [], set()
    narration_total = hold_total = elapsed = 0.0
    for raw in scenes:
        if not isinstance(raw, dict):
            errors.append("Invalid scene record")
            continue
        sid = raw.get("id")
        if not sid or sid in scene_ids:
            errors.append(f"Missing or duplicate scene id: {sid}")
            continue
        scene_ids.add(sid)
        try:
            image = path_for(base, raw.get("image"), f"Scene {sid} image")
            if image.suffix.lower() not in (".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff", ".bmp", ".svg"):
                raise RenderError(f"Scene {sid}: this foundation renderer requires a still image, not a planned motion file")
            image_streams = [s for s in probe(image).get("streams", []) if s.get("codec_type") == "video"]
            if not image_streams or not image_streams[0].get("width") or not image_streams[0].get("height"):
                raise RenderError(f"Scene {sid}: image cannot be decoded")
            luminance_range = image_luminance_range(image)
            if luminance_range < 8:
                raise RenderError(f"Scene {sid}: image appears blank or nearly uniform")
            narration = path_for(base, raw.get("narration_wav"), f"Scene {sid} narration")
            if narration.suffix.lower() != ".wav":
                raise RenderError(f"Scene {sid}: actual narration must be WAV")
            audio_probe = probe(narration)
            if not any(s.get("codec_type") == "audio" for s in audio_probe.get("streams", [])):
                raise RenderError(f"Scene {sid}: narration has no audio stream")
            audio_duration = number(audio_probe["format"].get("duration"), f"Scene {sid} audio duration", minimum=0.1)
            stats = speech_stats(narration, audio_duration)
            if stats["peak_dbfs"] < -50 or stats["silence_fraction_at_minus50db"] >= 0.8:
                raise RenderError(f"Scene {sid}: narration is silent or mostly silent, cannot count as spoken runtime")
            hold = number(raw.get("hold_after_seconds", 0), f"Scene {sid} hold")
            if hold and not raw.get("hold_reason"):
                raise RenderError(f"Scene {sid}: reading hold requires hold_reason")
            if hold and raw.get("hold_during_narration"):
                raise RenderError(f"Scene {sid}: hold_during_narration cannot also add hold_after_seconds")
            duration = math.ceil((audio_duration + hold) * FPS - 1e-7) / FPS
            refs = raw.get("claim_ids", [])
            if not isinstance(refs, list):
                raise RenderError(f"Scene {sid}: claim_ids must be a list")
            if not fixture and raw.get("scene_type", "factual") == "factual" and not refs:
                raise RenderError(f"Scene {sid}: factual scene has no claim_ids")
            if any(cid not in claim_map for cid in refs):
                raise RenderError(f"Scene {sid}: unknown claim_ids")
            explicit = raw.get("captions")
            captions = explicit if explicit is not None else make_caption_cues(raw.get("caption_text", ""), audio_duration)
            if not isinstance(captions, list) or not captions:
                raise RenderError(f"Scene {sid}: captions must be nonempty")
            previous_end = 0.0
            clean_cues = []
            for cue in captions:
                start = number(cue.get("start"), f"Scene {sid} caption start")
                end = number(cue.get("end"), f"Scene {sid} caption end")
                text = cue.get("text", "")
                if start < previous_end - 0.001 or end <= start or end > audio_duration + 0.05:
                    raise RenderError(f"Scene {sid}: overlapping, unordered or out-of-audio caption times")
                if not isinstance(text, str) or not text.strip():
                    raise RenderError(f"Scene {sid}: empty caption")
                if len(text.replace("\n", " ")) > 84:
                    raise RenderError(f"Scene {sid}: caption exceeds 84 characters")
                lines = textwrap.wrap(text.replace("\n", " "), width=42)
                if len(lines) > 2:
                    raise RenderError(f"Scene {sid}: caption requires more than two readable lines")
                clean_cues.append({"start": start, "end": end, "text": "\n".join(lines)})
                previous_end = end
            if explicit is None:
                warnings.append(f"Scene {sid}: caption timing estimated by word count, requires alignment review")
            if not fixture and (explicit is None or raw.get("captions_verified") is not True):
                raise RenderError(f"Scene {sid}: explicit aligned cues with captions_verified=true required for final render")
            effects = []
            for effect in raw.get("sfx", []):
                p = path_for(base, effect.get("file"), f"Scene {sid} SFX")
                effect_duration = number(probe(p)["format"].get("duration"), f"Scene {sid} SFX duration", minimum=0.01)
                offset = number(effect.get("offset_seconds", 0), f"Scene {sid} SFX offset")
                gain = number(effect.get("gain_db", -18), f"Scene {sid} SFX gain", minimum=-80)
                if gain > -6:
                    raise RenderError(f"Scene {sid}: SFX gain must be <=-6 dB to preserve speech")
                if offset + effect_duration > duration + 0.005:
                    raise RenderError(f"Scene {sid}: SFX extends beyond its scene")
                effects.append({"file": str(p), "offset_seconds": offset, "gain_db": gain,
                                "duration_seconds": effect_duration, "sha256": sha256(p)})
            scene = dict(raw)
            scene.update(image=str(image), narration_wav=str(narration), captions=clean_cues,
                         audio_duration_seconds=audio_duration, duration_seconds=duration,
                         start_seconds=elapsed, end_seconds=elapsed + duration, sfx=effects,
                         audio_stats=stats, image_sha256=sha256(image), narration_sha256=sha256(narration))
            scene["image_luminance_range"] = luminance_range
            prepared.append(scene)
            elapsed += duration
            narration_total += audio_duration
            hold_total += hold
        except (RenderError, KeyError, TypeError, ValueError) as e:
            errors.append(str(e))
    if not fixture:
        comparison = manifest.get("central_comparison", {})
        if comparison.get("complete") is not True:
            errors.append("Essential central comparison is incomplete")
        comparison_ids = comparison.get("scene_ids", [])
        if not comparison_ids or any(sid not in scene_ids for sid in comparison_ids):
            errors.append("Central comparison scene_ids are missing or invalid")
        benchmark_ids = comparison.get("benchmark_claim_ids", [])
        if not benchmark_ids or any(cid not in claim_map for cid in benchmark_ids):
            errors.append("Central comparison needs valid benchmark_claim_ids")
        tests = comparison.get("run_records", [])
        if not isinstance(tests, list) or len(tests) < 2:
            errors.append("Central comparison requires at least two actual run_records")
            tests = []
        input_hashes, configurations = [], set()
        for record_path in tests:
            try:
                path = path_for(base, record_path, "Comparison run record")
                test = json.loads(path.read_text())
                if test.get("fixture_only"):
                    raise RenderError(f"{record_path}: fixture test cannot become factual model evidence")
                if test.get("status") != "completed" or not test.get("usable_output"):
                    raise RenderError(f"{record_path}: genuine comparison output did not complete")
                if not test.get("requested_model") or not test.get("provider"):
                    raise RenderError(f"{record_path}: model/provider missing")
                configurations.add((test["provider"], test["requested_model"]))
                origin = test.get("origin")
                if not origin and (path.parent / "started.json").is_file():
                    origin = json.loads((path.parent / "started.json").read_text()).get("origin")
                if origin not in ("live_provider_requests", "live_provider_request", "user_supplied_provider_export"):
                    raise RenderError(f"{record_path}: real provider request/export origin is missing")
                payload = test.get("request_payload", {})
                messages = payload.get("messages")
                if not isinstance(messages, list) or not messages:
                    raise RenderError(f"{record_path}: retained original prompt/messages missing")
                canonical = json.dumps(messages, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
                actual_prompt_hash = hashlib.sha256(canonical).hexdigest()
                if test.get("prompt_sha256") != actual_prompt_hash:
                    raise RenderError(f"{record_path}: prompt_sha256 does not match retained original messages")
                input_hashes.append(actual_prompt_hash)
                if test.get("settings_verified") is not True or payload.get("model") != test["requested_model"]:
                    raise RenderError(f"{record_path}: exact request settings are unverified")
                if not test.get("raw_response") or not test.get("output_text"):
                    raise RenderError(f"{record_path}: raw provider response/output missing")
                usage = test.get("usage", {})
                for key in ("input_tokens", "output_tokens"):
                    if type(usage.get(key)) is not int or usage[key] < 0:
                        raise RenderError(f"{record_path}: original provider usage {key} is missing")
                cost = test.get("cost", {})
                number(cost.get("total_usd"), f"{record_path}: supported attempt cost")
                if cost.get("basis") not in ("published_tariff_calculation_only", "actual_provider_bill"):
                    raise RenderError(f"{record_path}: supported cost basis is missing")
                if cost.get("basis") == "published_tariff_calculation_only":
                    warnings.append(f"{record_path}: cost is calculated from published tariffs, not an actual provider bill")
            except (RenderError, OSError, ValueError, TypeError, AttributeError) as e:
                errors.append(str(e))
        if input_hashes and len(set(input_hashes)) != 1:
            errors.append("Comparison inputs differ: identical canonical original prompt/messages required")
        if tests and len(configurations) < 2:
            errors.append("Comparison requires different provider/model configurations")
        if elapsed < 600:
            errors.append(f"Runtime {elapsed:.3f}s is below required 600s")
        if elapsed > 900 and not (manifest.get("extension_reason") or manifest.get("runtime_extension_reason")):
            errors.append(f"Runtime {elapsed:.3f}s exceeds 900s without justified extension reason")
        if hold_total > min(60, narration_total * 0.1) + 0.001:
            errors.append("Reading holds exceed 60 seconds or 10% of actual narration duration")
    if fixture and elapsed > 60:
        errors.append("Fixture render is limited to 60 seconds and cannot substitute for a full episode")
    report = {"schema_version": 1, "fixture_only": fixture, "valid": not errors,
              "errors": errors, "warnings": warnings, "validated_at": clock.isoformat(),
              "declared_source_cutoff": manifest.get("research_cutoff"), "timezone": str(tz),
              "scene_count": len(prepared), "runtime_seconds": round(elapsed, 6),
              "actual_narration_seconds": round(narration_total, 6), "reading_hold_seconds": hold_total,
              "manual_playback_required": True, "manual_playback_complete": False,
              "renderer_scope": "Still-frame and fade assembly foundation. visual_action and animation_timing remain plans unless implemented in source assets.",
              "machine_checks_do_not_prove": ["truth of declared evidence", "spoken transcript matches audio",
                  "natural voice or pronunciation", "complete watch/listen playback", "full-frame readability"]}
    manifest = dict(manifest)
    manifest["scenes"] = prepared
    return manifest, report


def write_json(path: pathlib.Path, content: dict):
    path.write_text(json.dumps(content, indent=2, ensure_ascii=False, allow_nan=False) + "\n")


def clock_text(seconds: float, *, vtt=False) -> str:
    ms = max(0, round(seconds * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02}{'.' if vtt else ','}{ms:03}"


def write_captions(manifest: dict, output: pathlib.Path, *, inpoint=0.0, duration=None, basename="captions"):
    cues = []
    for scene in manifest["scenes"]:
        for c in scene["captions"]:
            start = scene["start_seconds"] + c["start"]
            end = scene["start_seconds"] + c["end"]
            outpoint = inpoint + duration if duration is not None else math.inf
            if end <= inpoint or start >= outpoint:
                continue
            cues.append((max(start, inpoint) - inpoint, min(end, outpoint) - inpoint, c["text"]))
    srt, vtt = [], ["WEBVTT\n"]
    for i, (start, end, text) in enumerate(cues, 1):
        srt.append(f"{i}\n{clock_text(start)} --> {clock_text(end)}\n{text}\n")
        vtt.append(f"{clock_text(start, vtt=True)} --> {clock_text(end, vtt=True)}\n{text}\n")
    (output / (basename + ".srt")).write_text("\n".join(srt) + "\n")
    (output / (basename + ".vtt")).write_text("\n".join(vtt) + "\n")
    return cues


def concat_file(paths: list[pathlib.Path], target: pathlib.Path):
    # Concat demuxer has its own quoting. Escaped single quotes reopen the quoted path.
    target.write_text("".join("file '" + str(p.resolve()).replace("'", "'\\''") + "'\n" for p in paths))


def render(manifest_path: pathlib.Path, output: pathlib.Path, *, fixture=False, excerpt_start=0.0) -> dict:
    manifest, report = validate(manifest_path, fixture=fixture)
    output.mkdir(parents=True, exist_ok=True)
    write_json(output / "validation-report.json", report)
    if not report["valid"]:
        raise RenderError("Render refused:\n" + "\n".join(report["errors"]))
    if not fixture and (excerpt_start < 0 or excerpt_start + 120 > report["runtime_seconds"]):
        raise RenderError("Excerpt inpoint must leave exactly 120 seconds in the completed episode")
    cache = output / "scene-cache"
    cache.mkdir(exist_ok=True)
    log = []

    def ffmpeg(args):
        command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-y", *args]
        log.append(shlex.join(command))
        run(command)

    videos, voice_parts, fx_parts, cue_sheet = [], [], [], []
    for i, scene in enumerate(manifest["scenes"]):
        duration = scene["duration_seconds"]
        stem = f"{i:03d}-{re.sub('[^A-Za-z0-9_-]', '_', scene['id'])}"
        video, voice, fx = (cache / (stem + suffix) for suffix in (".mp4", "-narration.wav", "-sfx.wav"))
        # Fades are inside their own scene, never overlap another scene's narration/evidence.
        filters = f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease,pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2,setsar=1,format=yuv420p"
        filters += ",fade=t=in:st=0:d=0.18"
        if scene.get("hold_after_seconds", 0) >= 0.3:
            filters += f",fade=t=out:st={duration-0.18:.6f}:d=0.18"
        ffmpeg(["-loop", "1", "-framerate", str(FPS), "-i", scene["image"], "-t", f"{duration:.6f}",
                "-vf", filters, "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-threads", "2", str(video)])
        ffmpeg(["-i", scene["narration_wav"], "-af",
                f"aresample={RATE},aformat=channel_layouts=stereo,loudnorm=I=-18:TP=-2:LRA=11,aresample={RATE},apad,atrim=duration={duration:.6f}",
                "-ar", str(RATE), "-ac", "2", "-c:a", "pcm_s16le", str(voice)])
        args = ["-f", "lavfi", "-i", f"anullsrc=r={RATE}:cl=stereo:d={duration:.6f}"]
        for effect in scene["sfx"]:
            args += ["-i", effect["file"]]
        graphs, labels = [], ["[0:a]"]
        for j, effect in enumerate(scene["sfx"], 1):
            delay = round(effect["offset_seconds"] * 1000)
            graphs.append(f"[{j}:a]aresample={RATE},aformat=channel_layouts=stereo,volume={effect['gain_db']}dB,adelay={delay}|{delay}[fx{j}]")
            labels.append(f"[fx{j}]")
            cue_sheet.append({"scene_id": scene["id"], "time_seconds": scene["start_seconds"] + effect["offset_seconds"],
                              "file": effect["file"], "gain_db": effect["gain_db"], "sha256": effect["sha256"]})
        graphs.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0,atrim=duration={duration:.6f}[mix]")
        ffmpeg(args + ["-filter_complex", ";".join(graphs), "-map", "[mix]", "-ar", str(RATE), "-ac", "2", "-c:a", "pcm_s16le", str(fx)])
        videos.append(video)
        voice_parts.append(voice)
        fx_parts.append(fx)
    for paths, name, is_video in ((videos, "video", True), (voice_parts, "narration", False), (fx_parts, "sfx-only", False)):
        listing = cache / f"{name}-concat.txt"
        concat_file(paths, listing)
        suffix = ".mp4" if is_video else ".wav"
        ffmpeg(["-f", "concat", "-safe", "0", "-i", str(listing), "-c", "copy", str(output / (name + suffix))])
    ffmpeg(["-i", str(output / "narration.wav"), "-i", str(output / "sfx-only.wav"), "-filter_complex",
            "[0:a][1:a]amix=inputs=2:normalize=0,alimiter=limit=0.89:level=0:latency=1[mix]", "-map", "[mix]", "-ar", str(RATE),
            "-ac", "2", "-c:a", "pcm_s16le", str(output / "final-mix.wav")])
    write_captions(manifest, output)
    movie = output / ("SMOKE_TEST_ONLY.mp4" if fixture else "episode-1080p.mp4")
    ffmpeg(["-i", str(output / "video.mp4"), "-i", str(output / "final-mix.wav"), "-i", str(output / "captions.srt"),
            "-map", "0:v:0", "-map", "1:a:0", "-map", "2:s:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-c:s", "mov_text",
            "-metadata", f"title={manifest['title']}", "-metadata", "comment=Automated encode checks only. Complete watch/listen review required.",
            "-movflags", "+faststart", str(movie)])
    actual = probe(movie)
    actual_duration = float(actual["format"]["duration"])
    if abs(actual_duration - report["runtime_seconds"]) > 0.15:
        raise RenderError(f"Final duration mismatch: {actual_duration} versus {report['runtime_seconds']}")
    if not fixture and actual_duration < 600:
        raise RenderError("Encoded final episode is shorter than 600 seconds")
    if not fixture:
        write_captions(manifest, output, inpoint=excerpt_start, duration=120, basename="excerpt-120s")
        ffmpeg(["-ss", f"{excerpt_start:.6f}", "-i", str(movie), "-i", str(output / "excerpt-120s.srt"),
                "-t", "120", "-map", "0:v:0", "-map", "0:a:0", "-map", "1:s:0", "-c:s", "mov_text",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-threads", "2", "-c:a", "aac", "-b:a", "192k",
                "-movflags", "+faststart", str(output / "excerpt-120s.mp4")])
        excerpt_duration = float(probe(output / "excerpt-120s.mp4")["format"]["duration"])
        if abs(excerpt_duration - 120) > 0.1:
            raise RenderError(f"Excerpt duration mismatch: {excerpt_duration}")
        report["excerpt"] = {"inpoint_seconds": excerpt_start, "duration_seconds": excerpt_duration,
                             "source_file": movie.name, "derived_from_full_episode_export": True,
                             "manual_playback_required": True}
    report.update(encoded_duration_seconds=actual_duration, encoded_video_file=movie.name,
                  final_mix_audio_stats=speech_stats(output / "final-mix.wav", actual_duration),
                  render_success=True, manual_playback_required=True, manual_playback_complete=False)
    finished = dt.datetime.now(dt.timezone.utc)
    report["render_finished_at"] = finished.isoformat()
    finished_date = finished.astimezone(ZoneInfo(manifest["timezone"])).date()
    cutoff_date = timestamp(manifest["research_cutoff"], "research_cutoff").astimezone(ZoneInfo(manifest["timezone"])).date()
    if not fixture and cutoff_date != finished_date:
        report["valid"] = False
        report["errors"].append("Production crossed local midnight: refresh changeable evidence before final delivery")
        write_json(output / "validation-report.json", report)
        raise RenderError(report["errors"][-1])
    write_json(output / "resolved-manifest.json", manifest)
    write_json(output / "validation-report.json", report)
    write_json(output / "sfx-cue-sheet.json", {"cues": cue_sheet})
    (output / "assembly-commands.sh").write_text("#!/bin/sh\nset -eu\n" + "\n".join(log) + "\n")
    (output / "MANUAL_REVIEW_REQUIRED.txt").write_text(
        "Machine checks establish file decoding, declared evidence fields, measured audio timing and encode dimensions.\n"
        "They do not prove evidence truth, accurate pronunciation, transcript/audio agreement or complete playback.\n"
        "Before publication watch and listen to the entire final MP4. Review all factual frames at full resolution,\n"
        "captions, transitions, sound cues, audio levels, licenses and comparison fields. Record actual checks.\n"
        "A fixture smoke test is infrastructure validation only and is never a completed episode.\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["validate", "render-final", "render-fixture"])
    parser.add_argument("manifest", type=pathlib.Path)
    parser.add_argument("--output", type=pathlib.Path)
    parser.add_argument("--excerpt-start", type=float, default=0.0)
    args = parser.parse_args()
    try:
        if args.command == "validate":
            _, report = validate(args.manifest)
            if args.output:
                args.output.mkdir(parents=True, exist_ok=True)
                write_json(args.output / "validation-report.json", report)
        else:
            if not args.output:
                parser.error("--output is required for rendering")
            report = render(args.manifest, args.output, fixture=args.command == "render-fixture", excerpt_start=args.excerpt_start)
        print(json.dumps(report, indent=2, allow_nan=False))
        return 0 if report["valid"] else 2
    except RenderError as e:
        print(str(e), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
