# AI Update cloud comparison

This small Python 3 program pre-registers one identical fictional invoice-extraction task for a lower-cost candidate and a comparator. It uses only the standard library. It does not select models, invent provider results, measure general model ability, or treat a published-price calculation as an actual billed charge.

The original `preregistered/` directory is preserved as **unconfigured**. The new `preregistered-v2/` proposal registers the exact OpenAI model IDs `gpt-6-luna` and `gpt-6.1-sol`, their standard short-context input/cached-input/cache-write/output rates checked on October 13, 2026, medium reasoning, 2,048 total output tokens, no tools, standard service tier, and zero retries. Temperature is omitted for compatibility with medium reasoning. Its cap is still `null`, and input ceilings remain explicitly **unverified**. Its real dry run is therefore blocked, with zero provider calls. Conditional arithmetic in that dry run is illustrative until ceilings are verified. Neither registration contains model outputs. `expected.json` is a deterministic grading key, **not a model answer**. Unit tests use explicitly marked fabricated responses in temporary directories.

## What is preselected

The fixed CSV has six fictional invoices, including a cancelled invoice, a non-USD invoice, an ambiguous status, case/whitespace normalization, and a quoted customer name containing a comma. Both models receive exactly the same system instruction and CSV. Both use the same temperature, seed setting, and maximum output-token budget.

Success requires all five checks: a strict JSON object, exact top-level keys, exact invoice records/flags, exact cancelled IDs, and the exact USD total. Ambiguous-status amounts and non-USD amounts do not contribute to that total. JSON key order and whitespace do not affect grading. Duplicate keys, code fences, or extra prose fail. The correct USD total is `375.60`; this is the grading key, not a provider observation.

The selected example cannot be changed in an existing registration. To change the task or its criteria, create a new version of the tool and a fresh registration before obtaining any responses.

## Configure securely

1. Create a new registration, or copy the included unconfigured one to a new directory before editing:

   ```bash
   python3 compare.py prepare --directory my-comparison-registration
   ```

2. Edit its `plan.json`. Configure **exact** candidate/comparator model IDs, provider names, and full HTTPS chat-completions endpoints. Supply their published input/output USD rates per million tokens, the primary source URL, and the date you actually checked those rates. Do not put API keys in the plan. `api_key_env` is an environment-variable name such as `CANDIDATE_API_KEY`; its value is never recorded.

3. Verify the exact service/model's input-token ceiling and output-limit semantics. Set the three verification booleans to `true` only after real verification: the input-token ceiling covers the entire request; the chosen `max_tokens` or `max_completion_tokens` field limits **all billed output, including reasoning**; and that output uses the configured uniform tariff. Record the relevant provider documentation in `token_limit_source_url`. Services with a separate reasoning tariff, unbounded reasoning, or unverifiable input ceilings are blocked by this minimal runner. The byte sanity bound is a conservative check, not an exact tokenizer count.

4. Set `max_spend_usd` explicitly. The dry run reserves each model's full configured token ceiling for every permitted attempt. Retries default to zero, are limited to two, and must be registered before running. They apply only to listed transient API/transport errors. Failed grading never triggers a retry.

5. Run the feasibility check; this makes no provider calls:

   ```bash
   python3 compare.py dry-run --plan my-comparison-registration/plan.json
   ```

6. Put the keys into the configured environment-variable names using your provider's secret manager or a silent terminal prompt. For example:

   ```bash
   read -rsp 'Candidate API key: ' CANDIDATE_API_KEY
   export CANDIDATE_API_KEY
   read -rsp 'Comparator API key: ' COMPARATOR_API_KEY
   export COMPARATOR_API_KEY
   ```

   Keep the key values out of command arguments, chat, screenshots, source control, and exports. Clear them with `unset CANDIDATE_API_KEY COMPARATOR_API_KEY` after the run. When using the v2 proposal, use its actual environment-variable names: `OPENAI_CANDIDATE_API_KEY` and `OPENAI_COMPARATOR_API_KEY`.

7. Only after choosing and authorizing a budget, execute explicitly. This example uses a **user-chosen** ten-cent maximum; it is not a recommendation or an authorization to purchase anything:

   ```bash
   python3 compare.py run --plan my-comparison-registration/plan.json \
     --out actual-run-001 --execute --max-spend-usd 0.10
   ```

   The run cap cannot exceed the registered cap, and all authorized attempts must fit it before the first request. Provider-verified ceilings make tariff guarding possible; this program cannot enforce a provider's actual invoice or rule out pricing mistakes, taxes, account fees, or unreported usage. It never claims that the cap is a provider billing guarantee. If observed usage exceeds a verified ceiling, it records the breach and stops further calls.

For OpenAI, use [API keys](https://platform.openai.com/api-keys), [API pricing](https://developers.openai.com/api/docs/pricing), [chat-completions documentation](https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create), [Luna documentation](https://developers.openai.com/api/docs/models/gpt-6-luna), [Sol documentation](https://developers.openai.com/api/docs/models/gpt-6.1-sol), and [cache accounting](https://developers.openai.com/api/docs/guides/prompt-caching). The [GPT-6 compatibility guide](https://developers.openai.com/api/docs/guides/latest-model) documents why temperature must be omitted with medium reasoning. Check rates on the actual America/New_York execution date; stale registration dates block execution. Other OpenAI-compatible services require their own primary documentation.

## Records and interpretation

The run directory is created exclusively and cannot overwrite an existing directory. A locked plan and `started.json` are written before any request. Each request has a reservation record written before it is sent, and every completed/error attempt has a separate JSON evidence file. If interrupted, inspect those files: a reserved request can still have been charged even if no response was captured.

Evidence includes the shared prompt hash, the complete request payload and its hash, exact requested/reported models, observed elapsed wall time, HTTP/error status, full stored response text, response-byte/output hashes, usage/reasoning fields as reported, grading, and cost basis. Credential echoes are redacted; the record states when this changes stored response text, while the original response-byte hash remains. HTTP redirects are refused to avoid forwarding bearer tokens. A response storage limit of two million bytes is recorded explicitly if exceeded.

`calculated_tariff_usd` and `cost.total_usd` use actual reported tokens and the registered tariffs. Ordinary input is `input − cached − cache_write`; each disjoint partition uses its own rate. Missing cache counts, inconsistent partitions, unknown/different response service tiers or model IDs, and incomplete usage yield unknown cost. The cap bound uses the maximum registered input/cache rate, so writes are included. The registered short-context tariff ceiling must cover the verified input ceiling. Reasoning tokens are preserved separately but are **not added twice** to completion tokens. Failed attempts stay in total-cost accounting; if their cost is unknown, the complete cost comparison is unknown. `actual_billed_usd` and actual billed savings always remain `null`, because this runner has no provider invoice evidence. Timing includes transport and generation, rather than claiming isolated model inference time.

The common gate fields on individual attempt files are `status`, `raw_response`, `prompt_sha256`, `provider`, `requested_model`, and `cost`. `status: completed` means an actual captured output was available; success still requires the deterministic grading checks. A cost-saving claim requires both models to pass with verified settings and all attempt costs known. One task establishes only that task's result.

## Import actual provider exports without making calls

If you prefer to supply outputs, run both models on the registered messages/settings and export the real provider responses. Sanitize the export first. Include the hash printed by `dry-run`, provenance, and each actually observed request/response. Do not replace missing settings, timing, or usage with guesses. Omitted fields remain `null`, and unverified request settings block a complete comparison.

The JSON envelope has these keys:

```json
{
  "source_label": "Actual provider export provenance and collection date",
  "test_fixture": false,
  "plan_file_sha256": "THE HASH PRINTED BY DRY-RUN",
  "records": [
    {
      "side": "candidate",
      "example_id": "fictional_invoice_csv_v1",
      "attempts": []
    },
    {
      "side": "comparator",
      "example_id": "fictional_invoice_csv_v1",
      "attempts": []
    }
  ]
}
```

Replace each empty `attempts` array with every real attempt. Each attempt requires an actual provider `response` object. Add `status: "completed"` only for a completed provider response; include `http_status`, `elapsed_seconds`, and the exact `request_payload` only when observed. Add `observed_at_utc` and `run_at` only for known original provider observation/start timestamps with explicit timezones; import time is not observation time. Unknown original dates remain `null` and prevent date-matched pricing. Missing request payload means settings cannot be verified. Set `test_fixture: false` only for actual evidence. The envelope above is deliberately incomplete and cannot pass as evidence.

```bash
python3 compare.py import --plan my-comparison-registration/plan.json \
  --export actual-sanitized-export.json --out actual-import-001
```

The importer emits the same portable per-attempt JSON files as a live run, preserves parsed provider responses, separately hashes the supplied export, and reports raw HTTP bytes as unknown. User-supplied provenance is recorded; authenticity is not independently certified by this program. It cannot turn a copied answer, invented response, or deterministic grading key into an authentic provider run. Portable records include `origin`, `test_fixture`, `observed_at_utc`, exact `request_payload`, raw usage, and `rate_record` for replay. A chart or final comparison must use summary costs across **every attempt**, including failures, rather than just the selected successful answer.

## Verify the program

```bash
python3 -m unittest -v test_compare.py
```

The tests cover decimal arithmetic, grading, reasoning-cost accounting, unknown usage/billing, preserved retry failures, no grading retries, spending/verification gates, credential redaction, immutable paths, fixture integrity, exceeded token ceilings, import unknowns, and matching prompt hashes. None of these unit tests establishes that a real cloud comparison was completed.
