#!/usr/bin/env python3
"""Pre-register, run, and grade a small cloud-model comparison (stdlib only).

No calls are made by prepare or dry-run. Running requires an explicit spending
cap and --execute. Charges are never described as billed without billing evidence.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from zoneinfo import ZoneInfo


VERSION = "1.1.0"
EXAMPLE_ID = "fictional_invoice_csv_v1"
FIXTURE = '''invoice_id,customer,amount,currency,status
INV-1001,Acme Demo,125.50,USD,paid
INV-1002,Example Studio,240.00,USD,issued
INV-1003,Fictional Labs,75.00,USD,cancelled
INV-1004,Sample GmbH,90.25,EUR,paid
INV-1005,Demo Services,50.00,USD,pending?
INV-1006,"Example, Inc.",10.10,usd, PAID 
'''
INSTRUCTION = '''Extract this fictional invoice CSV into exactly one JSON object, with no prose or Markdown.
Use exactly these top-level keys: invoices, excluded_cancelled_invoice_ids, usd_total.
Keep invoices in CSV row order. Every included invoice must have exactly these keys:
invoice_id, customer, amount, currency, status, flags.
Preserve invoice_id and customer. Format amount as a string with two decimal places.
Trim status whitespace and convert status to lowercase. Trim currency and uppercase it.
Exclude rows with normalized status cancelled; list their IDs, in row order, in excluded_cancelled_invoice_ids.
For included rows, set flags to an array: add non_usd_currency first if currency is not USD;
add ambiguous_status second if status is neither paid nor issued.
usd_total is a two-decimal string: sum only included USD invoices whose status is paid or issued.
Do not infer a meaning for an ambiguous status. Do not convert currencies.
'''
POLICY = {
    "selection": "One fixed fictional CSV chosen before any model outputs; all six rows are evaluated.",
    "success": "All five deterministic checks must pass; no partial pass counts as success.",
    "checks": ["strict_json_object", "top_level_keys", "invoices_exact", "cancelled_ids_exact", "usd_total_exact"],
    "format": "JSON whitespace/key ordering do not affect scoring; array ordering and types do.",
    "retries": "Retry transport/API failures only, never failed grading or an inconvenient answer.",
    "scope": "This is a narrow extraction task; it cannot establish general model superiority.",
}
SECRET_FIELD = re.compile(r"(^|_)(authorization|password|secret|api_key|access_token|refresh_token)($|_)", re.I)
KEY_ENV = re.compile(r"^[A-Z][A-Z0-9_]{1,63}_API_KEY$")
MAX_RESPONSE_BYTES = 2_000_000


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def research_date():
    return datetime.now(ZoneInfo("America/New_York")).date().isoformat()


def decimal_value(value, label, positive=False):
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError(f"{label} must be a finite decimal") from None
    if not parsed.is_finite() or parsed < 0 or (positive and parsed == 0):
        raise ValueError(f"{label} must be {'positive' if positive else 'nonnegative'} and finite")
    return parsed


def assert_no_secrets(value):
    """Reject credential-bearing plan/export fields; credentials belong in env only."""
    if isinstance(value, dict):
        for key, item in value.items():
            if SECRET_FIELD.search(str(key)) and key != "api_key_env":
                raise ValueError("Credential-bearing fields are prohibited in plans and exports")
            if key == "api_key_env" and item is not None and (not isinstance(item, str) or not KEY_ENV.fullmatch(item)):
                raise ValueError("api_key_env must be a safe uppercase environment-variable name")
            assert_no_secrets(item)
    elif isinstance(value, list):
        for item in value:
            assert_no_secrets(item)
    elif isinstance(value, str) and re.search(r"\bBearer\s+\S+|\bsk-[A-Za-z0-9_-]{10,}", value):
        raise ValueError("A possible credential was found in a plan or export")


def scrub(value, secrets=()):
    """Preserve evidence with explicit redaction if a service echoes credentials."""
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            sensitive = SECRET_FIELD.search(str(key)) and key != "api_key_env"
            invalid_env = key == "api_key_env" and item is not None and (not isinstance(item, str) or not KEY_ENV.fullmatch(item))
            result[key] = "[REDACTED]" if sensitive or invalid_env else scrub(item, secrets)
        return result
    if isinstance(value, list):
        return [scrub(v, secrets) for v in value]
    if isinstance(value, str):
        for secret in secrets:
            if secret:
                value = value.replace(secret, "[REDACTED]")
        value = re.sub(r"\bBearer\s+\S+", "Bearer [REDACTED]", value)
        return re.sub(r"\bsk-[A-Za-z0-9_-]{10,}", "[REDACTED]", value)
    return value


def write_json(path, value, secrets=()):
    path = Path(path)
    data = json.dumps(scrub(value, secrets), indent=2, ensure_ascii=False) + "\n"
    # O_EXCL makes overwriting a previous run impossible, including through symlinks.
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(data)


def expected_output(csv_text):
    invoices, cancelled = [], []
    total = Decimal("0")
    for row in csv.DictReader(io.StringIO(csv_text)):
        status, currency = row["status"].strip().lower(), row["currency"].strip().upper()
        if status == "cancelled":
            cancelled.append(row["invoice_id"])
            continue
        amount = decimal_value(row["amount"], "invoice amount")
        if amount != amount.quantize(Decimal("0.01")):
            raise ValueError("Fixture amount has more than two decimal places")
        flags = []
        if currency != "USD":
            flags.append("non_usd_currency")
        if status not in ("paid", "issued"):
            flags.append("ambiguous_status")
        elif currency == "USD":
            total += amount
        invoices.append({"invoice_id": row["invoice_id"], "customer": row["customer"],
                         "amount": f"{amount:.2f}", "currency": currency, "status": status, "flags": flags})
    return {"invoices": invoices, "excluded_cancelled_invoice_ids": cancelled, "usd_total": f"{total:.2f}"}


def grade(output, expected):
    checks = {name: False for name in POLICY["checks"]}
    try:
        # No duplicate JSON keys, NaN, Infinity, or trailing prose are accepted.
        def unique_pairs(pairs):
            result = {}
            for k, v in pairs:
                if k in result:
                    raise ValueError("Duplicate JSON key")
                result[k] = v
            return result
        value = json.loads(output, object_pairs_hook=unique_pairs,
                           parse_constant=lambda value: (_ for _ in ()).throw(ValueError("Nonfinite JSON")))
        checks["strict_json_object"] = isinstance(value, dict)
        if isinstance(value, dict):
            checks["top_level_keys"] = set(value) == set(expected)
            checks["invoices_exact"] = value.get("invoices") == expected["invoices"]
            checks["cancelled_ids_exact"] = value.get("excluded_cancelled_invoice_ids") == expected["excluded_cancelled_invoice_ids"]
            checks["usd_total_exact"] = value.get("usd_total") == expected["usd_total"]
        return {"success": all(checks.values()), "checks": checks, "parse_error": None}
    except (json.JSONDecodeError, ValueError, TypeError) as error:
        return {"success": False, "checks": checks, "parse_error": str(error)}


def blank_model():
    return {"provider": None, "model": None, "endpoint": None, "api_key_env": None,
            "input_usd_per_million": None, "output_usd_per_million": None,
            "cached_input_usd_per_million": None, "cache_write_usd_per_million": None,
            "cache_counts_partition_input_verified": False,
            "cache_accounting_source_url": None, "expected_response_service_tier": None,
            "pricing_input_context_limit": None, "pricing_context": None,
            "rate_source_url": None, "rate_checked_date": None,
            "input_token_ceiling": 4096,
            "output_limit_field": "max_completion_tokens",
            "output_limit_includes_reasoning": False,
            "uniform_output_rate_includes_reasoning": False,
            "input_ceiling_verified_for_provider": False,
            "token_limit_source_url": None}


def prepare(directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    plan = {"schema_version": 1, "tool_version": VERSION, "preregistered_at_utc": utc_now(),
            "example_id": EXAMPLE_ID, "fixture_sha256": sha(FIXTURE.encode()),
            "instruction_sha256": sha(INSTRUCTION.encode()), "grading_policy": POLICY,
            "models": {"candidate": blank_model(), "comparator": blank_model()},
            "settings": {"temperature": None, "max_output_tokens": 2048, "seed": None,
                         "reasoning_effort": "medium", "service_tier": "default", "tools": [],
                         "timeout_seconds": 60, "retry_limit": 0},
            "max_spend_usd": None,
            "cap_basis": "Conservative token ceilings multiplied by published tariffs, including every authorized attempt; not a provider billing guarantee."}
    write_json(directory / "plan.json", plan)
    # Fixture and expected answer are public task material, never claimed to be model outputs.
    (directory / "task.csv").write_text(FIXTURE, encoding="utf-8")
    write_json(directory / "expected.json", expected_output(FIXTURE))
    (directory / "instruction.txt").write_text(INSTRUCTION, encoding="utf-8")
    return directory / "plan.json"


def load_plan(path):
    path = Path(path)
    raw = path.read_bytes()
    plan = json.loads(raw)
    assert_no_secrets(plan)
    fixture = (path.parent / "task.csv").read_text(encoding="utf-8")
    instruction = (path.parent / "instruction.txt").read_text(encoding="utf-8")
    if plan.get("schema_version") != 1 or plan.get("example_id") != EXAMPLE_ID:
        raise ValueError("Unsupported plan or example")
    if plan.get("fixture_sha256") != sha(fixture.encode()) or fixture != FIXTURE:
        raise ValueError("The preselected fixture changed; create a fresh plan instead")
    if plan.get("instruction_sha256") != sha(instruction.encode()) or instruction != INSTRUCTION:
        raise ValueError("The preselected instruction changed; create a fresh plan instead")
    if plan.get("grading_policy") != POLICY:
        raise ValueError("The preselected criteria changed; create a fresh plan instead")
    # Recompute the expected result; a modified expected.json cannot change scoring.
    return plan, fixture, instruction, sha(raw)


def request_payload(plan, side, fixture, instruction):
    model, settings = plan["models"][side], plan["settings"]
    result = {"model": model["model"],
              "messages": [{"role": "system", "content": instruction},
                           {"role": "user", "content": fixture}],
              model["output_limit_field"]: settings["max_output_tokens"]}
    if settings.get("temperature") is not None:
        result["temperature"] = settings["temperature"]
    if settings.get("reasoning_effort") is not None:
        result["reasoning_effort"] = settings["reasoning_effort"]
    if settings.get("service_tier") is not None:
        result["service_tier"] = settings["service_tier"]
    if settings.get("seed") is not None:
        result["seed"] = settings["seed"]
    return result


def validate(plan, fixture, instruction):
    problems, bounds = [], {}
    settings = plan.get("settings", {})
    if type(settings.get("max_output_tokens")) is not int or not 1 <= settings["max_output_tokens"] <= 100_000:
        problems.append("max_output_tokens must be an integer from 1 to 100000")
    if type(settings.get("retry_limit")) is not int or not 0 <= settings["retry_limit"] <= 2:
        problems.append("retry_limit must be an integer from 0 to 2")
    if type(settings.get("timeout_seconds")) not in (int, float) or not 1 <= settings["timeout_seconds"] <= 300:
        problems.append("timeout_seconds must be between 1 and 300")
    if settings.get("temperature") is not None and (type(settings["temperature"]) not in (int, float) or not 0 <= settings["temperature"] <= 2):
        problems.append("temperature must be between 0 and 2 or null/omitted")
    if settings.get("reasoning_effort") not in (None, "none", "low", "medium", "high", "xhigh", "max"):
        problems.append("reasoning_effort must be null or a supported explicit effort")
    if settings.get("tools") != []:
        problems.append("This minimal comparison must have no tools")
    if settings.get("service_tier") != "default":
        problems.append("This minimal tariff runner requires explicit default/standard service_tier")
    if settings.get("seed") is not None and type(settings["seed"]) is not int:
        problems.append("seed must be an integer or null")
    try:
        cap = decimal_value(plan.get("max_spend_usd"), "max_spend_usd", positive=True)
    except ValueError as error:
        cap = None
        problems.append(str(error))
    for side in ("candidate", "comparator"):
        model = plan.get("models", {}).get(side, {})
        for name in ("provider", "model", "endpoint", "api_key_env", "rate_source_url", "rate_checked_date", "token_limit_source_url", "cache_accounting_source_url", "expected_response_service_tier"):
            if not isinstance(model.get(name), str) or not model[name].strip():
                problems.append(f"{side}.{name} is required")
        endpoint = urllib.parse.urlsplit(model.get("endpoint") or "")
        if endpoint.scheme != "https" or not endpoint.hostname or endpoint.username or endpoint.password or endpoint.query or endpoint.fragment:
            problems.append(f"{side}.endpoint must be an HTTPS URL without credentials, query, or fragment")
        if not KEY_ENV.fullmatch(model.get("api_key_env") or ""):
            problems.append(f"{side}.api_key_env must be an uppercase name ending in _API_KEY")
        if model.get("output_limit_field") not in ("max_completion_tokens", "max_tokens"):
            problems.append(f"{side}.output_limit_field must be max_completion_tokens or max_tokens")
        if model.get("rate_checked_date") != research_date():
            problems.append(f"{side}.rate_checked_date must be today's America/New_York research date ({research_date()})")
        for name in ("output_limit_includes_reasoning", "uniform_output_rate_includes_reasoning", "input_ceiling_verified_for_provider", "cache_counts_partition_input_verified"):
            if model.get(name) is not True:
                problems.append(f"{side}.{name} must be verified true for this exact service/model")
        ceiling = model.get("input_token_ceiling")
        # This sanity check is not represented as an exact tokenizer measurement.
        if type(ceiling) is not int or ceiling < len((fixture + instruction).encode()) + 128:
            problems.append(f"{side}.input_token_ceiling is below the conservative UTF-8-byte sanity bound plus 128")
        pricing_limit = model.get("pricing_input_context_limit")
        if type(pricing_limit) is not int or pricing_limit <= 0 or (type(ceiling) is int and ceiling > pricing_limit):
            problems.append(f"{side}.pricing_input_context_limit must cover the verified input ceiling at these tariffs")
        try:
            in_rate = decimal_value(model.get("input_usd_per_million"), f"{side}.input rate")
            out_rate = decimal_value(model.get("output_usd_per_million"), f"{side}.output rate")
            cached_rate = decimal_value(model.get("cached_input_usd_per_million"), f"{side}.cached input rate")
            write_rate = decimal_value(model.get("cache_write_usd_per_million"), f"{side}.cache write rate")
            if type(ceiling) is int and type(settings.get("max_output_tokens")) is int:
                bounds[side] = (Decimal(ceiling) * max(in_rate, cached_rate, write_rate) + Decimal(settings["max_output_tokens"]) * out_rate) / Decimal(1_000_000)
        except ValueError as error:
            problems.append(str(error))
    attempts = 1 + settings.get("retry_limit", 0) if type(settings.get("retry_limit")) is int else 1
    total = sum(bounds.values(), Decimal(0)) * attempts
    if cap is not None and total > cap:
        problems.append(f"Preflight tariff bound {total} USD exceeds plan cap {cap} USD")
    if len(bounds) == 2 and bounds["candidate"] >= bounds["comparator"]:
        problems.append("Candidate must have a lower preflight task-cost bound than comparator")
    return {"ready": not problems, "problems": problems,
            "per_attempt_tariff_bound_usd": {k: str(v) for k, v in bounds.items()},
            "all_authorized_attempts_tariff_bound_usd": str(total),
            "token_ceilings_verified": all(plan.get("models", {}).get(side, {}).get("input_ceiling_verified_for_provider") is True for side in ("candidate", "comparator")),
            "bound_note": "Amounts are conditional on the registered token ceilings; unverified ceilings are illustrative assumptions and cannot authorize a run.",
            "cap_usd": str(cap) if cap is not None else None,
            "actual_billing_cap_guaranteed": False,
            "explanation": "Provider-verified input/output ceilings are required. Tariff arithmetic is a spending guard, not evidence of actual invoiced charges."}


def normalize_usage(response):
    usage = response.get("usage") if isinstance(response, dict) else None
    if not isinstance(usage, dict):
        return {"raw": usage, "input_tokens": None, "output_tokens": None, "reasoning_tokens": None,
                "cached_input_tokens": None, "cache_write_input_tokens": None}
    def count(primary, alternate):
        value = usage.get(primary, usage.get(alternate))
        return value if type(value) is int and value >= 0 else None
    details = usage.get("completion_tokens_details", usage.get("output_tokens_details", {}))
    reasoning = details.get("reasoning_tokens") if isinstance(details, dict) else None
    input_details = usage.get("prompt_tokens_details", usage.get("input_tokens_details", {}))
    cached = input_details.get("cached_tokens") if isinstance(input_details, dict) else None
    written = input_details.get("cache_write_tokens") if isinstance(input_details, dict) else None
    return {"raw": usage, "input_tokens": count("prompt_tokens", "input_tokens"),
            "output_tokens": count("completion_tokens", "output_tokens"),
            "reasoning_tokens": reasoning if type(reasoning) is int and reasoning >= 0 else None,
            "cached_input_tokens": cached if type(cached) is int and cached >= 0 else None,
            "cache_write_input_tokens": written if type(written) is int and written >= 0 else None}


def tariff_cost(usage, model):
    if any(usage.get(k) is None for k in ("input_tokens", "output_tokens", "cached_input_tokens", "cache_write_input_tokens")):
        return None
    if model.get("cache_counts_partition_input_verified") is not True:
        return None
    ordinary = usage["input_tokens"] - usage["cached_input_tokens"] - usage["cache_write_input_tokens"]
    if ordinary < 0:
        return None
    try:
        return str((Decimal(ordinary) * decimal_value(model.get("input_usd_per_million"), "input rate")
                    + Decimal(usage["cached_input_tokens"]) * decimal_value(model.get("cached_input_usd_per_million"), "cached input rate")
                    + Decimal(usage["cache_write_input_tokens"]) * decimal_value(model.get("cache_write_usd_per_million"), "cache write rate")
                    + Decimal(usage["output_tokens"]) * decimal_value(model.get("output_usd_per_million"), "output rate")) / Decimal(1_000_000))
    except ValueError:
        return None


def rate_record(model):
    return {k: model.get(k) for k in ("input_usd_per_million", "cached_input_usd_per_million",
            "cache_write_usd_per_million", "output_usd_per_million", "rate_source_url", "rate_checked_date",
            "cache_counts_partition_input_verified", "cache_accounting_source_url", "expected_response_service_tier",
            "pricing_input_context_limit", "pricing_context")}


def extract_output(response):
    try:
        content = response["choices"][0]["message"]["content"]
        return content if isinstance(content, str) else None
    except (KeyError, IndexError, TypeError):
        return None


class NoRedirect(urllib.request.HTTPRedirectHandler):
    # Never forward a bearer token to another host through an HTTP redirect.
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def send_request(endpoint, payload, key, timeout):
    request = urllib.request.Request(endpoint, data=canonical(payload),
                                     headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"}, method="POST")
    start = time.perf_counter()
    started_at = utc_now()
    try:
        with urllib.request.build_opener(NoRedirect).open(request, timeout=timeout) as response:
            body = response.read(MAX_RESPONSE_BYTES + 1)
            status = response.status
        if len(body) > MAX_RESPONSE_BYTES:
            return {"status": "response_too_large", "http_status": status, "body": body[:MAX_RESPONSE_BYTES],
                    "body_truncated": True, "elapsed_seconds": time.perf_counter() - start,
                    "started_at_utc": started_at, "observed_at_utc": utc_now(),
                    "error": "Response exceeded evidence storage limit"}
        return {"status": "http_success", "http_status": status, "body": body, "body_truncated": False,
                "started_at_utc": started_at, "observed_at_utc": utc_now(),
                "elapsed_seconds": time.perf_counter() - start, "error": None}
    except urllib.error.HTTPError as error:
        body = error.read(MAX_RESPONSE_BYTES + 1)
        return {"status": "http_error", "http_status": error.code, "body": body[:MAX_RESPONSE_BYTES],
                "started_at_utc": started_at, "observed_at_utc": utc_now(),
                "body_truncated": len(body) > MAX_RESPONSE_BYTES,
                "elapsed_seconds": time.perf_counter() - start, "error": str(error)}
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        return {"status": "transport_error", "http_status": None, "body": b"", "body_truncated": False,
                "started_at_utc": started_at, "observed_at_utc": utc_now(),
                "elapsed_seconds": time.perf_counter() - start, "error": str(error)}


def attempt_record(transport, payload, model, expected, secrets=(), origin="live_provider_requests", test_fixture=False):
    body = transport["body"]
    raw_text = body.decode("utf-8", errors="replace")
    try:
        response = json.loads(raw_text)
    except (json.JSONDecodeError, TypeError):
        response = None
    usage = normalize_usage(response)
    output = extract_output(response)
    success = transport["status"] == "http_success" and output is not None
    record = {k: v for k, v in transport.items() if k != "body"}
    record["transport_status"] = record["status"]
    record["status"] = "completed" if success else record["transport_status"]
    cost = tariff_cost(usage, model)
    observed_at = transport.get("observed_at_utc")
    reported_tier = response.get("service_tier") if isinstance(response, dict) else None
    reported_model = response.get("model") if isinstance(response, dict) else None
    # A different/unknown tariff tier or model cannot be priced from the registered rates.
    if reported_tier != model.get("expected_response_service_tier") or reported_model != model.get("model"):
        cost = None
    if not observed_at or datetime.fromisoformat(observed_at.replace("Z", "+00:00")).astimezone(ZoneInfo("America/New_York")).date().isoformat() != model.get("rate_checked_date"):
        cost = None
    record.update({"request_payload": payload, "request_sha256": sha(canonical(payload)),
                   "origin": origin, "test_fixture": test_fixture,
                   "observed_at_utc": observed_at, "run_at": transport.get("started_at_utc"),
                   "provenance": {"endpoint": model["endpoint"], "provider": model["provider"],
                                  "captured_by": "AI Update comparison runner", "authentication": "Bearer credential from named environment variable; key omitted"},
                   "rate_record": rate_record(model),
                   "prompt_sha256": sha(canonical(payload["messages"])), "provider": model["provider"],
                   "raw_response_text": raw_text, "raw_response_sha256": sha(body),
                   "raw_response": raw_text,
                   "response_json": response, "output_text": output,
                   "output_sha256": sha(output.encode()) if output is not None else None,
                   "usage": usage, "calculated_tariff_usd": cost,
                   "cost": {"total_usd": cost, "basis": "published_tariff_calculation_only" if cost is not None else "unknown", "actual_billed_usd": None,
                            "rate_record": rate_record(model), "usage_basis": "Reported input partitions and total completion tokens; reasoning not added twice"},
                   "actual_billed_usd": None, "cost_basis": "published_tariff_calculation_only" if cost is not None else "unknown",
                   "requested_model": model["model"],
                   "reported_model": reported_model, "reported_service_tier": reported_tier,
                   "settings_verified": True,
                   "grading": grade(output, expected) if success else None,
                   "usable_output": success,
                   "raw_response_redacted": scrub(raw_text, secrets) != raw_text})
    return scrub(record, secrets)


def execute(plan_path, output_dir, execute_flag, max_spend_usd, sender=send_request):
    # Authorize and validate completely before touching output directories or the network.
    if not execute_flag or max_spend_usd is None:
        raise ValueError("No execution: supply both --execute and --max-spend-usd")
    user_cap = decimal_value(max_spend_usd, "explicit spending cap", positive=True)
    plan, fixture, instruction, plan_hash = load_plan(plan_path)
    feasibility = validate(plan, fixture, instruction)
    if not feasibility["ready"]:
        raise ValueError("No execution: " + "; ".join(feasibility["problems"]))
    if user_cap > decimal_value(plan["max_spend_usd"], "plan cap", positive=True):
        raise ValueError("Explicit run cap cannot exceed the preregistered plan cap")
    total_bound = decimal_value(feasibility["all_authorized_attempts_tariff_bound_usd"], "preflight bound")
    if total_bound > user_cap:
        raise ValueError("No execution: all authorized attempts exceed the explicit run cap")
    keys = {}
    for side in ("candidate", "comparator"):
        env_name = plan["models"][side]["api_key_env"]
        key = os.environ.get(env_name)
        if not key or any(character in key for character in "\r\n"):
            raise ValueError(f"Missing or invalid environment credential: {env_name}")
        keys[side] = key
    secrets = tuple(keys.values())
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=False)
    write_json(output_dir / "locked-plan.json", plan, secrets)
    is_test = sender is not send_request
    origin = "unit_test_fixture" if is_test else "live_provider_requests"
    metadata = {"tool_version": VERSION, "started_at_utc": utc_now(), "plan_file_sha256": plan_hash,
                "origin": origin, "test_fixture": is_test, "fixture_sha256": sha(fixture.encode()),
                "instruction_sha256": sha(instruction.encode()), "explicit_run_cap_usd": str(user_cap),
                "feasibility": feasibility, "records": []}
    write_json(output_dir / "started.json", metadata, secrets)
    reserved = Decimal(0)
    expected = expected_output(fixture)
    for side in ("candidate", "comparator"):
        model = plan["models"][side]
        payload = request_payload(plan, side, fixture, instruction)
        record = {"side": side, "example_id": plan["example_id"], "attempts": []}
        per_attempt = decimal_value(feasibility["per_attempt_tariff_bound_usd"][side], "attempt bound")
        for index in range(1 + plan["settings"]["retry_limit"]):
            if reserved + per_attempt > user_cap:
                raise ValueError("Spending guard stopped execution before a request")
            # A failed or interrupted attempt can still be billed: always reserve its full bound.
            reserved += per_attempt
            write_json(output_dir / f"{side}-request-{index + 1}.json",
                       {"status": "reserved_before_request", "side": side, "provider": model["provider"],
                        "attempt_number": index + 1, "requested_model": model["model"],
                        "request_payload": payload, "request_sha256": sha(canonical(payload)),
                        "prompt_sha256": sha(canonical(payload["messages"])),
                        "reserved_tariff_bound_usd": str(per_attempt), "recorded_at_utc": utc_now()}, secrets)
            transport = sender(model["endpoint"], payload, keys[side], plan["settings"]["timeout_seconds"])
            attempt = attempt_record(transport, payload, model, expected, secrets, origin, is_test)
            attempt["attempt_number"] = index + 1
            attempt["reserved_tariff_bound_usd"] = str(per_attempt)
            attempt["recorded_at_utc"] = utc_now()
            usage = attempt["usage"]
            attempt["token_ceiling_exceeded"] = bool(
                (usage["input_tokens"] is not None and usage["input_tokens"] > model["input_token_ceiling"])
                or (usage["output_tokens"] is not None and usage["output_tokens"] > plan["settings"]["max_output_tokens"]))
            write_json(output_dir / f"{side}-attempt-{index + 1}.json", attempt, secrets)
            record["attempts"].append(attempt)
            if attempt["token_ceiling_exceeded"]:
                metadata["records"].append(record)
                metadata.update({"finished_at_utc": utc_now(), "reserved_tariff_bound_usd": str(reserved),
                                 "stopped_reason": "Provider reported usage above a verified token ceiling; all further calls stopped."})
                metadata["summary"] = summarize(metadata["records"])
                write_json(output_dir / "result.json", metadata, secrets)
                return metadata
            # Missing/invalid output is preserved, never automatically retried.
            # Only API/transport errors get the explicitly preregistered retry allowance.
            if transport["status"] not in ("transport_error", "http_error"):
                break
            if transport.get("http_status") is not None and transport["http_status"] not in (408, 429, 500, 502, 503, 504):
                break
        metadata["records"].append(record)
    metadata.update({"finished_at_utc": utc_now(), "reserved_tariff_bound_usd": str(reserved)})
    metadata["summary"] = summarize(metadata["records"])
    write_json(output_dir / "result.json", metadata, secrets)
    return metadata


def summarize(records):
    summary = {}
    for record in records:
        attempts = record["attempts"]
        selected = next((a for a in attempts if a.get("usable_output")), None)
        known = [a.get("calculated_tariff_usd") for a in attempts]
        summary[record["side"]] = {"attempt_count": len(attempts),
                                   "task_success": selected["grading"]["success"] if selected else False,
                                   "settings_verified": bool(selected and selected.get("settings_verified")),
                                   "selected_attempt_number": selected.get("attempt_number") if selected else None,
                                   "calculated_total_tariff_usd": str(sum((Decimal(x) for x in known), Decimal(0))) if known and all(x is not None for x in known) else None,
                                   "actual_billed_usd": None,
                                   "elapsed_seconds_all_attempts": sum(a["elapsed_seconds"] for a in attempts) if all(a.get("elapsed_seconds") is not None for a in attempts) else None}
    comparable = all(side in summary and summary[side]["task_success"] and summary[side]["settings_verified"] for side in ("candidate", "comparator"))
    costs = [summary.get(side, {}).get("calculated_total_tariff_usd") for side in ("candidate", "comparator")]
    summary["comparison"] = {"both_passed_with_verified_settings": comparable,
                              "calculated_tariff_saving_usd": str(Decimal(costs[1]) - Decimal(costs[0])) if comparable and all(c is not None for c in costs) else None,
                              "actual_billed_saving_usd": None,
                              "interpretation": "A narrow task result only. Missing usage, failed attempts, or unverified export settings prevent a complete cost comparison."}
    return summary


def import_export(plan_path, export_path, output_dir):
    """Import a user-supplied, sanitized export; no inference fills missing fields."""
    plan, fixture, instruction, plan_hash = load_plan(plan_path)
    export_raw = Path(export_path).read_bytes()
    export = json.loads(export_raw)
    assert_no_secrets(export)
    if not isinstance(export.get("source_label"), str) or not export["source_label"].strip():
        raise ValueError("Export requires a source_label identifying its provenance")
    if export.get("plan_file_sha256") != plan_hash:
        raise ValueError("Export must identify this exact pre-registered plan_file_sha256")
    records = []
    seen = set()
    for item in export.get("records", []):
        side = item.get("side")
        if side not in ("candidate", "comparator") or side in seen or item.get("example_id") != plan["example_id"]:
            raise ValueError("Export must have unique recognized sides and the registered example ID")
        seen.add(side)
        expected_payload = request_payload(plan, side, fixture, instruction)
        attempts = []
        for index, source in enumerate(item.get("attempts", []), 1):
            if not isinstance(source.get("response"), dict):
                raise ValueError("Each export attempt requires the actual provider response object")
            response = source["response"]
            output = extract_output(response)
            usage = normalize_usage(response)
            elapsed = source.get("elapsed_seconds")
            if elapsed is not None and (type(elapsed) not in (int, float) or elapsed < 0):
                raise ValueError("elapsed_seconds must be nonnegative or null")
            actual_payload = source.get("request_payload")
            verified = actual_payload == expected_payload
            model = plan["models"][side]
            cost = None
            observed_at = source.get("observed_at_utc")
            if observed_at is not None:
                try:
                    observed_dt = datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
                    if observed_dt.utcoffset() is None:
                        raise ValueError("Missing timezone")
                except (AttributeError, ValueError):
                    raise ValueError("Export observation timestamp must include its actual timezone, or remain null") from None
            else:
                observed_dt = None
            rate_date_matches = bool(observed_dt and observed_dt.astimezone(ZoneInfo("America/New_York")).date().isoformat() == model.get("rate_checked_date"))
            if (verified and rate_date_matches and model.get("uniform_output_rate_includes_reasoning") is True
                and response.get("service_tier") == model.get("expected_response_service_tier")
                and response.get("model") == model.get("model")):
                cost = tariff_cost(usage, model)
            observed_status = source.get("status")
            completed = output is not None and observed_status in ("completed", "http_success")
            attempts.append({"attempt_number": index, "origin": "user_supplied_provider_export",
                             "test_fixture": export.get("test_fixture") is not False,
                             "observed_at_utc": observed_at, "run_at": source.get("run_at"),
                             "provenance": {"source_label": export["source_label"], "authentication_verified": False,
                                            "note": "User-supplied export; provider authenticity is not independently certified"},
                             "rate_record": rate_record(model),
                             "status": "completed" if completed else observed_status, "http_status": source.get("http_status"),
                             "provider": model.get("provider"),
                             "prompt_sha256": sha(canonical(actual_payload["messages"])) if verified else None,
                             "elapsed_seconds": elapsed, "request_payload": actual_payload,
                             "expected_request_sha256": sha(canonical(expected_payload)),
                             "request_sha256": sha(canonical(actual_payload)) if actual_payload is not None else None,
                             "settings_verified": verified, "response_json": response,
                             "raw_response": response,
                             "raw_response_text": None, "raw_response_sha256": None,
                             "raw_response_note": "Raw HTTP bytes are unknown; export contains a parsed provider response.",
                             "output_text": output, "output_sha256": sha(output.encode()) if output is not None else None,
                             "requested_model": model.get("model"), "reported_model": response.get("model"),
                             "usage": usage, "calculated_tariff_usd": cost, "actual_billed_usd": None,
                             "cost": {"total_usd": cost, "basis": "published_tariff_calculation_only" if cost is not None else "unknown", "actual_billed_usd": None,
                                      "rate_record": rate_record(model)},
                             "cost_basis": "published_tariff_calculation_only" if cost is not None else "unknown",
                             "usable_output": completed,
                             "grading": grade(output, expected_output(fixture)) if completed else None})
        if not attempts:
            raise ValueError("Each exported side must contain at least one actual attempt")
        records.append({"side": side, "example_id": plan["example_id"], "attempts": attempts})
    if not records:
        raise ValueError("Export contains no actual records")
    result = {"tool_version": VERSION, "origin": "user_supplied_provider_export",
              "imported_at_utc": utc_now(), "source_label": export["source_label"],
              "export_file_sha256": sha(export_raw), "plan_file_sha256": plan_hash,
              "records": records, "summary": summarize(records)}
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=False)
    write_json(output_dir / "locked-plan.json", plan)
    for record in records:
        for attempt in record["attempts"]:
            write_json(output_dir / f"{record['side']}-attempt-{attempt['attempt_number']}.json", attempt)
    write_json(output_dir / "result.json", result)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    prep = sub.add_parser("prepare", help="Create a new task and unconfigured pre-registration")
    prep.add_argument("--directory", required=True)
    dry = sub.add_parser("dry-run", help="Validate configuration without provider calls")
    dry.add_argument("--plan", required=True)
    run = sub.add_parser("run", help="Explicitly authorize bounded provider calls")
    run.add_argument("--plan", required=True)
    run.add_argument("--out", required=True)
    run.add_argument("--execute", action="store_true")
    run.add_argument("--max-spend-usd")
    imp = sub.add_parser("import", help="Grade a sanitized actual provider export, without calls")
    imp.add_argument("--plan", required=True)
    imp.add_argument("--export", required=True)
    imp.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "prepare":
            result = {"plan": str(prepare(args.directory)), "provider_calls": 0,
                      "next": "Configure exact providers, models, tariffs, verified token ceilings, and a cap; then dry-run."}
        elif args.command == "dry-run":
            plan, fixture, instruction, plan_hash = load_plan(args.plan)
            result = {"plan_file_sha256": plan_hash, "provider_calls": 0, **validate(plan, fixture, instruction)}
        elif args.command == "run":
            result = execute(args.plan, args.out, args.execute, args.max_spend_usd)["summary"]
        else:
            result = import_export(args.plan, args.export, args.out)["summary"]
        print(json.dumps(result, indent=2))
        return 0
    except (ValueError, KeyError, FileExistsError, FileNotFoundError, json.JSONDecodeError) as error:
        print(json.dumps({"error": scrub(str(error)), "inspect_partial_records_if_run_started": args.command == "run"}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
