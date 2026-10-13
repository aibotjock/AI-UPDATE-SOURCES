#!/usr/bin/env python3
"""Generate a dated production brief; validate recorded workflow prerequisites.

This program does not research, write the final script, render, or verify playback.
Validation checks records and files, not whether recorded human claims are true.
"""

import argparse
import hashlib
import json
import math
import re
import shutil
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ZONE = ZoneInfo("America/New_York")
REFERENCES = (
    "references/source-registry.json", "library/asset-index.json", "library/INDEX.md",
    "channel/series-master-prompt.txt", "channel/episode-formula.txt",
    "channel/channel-description.txt", "channel/continuity.json",
    "channel/source-review-policy.md", "channel/evolution-policy.md",
)
STAGES = ("prompt_generated", "researched", "script_finalized", "rendered")


def local_now(now=None):
    value = now or datetime.now(ZONE)
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("The generation clock must include a timezone.")
    return value.astimezone(ZONE)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def read_json(path):
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.name} must contain a JSON object.")
    return value


def generate(repo_root, output_root, episode, include_lesson=False, now=None):
    """Only tests inject a clock; the CLI always uses the actual local clock."""
    clock = local_now(now)
    day = clock.date().isoformat()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,39}", episode):
        raise ValueError("Episode ID must use 1–40 letters, digits, hyphens or underscores.")
    canonical = Path(repo_root)
    texts = {name: (canonical / name).read_text(encoding="utf-8") for name in REFERENCES}
    continuity = json.loads(texts["channel/continuity.json"])
    if not isinstance(continuity, dict):
        raise ValueError("continuity.json must contain a JSON object.")
    folder = Path(output_root) / day / episode
    folder.parent.mkdir(parents=True, exist_ok=True)
    folder.mkdir()  # Deliberately fails if this dated episode ID already exists.
    try:
        snapshots = folder / "reference-snapshot"
        snapshots.mkdir()
        for name, contents in texts.items():
            (snapshots / name).parent.mkdir(parents=True, exist_ok=True)
            (snapshots / name).write_text(contents, encoding="utf-8")
        optional = (
            "\nPractical lesson selected: include one only for a special occasion featuring "
            "the best and/or new items. Fit it within the agreed runtime and explain its value.\n"
            if include_lesson else ""
        )
        prompt = f"""# AI UPDATE — episode {episode} production brief

Generation date: {day} (America/New_York).
Generated at: {clock.isoformat()}.
This is a generated production brief. Research, comparison, final script, video,
and playback remain pending; do not claim this brief completes any of them.

Read references/source-registry.json, library/asset-index.json and library/INDEX.md
first; use this repository's library and technology sources to select the episode.
Their generation-day snapshots are available relative to this episode folder at
reference-snapshot/references/source-registry.json,
reference-snapshot/library/asset-index.json and reference-snapshot/library/INDEX.md.
Read these files as needed; their full catalogs are deliberately outside this prompt.
Read relevant data, provenance, reproducibility and correction records next, then
apply the channel continuity documents. The snapshots preserve generation-day
context; a registry entry or successful access check does not establish current
reliability. Review each source's authority for the specific claim, independently
validate where needed, and follow retirement/replacement status and history.
Open and verify actual primary-source content; access checks alone are insufficient.
Before writing the script, conduct fresh research on {day} in America/New_York.
Record real source URLs, dates, supported claims and same-day verification in
evidence-ledger.json. Do not fabricate research or backdate the episode.
Copy source_record_template into sources only after completing its checks; the
template itself is pending metadata and is never evidence.
Each source record needs title, url, kind (news/benchmark/documentation/other),
claims (a list), content_verified (true only after reading), authority_note,
independent_validation (record the check or explain why it was unnecessary),
verified_at (timestamp with timezone), and published_date (ISO date or null).
Only regularly updated sources qualify: record regularly_updated_verified and
recent_maintenance_verified as true only after checking actual update history.
Record update_cadence as an observed pattern, never an invented schedule;
provide update_history_url or dated maintenance_evidence records (date and note),
last_updated_at (known ISO date or aware timestamp), and maintenance_checked_at
(today's aware timestamp). Pending registry candidates need these checks too.
The registry's regular_updates_verified is prior catalog review; the episode's
regularly_updated_verified requires a fresh check today, with no automatic promotion.
Recent benchmark results may repeat across days: keep their original benchmark
dates in original_benchmark_date, reverify them today, and describe them accurately
as the latest available. A dated benchmark must come from a maintained collection;
an old static paper alone does not satisfy the regularly updated source rule.

For the standard same-prompt comparison, record one shared prompt and actual
results from at least two models/tools in same-prompt-comparison.json. Authorized
existing account/API access may be used. Record provider, exact model/version/mode,
settings, actual result, and usage_cost for each run. usage_cost needs usage, note,
cost_basis (measured, estimated, subscription_not_allocated, or unavailable),
total and currency. Use numeric totals/currency where known; label estimates and
their basis. Do not invent a subscription's per-prompt allocation. Compare paid
model prices when relevant. Do not make purchases or new paid commitments without
explicit approval, and do not publish a video. Record observations and choice.
Record comparison_reviewed_at as today's aware review timestamp before script
creation, separate from each run's original aware run_at. Set evidence_origin to
new_run or reused_run. New runs must occur during today's production, between
research start and comparison review. Reused runs must preserve the original
timestamp and retain evidence_reference plus reuse_review_note explaining why
the shared prompt, task, model/version/mode and settings remain valid today.
Never relabel an older run as newly executed; same-day review is not a new run.

Narration identity: Dr. Chris, with no surname. Images use the AI UPDATE brand
only. Use these five standard roles for a 12-minute episode:
1. Main takeaway — 0:30.
2. What changed — 2:45.
3. Benchmark — 2:30.
4. Same-prompt comparison — 4:00.
5. Choice / what next — 2:15.
Keep runtime between 10 and 15 minutes, never below 10. A rare extension beyond
15 minutes requires an explicit written justification.
{optional}
Keep episode-status.json honest. Advance its stage only after completing the
required work and recording the corresponding evidence, files and timestamps.
A rendered claim additionally requires manual full playback with watch/listen
verification and notes, bound to the video hash. Decoder checks may establish
file integrity but do not complete the manual playback requirement.
The validator checks recorded prerequisites; it cannot verify factual claims,
estimate runtime from a script, inspect video duration, or perform playback.

## Frozen channel references
"""
        for name, contents in texts.items():
            if not name.startswith("channel/"):
                continue
            prompt += f"\n### {name}\n\n{contents.rstrip()}\n"
        (folder / "prompt.md").write_text(prompt, encoding="utf-8")
        write_json(folder / "evidence-ledger.json", {
            "schema_version": 1, "episode_date": day,
            "research_started_at": None, "research_completed_at": None, "sources": [],
            "source_record_template": {
                "title": None, "url": None, "kind": None, "claims": [],
                "published_date": None, "original_benchmark_date": None, "verified_at": None,
                "content_verified": False, "authority_note": None, "independent_validation": None,
                "regularly_updated_verified": False, "recent_maintenance_verified": False,
                "update_cadence": None, "update_history_url": None, "maintenance_evidence": [],
                "last_updated_at": None, "maintenance_checked_at": None,
            },
        })
        write_json(folder / "same-prompt-comparison.json", {
            "schema_version": 1, "episode_date": day, "comparison_reviewed_at": None,
            "prompt": None, "runs": [], "observations": [], "choice": None,
            "run_record_template": {
                "provider": None, "model": None, "version": None, "mode": None,
                "run_at": None, "evidence_origin": None, "evidence_reference": None,
                "reuse_review_note": None,
                "settings": {}, "result": None, "usage_cost": {
                    "usage": None, "cost_basis": "unavailable", "total": None,
                    "currency": None, "note": None,
                },
            },
        })
        write_json(folder / "episode-status.json", {
            "schema_version": 1, "episode_id": episode, "episode_date": day,
            "timezone": "America/New_York", "generated_at": clock.isoformat(),
            "series_version": continuity.get("series_version"), "stage": STAGES[0],
            "practical_lesson_included": bool(include_lesson),
            "reference_sha256": {name: digest(snapshots / name) for name in REFERENCES},
            "script_path": None, "script_sha256": None, "script_created_at": None, "script_finalized_at": None,
            "duration_seconds": None, "duration_extension_reason": None,
            "video_path": None, "video_sha256": None, "rendered_at": None,
            "render_script_sha256": None, "playback_video_sha256": None,
            "playback_verified_at": None, "playback_method": None, "playback_notes": None,
        })
    except Exception:
        shutil.rmtree(folder)
        raise
    return folder


def validate(folder, now=None):
    """Fail closed on missing or inconsistent prerequisites; return the stage."""
    folder = Path(folder).resolve()
    clock = local_now(now)

    def require(condition, message):
        if not condition:
            raise ValueError(message)

    def nonempty(value):
        return isinstance(value, str) and bool(value.strip())

    def timestamp(value, label, same_day=False):
        require(nonempty(value), f"{label} is required.")
        stamp = local_now(datetime.fromisoformat(value))
        require(stamp <= clock, f"{label} cannot be in the future.")
        if same_day:
            require(stamp.date().isoformat() == day, f"{label} must match the episode's local date.")
        return stamp

    def artifact(relative, expected_hash, label):
        require(nonempty(relative), f"{label} path is required.")
        path = (folder / relative).resolve()
        require(path.is_relative_to(folder), f"{label} must be inside the episode folder.")
        require(path.is_file() and path.stat().st_size > 0, f"{label} file is missing or empty.")
        require(expected_hash == digest(path), f"{label} SHA-256 does not match its file.")
        return path

    status = read_json(folder / "episode-status.json")
    require(status.get("schema_version") == 1, "Unsupported status schema.")
    day = status.get("episode_date")
    require(nonempty(day) and date.fromisoformat(day).isoformat() == day, "Invalid episode_date.")
    require(status.get("timezone") == "America/New_York", "Incorrect episode timezone.")
    generated = timestamp(status.get("generated_at"), "generated_at", True)
    require(status.get("stage") in STAGES, "Unknown episode stage.")
    level = STAGES.index(status["stage"])
    require(type(status.get("practical_lesson_included")) is bool, "Lesson selection must be boolean.")
    for name in ("prompt.md", "evidence-ledger.json", "same-prompt-comparison.json"):
        require((folder / name).is_file() and (folder / name).stat().st_size > 0, f"Missing {name}.")
    hashes = status.get("reference_sha256")
    require(isinstance(hashes, dict) and set(hashes) == set(REFERENCES), "Reference hashes are incomplete.")
    for name in REFERENCES:
        artifact("reference-snapshot/" + name, hashes[name], "Reference " + name)
    ledger = read_json(folder / "evidence-ledger.json")
    comparison = read_json(folder / "same-prompt-comparison.json")
    require(ledger.get("schema_version") == 1 and comparison.get("schema_version") == 1,
            "Unsupported ledger or comparison schema.")
    require(ledger.get("episode_date") == day and comparison.get("episode_date") == day,
            "Ledger and comparison dates must match the episode date.")

    # A lower stage must not simultaneously contain final-state claims.
    if level < 2:
        require(status.get("script_finalized_at") is None, "Script finalization requires script_finalized stage.")
    if level < 3:
        require(status.get("rendered_at") is None and status.get("playback_verified_at") is None,
                "Render/playback claims require rendered stage.")
    if level == 0:
        require(ledger.get("research_completed_at") is None,
                "Completed research requires researched stage.")
        return status["stage"]

    started = timestamp(ledger.get("research_started_at"), "research_started_at", True)
    completed = timestamp(ledger.get("research_completed_at"), "research_completed_at", True)
    require(generated <= started <= completed, "Research must occur after generation, in chronological order.")
    sources = ledger.get("sources")
    require(isinstance(sources, list) and bool(sources), "Researched stage requires source evidence.")
    for source in sources:
        require(isinstance(source, dict), "Each source must be an object.")
        require(nonempty(source.get("title")) and nonempty(source.get("url"))
                and source["url"].startswith(("https://", "http://")), "Each source needs a title and URL.")
        require(isinstance(source.get("claims"), list) and bool(source["claims"])
                and all(nonempty(claim) for claim in source["claims"]), "Each source needs supported claims.")
        require(source.get("content_verified") is True and nonempty(source.get("authority_note"))
                and nonempty(source.get("independent_validation")),
                "Each source needs content verification, claim authority and independent-validation notes.")
        verified = timestamp(source.get("verified_at"), "source verified_at", True)
        require(started <= verified <= completed, "Source verification must occur during recorded research.")
        require(source.get("regularly_updated_verified") is True
                and source.get("recent_maintenance_verified") is True
                and nonempty(source.get("update_cadence")),
                "Each source requires verified regular updates, recent maintenance and observed cadence.")
        checked = timestamp(source.get("maintenance_checked_at"), "maintenance_checked_at", True)
        require(started <= checked <= completed, "Maintenance checks must occur during recorded research.")
        history = source.get("update_history_url")
        evidence = source.get("maintenance_evidence")
        has_history = nonempty(history) and history.startswith(("https://", "http://"))
        if evidence:
            require(isinstance(evidence, list) and all(isinstance(item, dict) and nonempty(item.get("note"))
                    and nonempty(item.get("date")) and date.fromisoformat(item["date"]) <= checked.date()
                    for item in evidence), "Maintenance evidence needs actual dates and notes.")
        require(has_history or bool(evidence), "Each source needs update history or dated maintenance evidence.")
        updated = source.get("last_updated_at")
        require(nonempty(updated), "Each source needs last_updated_at.")
        if len(updated) == 10:
            require(date.fromisoformat(updated) <= checked.date(), "Last update cannot be in the future.")
        else:
            require(timestamp(updated, "last_updated_at") <= checked, "Last update must precede its check.")
        published = source.get("published_date")
        if published is not None:
            require(date.fromisoformat(published) <= verified.date(), "Source publication date cannot be in the future.")
        require(source.get("kind") in ("news", "benchmark", "documentation", "other"), "Each source needs a valid kind.")
        if source["kind"] == "benchmark":
            original = source.get("original_benchmark_date")
            require(nonempty(original) and date.fromisoformat(original) <= verified.date(),
                    "Benchmarks require their original date, even when repeated.")
    if level == 1:
        return status["stage"]

    created = timestamp(status.get("script_created_at"), "script_created_at", True)
    finalized = timestamp(status.get("script_finalized_at"), "script_finalized_at", True)
    require(completed <= created <= finalized, "Fresh research must finish before script creation and finalization.")
    reviewed = timestamp(comparison.get("comparison_reviewed_at"), "comparison_reviewed_at", True)
    require(started <= reviewed <= created, "Comparison review must occur during production, before script creation.")
    runs = comparison.get("runs")
    require(nonempty(comparison.get("prompt")) and isinstance(runs, list) and len(runs) >= 2,
            "Final script requires a recorded shared prompt and at least two comparison runs.")
    for run in runs:
        require(isinstance(run, dict) and all(nonempty(run.get(field)) for field in
                ("provider", "model", "version", "mode", "result")) and isinstance(run.get("settings"), dict),
                "Each run needs provider, exact model/version/mode, settings and actual result.")
        require(run.get("prompt", comparison["prompt"]) == comparison["prompt"],
                "Comparison runs must use exactly the shared prompt.")
        origin = run.get("evidence_origin")
        require(origin in ("new_run", "reused_run"), "Each run needs evidence_origin new_run or reused_run.")
        run_at = timestamp(run.get("run_at"), "run_at", origin == "new_run")
        require(run_at <= reviewed, "Original run timestamps must precede comparison review.")
        if origin == "new_run":
            require(started <= run_at, "New runs must occur during today's recorded production.")
        else:
            require(nonempty(run.get("evidence_reference")) and nonempty(run.get("reuse_review_note")),
                    "Reused runs require retained evidence_reference and a current task/configuration reuse_review_note.")
        cost = run.get("usage_cost")
        require(isinstance(cost, dict) and cost.get("cost_basis") in
                ("measured", "estimated", "subscription_not_allocated", "unavailable")
                and bool(cost.get("usage")) and nonempty(cost.get("note")),
                "Each run needs an honest usage/cost record and basis.")
        total = cost.get("total")
        if cost["cost_basis"] in ("measured", "estimated"):
            require(type(total) in (int, float) and math.isfinite(total) and total >= 0
                    and nonempty(cost.get("currency")), "Known/estimated costs need numeric totals and currency.")
        else:
            require(total is None, "Unavailable/unallocated per-prompt costs must remain null.")
    require(len({tuple(run[field].strip().casefold() for field in ("provider", "model", "version", "mode"))
                 for run in runs}) >= 2, "Comparison requires distinct models/tools or modes.")
    require(isinstance(comparison.get("observations"), list) and bool(comparison["observations"])
            and all(nonempty(item) for item in comparison["observations"])
            and nonempty(comparison.get("choice")), "Comparison needs observations and a choice.")
    artifact(status.get("script_path"), status.get("script_sha256"), "Script")
    seconds = status.get("duration_seconds")
    require(type(seconds) in (int, float) and math.isfinite(seconds) and seconds >= 600,
            "Episode runtime must be at least 10 minutes and finite.")
    require(seconds <= 900 or nonempty(status.get("duration_extension_reason")),
            "Runtime over 15 minutes requires an explicit extension justification.")
    if level == 2:
        return status["stage"]

    rendered = timestamp(status.get("rendered_at"), "rendered_at")
    playback = timestamp(status.get("playback_verified_at"), "playback_verified_at")
    require(finalized <= rendered <= playback, "Render and playback timestamps must follow script finalization.")
    artifact(status.get("video_path"), status.get("video_sha256"), "Video")
    require(status.get("render_script_sha256") == status.get("script_sha256"),
            "Render record must identify the finalized script hash.")
    require(status.get("playback_video_sha256") == status.get("video_sha256"),
            "Playback record must identify the verified video hash.")
    require(status.get("playback_method") == "manual_full_playback",
            "Rendered stage requires manual full watch/listen playback; decoder checks alone are insufficient.")
    require(nonempty(status.get("playback_notes")), "Rendered stage requires playback verification notes.")
    return status["stage"]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("generate", help="Generate today's production brief and pending records.")
    create.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    create.add_argument("--output-root", type=Path)
    create.add_argument("--episode", required=True)
    create.add_argument("--include-practical-lesson", action="store_true")
    check = commands.add_parser("validate", help="Check recorded prerequisites; does not verify claims or playback.")
    check.add_argument("folder", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "generate":
            result = generate(args.repo_root, args.output_root or args.repo_root / "episodes",
                              args.episode, args.include_practical_lesson)
            print(f"Generated production brief: {result}")
        else:
            stage = validate(args.folder)
            print(f"Recorded prerequisites valid for {stage}. Claims and playback require human verification.")
    except (OSError, ValueError, TypeError, KeyError) as error:
        parser.exit(1, f"Error: {error}\n")


if __name__ == "__main__":
    main()
