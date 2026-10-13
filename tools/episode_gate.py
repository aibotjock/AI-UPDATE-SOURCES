#!/usr/bin/env python3
"""Check evidence readiness without claiming human editorial/playback review."""
import argparse
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
from zoneinfo import ZoneInfo


def timestamp(value):
    parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp needs a timezone")
    return parsed


def check(manifest, base, stage="research", now=None):
    errors = []
    zone = ZoneInfo(manifest.get("timezone", "America/New_York"))
    now = now or dt.datetime.now(zone)
    today = now.astimezone(zone).date()
    try:
        cutoff = timestamp(manifest["research_cutoff"])
        if cutoff > now:
            errors.append("Research cutoff is in the future")
        if cutoff.astimezone(zone).date() != today:
            errors.append("Refresh changeable evidence for today's local date")
    except (ValueError, KeyError, TypeError):
        cutoff = None
        errors.append("Research cutoff must be a real timezone-aware timestamp")
    claims = manifest.get("claims", [])
    claim_ids = [claim.get("id") for claim in claims]
    if not claims:
        errors.append("No claim-level evidence ledger")
    if len(set(claim_ids)) != len(claim_ids) or None in claim_ids:
        errors.append("Claim IDs must be unique and present")
    for claim in claims:
        prefix = str(claim.get("id", "unknown"))
        if not claim.get("source_url", "").startswith("https://"):
            errors.append(prefix + ": missing original source URL")
        if claim.get("reviewed") is not True:
            errors.append(prefix + ": claim review is incomplete")
        if claim.get("changeable"):
            try:
                verified = timestamp(claim["verified_at"])
                if verified > now or (cutoff and verified > cutoff) or verified.astimezone(zone).date() != today:
                    errors.append(prefix + ": mutable claim needs today's verification")
            except (KeyError, ValueError, TypeError):
                errors.append(prefix + ": missing verification timestamp")
        if not claim.get("evidence_type"):
            errors.append(prefix + ": evidence origin is missing")
    comparison = manifest.get("central_comparison", {})
    if comparison.get("complete") is not True:
        errors.append("Required real same-prompt comparison is incomplete")
    run_paths = comparison.get("run_records", [])
    if len(run_paths) < 2:
        errors.append("Need at least two original model run records")
    prompt_hashes = set()
    resolved_models = set()
    for relative in run_paths:
        path = (base / relative).resolve()
        try:
            path.relative_to(base.resolve())
            run = json.loads(path.read_text())
            if run.get("origin") not in ("live_provider_requests", "user_supplied_provider_export") or run.get("test_fixture"):
                errors.append(str(relative) + ": real provider evidence origin is missing")
            payload = run.get("request_payload", {})
            actual_hash = hashlib.sha256(json.dumps(payload.get("messages"), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            if not payload.get("messages") or actual_hash != run.get("prompt_sha256"):
                errors.append(str(relative) + ": original request does not match prompt hash")
            if run.get("settings_verified") is not True:
                errors.append(str(relative) + ": exact request settings are unverified")
            try:
                observed = timestamp(run["observed_at_utc"])
                if observed > now or (cutoff and observed > cutoff):
                    errors.append(str(relative) + ": run occurred after research cutoff")
            except (KeyError, ValueError, TypeError):
                errors.append(str(relative) + ": original run timestamp is missing")
            usage = run.get("usage")
            if not isinstance(usage, dict) or not usage.get("raw") or any(type(usage.get(k)) is not int or usage[k] < 0 for k in ("input_tokens", "output_tokens")):
                errors.append(str(relative) + ": provider usage evidence is missing")
            if run.get("status") != "completed":
                errors.append(str(relative) + ": run did not complete")
            if not run.get("raw_response"):
                errors.append(str(relative) + ": original response is missing")
            if not run.get("prompt_sha256"):
                errors.append(str(relative) + ": prompt hash is missing")
            prompt_hashes.add(run.get("prompt_sha256"))
            resolved_models.add((run.get("provider"), run.get("requested_model")))
            if not run.get("requested_model") or not run.get("provider"):
                errors.append(str(relative) + ": model/provider is missing")
            if not run.get("cost") or run["cost"].get("total_usd") is None:
                errors.append(str(relative) + ": supported task cost is missing")
            else:
                try:
                    cost = float(run["cost"]["total_usd"])
                    if not math.isfinite(cost) or cost < 0:
                        raise ValueError("invalid cost")
                    if run["cost"].get("basis") not in ("published_tariff_calculation_only", "provider_billed_charge"):
                        errors.append(str(relative) + ": task cost basis is incomplete or an upper bound")
                except (ValueError, TypeError):
                    errors.append(str(relative) + ": cost must be finite and nonnegative")
        except (OSError, ValueError, KeyError, TypeError):
            errors.append(str(relative) + ": invalid or inaccessible run record")
    if run_paths and len(prompt_hashes) != 1:
        errors.append("Comparison runs must use the identical prompt")
    if run_paths and len(resolved_models) < 2:
        errors.append("Comparison requires different model/provider configurations")
    if stage == "final":
        if manifest.get("finalization_date") != str(today):
            errors.append("Finalization date must be today's actual local date")
        seconds = manifest.get("measured_runtime_seconds")
        if not isinstance(seconds, (int, float)) or seconds < 600:
            errors.append("Measured runtime is missing or below ten minutes")
        elif seconds > 900 and not manifest.get("extension_reason"):
            errors.append("Runtime over fifteen minutes needs a documented reason")
        required = ["mp4", "pptx", "docx", "script_txt", "srt", "vtt",
                    "narration_wav", "sfx_wav", "mixed_wav", "excerpt_mp4"]
        for kind in required:
            rel = manifest.get("deliverables", {}).get(kind)
            if not rel or not (base / rel).is_file():
                errors.append("Missing deliverable: " + kind)
        scenes = manifest.get("scenes", [])
        scene_ids = {scene.get("id") for scene in scenes}
        if not set(comparison.get("scene_ids", [])).issubset(scene_ids):
            errors.append("Combined comparison scene reference is invalid")
        for scene in scenes:
            for name in ("image", "narration_wav"):
                rel = scene.get(name)
                if not rel or not (base / rel).is_file():
                    errors.append(scene["id"] + ": missing " + name)
            if not set(scene.get("claim_ids", [])).issubset(set(claim_ids)):
                errors.append(scene["id"] + ": unknown factual claim IDs")
        for name in ("full_video_watch_and_listen", "readable_citations",
                     "pronunciation", "caption_sync", "media_permissions",
                     "graphics_fact_check", "combined_comparison_readable"):
            attestation = manifest.get("human_checks", {}).get(name, {})
            if not attestation.get("checked_at") or not attestation.get("reviewer"):
                errors.append("Unperformed review: " + name)
            else:
                try:
                    if timestamp(attestation["checked_at"]) > now:
                        raise ValueError("future attestation")
                except (ValueError, TypeError):
                    errors.append("Invalid review timestamp: " + name)
    return {"ready": not errors, "stage": stage, "errors": errors,
            "checked_at": now.isoformat(),
            "authenticity_review_required": True,
            "scope": "Readiness checks only. No claim of human playback or editorial review."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--stage", choices=["research", "final"], default="research")
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text())
    result = check(manifest, args.manifest.parent, args.stage)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["ready"] else 2)


if __name__ == "__main__":
    main()
