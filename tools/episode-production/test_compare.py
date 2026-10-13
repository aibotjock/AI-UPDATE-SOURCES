"""Unit tests use fabricated responses only, never cloud-provider calls."""
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import compare


class ComparisonTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.plan_path = compare.prepare(self.root / "preregistered")
        self.plan = json.loads(self.plan_path.read_text())
        self.plan["max_spend_usd"] = "0.2"
        for side, rate in (("candidate", "1"), ("comparator", "4")):
            model = self.plan["models"][side]
            model.update({"provider": "UNIT_TEST_FAKE_PROVIDER", "model": f"unit-test-{side}-exact-id",
                          "endpoint": "https://example.invalid/v1/chat/completions",
                          "api_key_env": f"TEST_{side.upper()}_API_KEY", "input_usd_per_million": rate,
                          "output_usd_per_million": rate, "rate_source_url": "https://example.invalid/pricing",
                          "rate_checked_date": compare.research_date(), "token_limit_source_url": "https://example.invalid/limits",
                          "cached_input_usd_per_million": "0.1", "cache_write_usd_per_million": str(float(rate) * 1.25),
                          "cache_counts_partition_input_verified": True,
                          "cache_accounting_source_url": "https://example.invalid/cache-accounting",
                          "expected_response_service_tier": "default",
                          "pricing_input_context_limit": 272000, "pricing_context": "unit_test_short",
                          "output_limit_includes_reasoning": True, "uniform_output_rate_includes_reasoning": True,
                          "input_ceiling_verified_for_provider": True})
        self.save_plan()
        self.env = {"TEST_CANDIDATE_API_KEY": "UNIT_TEST_KEY_CANDIDATE_DO_NOT_EXPORT",
                    "TEST_COMPARATOR_API_KEY": "UNIT_TEST_KEY_COMPARATOR_DO_NOT_EXPORT"}

    def tearDown(self):
        self.tmp.cleanup()

    def save_plan(self):
        self.plan_path.write_text(json.dumps(self.plan, indent=2) + "\n")

    def transport(self, output=None, usage=True):
        if output is None:
            output = json.dumps(compare.expected_output(compare.FIXTURE))
        response = {"model": "reported-unit-test-id", "service_tier": "default", "choices": [{"message": {"content": output}}]}
        if usage:
            response["usage"] = {"prompt_tokens": 1500, "completion_tokens": 400,
                                 "prompt_tokens_details": {"cached_tokens": 0, "cache_write_tokens": 0},
                                 "completion_tokens_details": {"reasoning_tokens": 50}}
        return {"status": "http_success", "http_status": 200, "body": compare.canonical(response),
                "body_truncated": False, "elapsed_seconds": 0.25, "error": None}

    def run_fake(self, sender, name="run"):
        def explicitly_fabricated_sender(*args):
            value = sender(*args)
            value["started_at_utc"] = compare.utc_now()
            value["observed_at_utc"] = compare.utc_now()
            if value["status"] == "http_success":
                response = json.loads(value["body"])
                response["model"] = args[1]["model"]
                value["body"] = compare.canonical(response)
            return value
        with patch.dict(os.environ, self.env):
            return compare.execute(self.plan_path, self.root / name, True, "0.2", explicitly_fabricated_sender)

    def test_expected_decimal_total_and_flags(self):
        expected = compare.expected_output(compare.FIXTURE)
        self.assertEqual(expected["usd_total"], "375.60")
        self.assertEqual(expected["excluded_cancelled_invoice_ids"], ["INV-1003"])
        self.assertEqual(expected["invoices"][2]["flags"], ["non_usd_currency"])
        self.assertEqual(expected["invoices"][3]["flags"], ["ambiguous_status"])
        self.assertEqual(expected["invoices"][4]["customer"], "Example, Inc.")

    def test_strict_grading_rejects_duplicate_keys_extra_prose_and_wrong_totals(self):
        expected = compare.expected_output(compare.FIXTURE)
        valid = json.dumps(expected)
        self.assertTrue(compare.grade(valid, expected)["success"])
        self.assertFalse(compare.grade(valid + " commentary", expected)["success"])
        self.assertFalse(compare.grade('{"invoices":[],"invoices":[]}', expected)["success"])
        expected["usd_total"] = "425.60"
        self.assertFalse(compare.grade(json.dumps(expected), compare.expected_output(compare.FIXTURE))["success"])

    def test_cost_includes_reasoning_once_and_is_not_a_billed_charge(self):
        usage = compare.normalize_usage(json.loads(self.transport()["body"]))
        self.assertEqual(usage["reasoning_tokens"], 50)
        self.assertEqual(compare.tariff_cost(usage, self.plan["models"]["candidate"]), "0.0019")
        result = self.run_fake(lambda *args: self.transport())
        self.assertIsNone(result["summary"]["candidate"]["actual_billed_usd"])
        self.assertEqual(result["summary"]["comparison"]["calculated_tariff_saving_usd"], "0.0057")
        self.assertIsNone(result["summary"]["comparison"]["actual_billed_saving_usd"])

    def test_unknown_usage_produces_unknown_cost(self):
        result = self.run_fake(lambda *args: self.transport(usage=False))
        self.assertIsNone(result["summary"]["candidate"]["calculated_total_tariff_usd"])
        self.assertIsNone(result["summary"]["comparison"]["calculated_tariff_saving_usd"])

    def test_cached_read_write_partitions_are_priced_without_double_count(self):
        usage = {"input_tokens": 1500, "output_tokens": 400, "cached_input_tokens": 600,
                 "cache_write_input_tokens": 500, "reasoning_tokens": 50}
        # 400 ordinary at $1 + 600 cached at $.1 + 500 written at $1.25 + 400 output at $1.
        self.assertEqual(compare.tariff_cost(usage, self.plan["models"]["candidate"]), "0.001485")
        usage["cache_write_input_tokens"] = 1000
        self.assertIsNone(compare.tariff_cost(usage, self.plan["models"]["candidate"]))

    def test_missing_cache_counts_are_unknown_cost(self):
        response = json.loads(self.transport()["body"])
        del response["usage"]["prompt_tokens_details"]["cache_write_tokens"]
        usage = compare.normalize_usage(response)
        self.assertIsNone(compare.tariff_cost(usage, self.plan["models"]["candidate"]))

    def test_rate_freshness_and_safe_environment_names(self):
        self.plan["models"]["candidate"]["rate_checked_date"] = "2000-01-01"
        result = compare.validate(self.plan, compare.FIXTURE, compare.INSTRUCTION)
        self.assertFalse(result["ready"])
        self.assertTrue(any("America/New_York" in error for error in result["problems"]))
        self.assertEqual(compare.scrub({"api_key_env": "EXAMPLE_API_KEY"})["api_key_env"], "EXAMPLE_API_KEY")
        with self.assertRaises(ValueError):
            compare.assert_no_secrets({"api_key_env": "actual-secret-not-an-env-name"})
        self.assertEqual(compare.scrub({"api_key_env": "actual-secret-not-an-env-name"})["api_key_env"], "[REDACTED]")

    def test_mocked_runs_explicitly_mark_test_fixtures(self):
        result = self.run_fake(lambda *args: self.transport())
        self.assertTrue(result["test_fixture"])
        self.assertEqual(result["origin"], "unit_test_fixture")
        self.assertTrue(result["records"][0]["attempts"][0]["test_fixture"])

    def test_retry_error_and_success_are_both_preserved_without_hidden_retry(self):
        self.plan["settings"]["retry_limit"] = 1
        self.save_plan()
        calls = []
        def sender(*args):
            calls.append(args)
            if len(calls) == 1:
                return {"status": "http_error", "http_status": 429, "body": b'{"error":"rate limit"}',
                        "body_truncated": False, "elapsed_seconds": 0.1, "error": "HTTP 429"}
            return self.transport()
        result = self.run_fake(sender)
        self.assertEqual(len(calls), 3)
        self.assertEqual(result["records"][0]["attempts"][0]["status"], "http_error")
        self.assertEqual(result["records"][0]["attempts"][1]["status"], "completed")
        self.assertIsNone(result["summary"]["candidate"]["calculated_total_tariff_usd"])
        self.assertTrue((self.root / "run" / "candidate-attempt-1.json").exists())
        self.assertTrue((self.root / "run" / "candidate-request-1.json").exists())

    def test_failed_grading_is_not_retried(self):
        self.plan["settings"]["retry_limit"] = 2
        self.save_plan()
        calls = []
        def sender(*args):
            calls.append(args)
            return self.transport("{}")
        result = self.run_fake(sender)
        self.assertEqual(len(calls), 2)
        self.assertFalse(result["summary"]["candidate"]["task_success"])

    def test_no_execution_without_explicit_flag_and_cap(self):
        for flag, cap in ((False, "0.1"), (True, None)):
            with self.assertRaises(ValueError):
                compare.execute(self.plan_path, self.root / "blocked", flag, cap,
                                lambda *args: self.fail("Network called"))
        self.assertFalse((self.root / "blocked").exists())

    def test_insufficient_cap_blocks_calls(self):
        with self.assertRaises(ValueError):
            compare.execute(self.plan_path, self.root / "blocked", True, "0.0001",
                            lambda *args: self.fail("Network called"))
        self.assertFalse((self.root / "blocked").exists())

    def test_missing_provider_verification_blocks_calls(self):
        self.plan["models"]["candidate"]["output_limit_includes_reasoning"] = False
        self.save_plan()
        with self.assertRaises(ValueError):
            self.run_fake(lambda *args: self.fail("Network called"))

    def test_credentials_redacted_from_response_error_and_written_files(self):
        secret = self.env["TEST_CANDIDATE_API_KEY"]
        calls = []
        def sender(*args):
            calls.append(args)
            if len(calls) == 1:
                return {"status": "http_error", "http_status": 401, "body": ("key=" + secret).encode(),
                        "body_truncated": False, "elapsed_seconds": 0.1, "error": "Bearer " + secret}
            return self.transport()
        self.run_fake(sender)
        for path in (self.root / "run").glob("*.json"):
            self.assertNotIn(secret, path.read_text())
            self.assertNotIn(self.env["TEST_COMPARATOR_API_KEY"], path.read_text())
        self.assertIn("[REDACTED]", (self.root / "run" / "candidate-attempt-1.json").read_text())

    def test_secret_fields_rejected_and_existing_paths_never_overwritten(self):
        with self.assertRaises(ValueError):
            compare.assert_no_secrets({"api_key": "unit_test_secret"})
        with self.assertRaises(FileExistsError):
            compare.prepare(self.root / "preregistered")
        self.run_fake(lambda *args: self.transport())
        with self.assertRaises(FileExistsError):
            self.run_fake(lambda *args: self.fail("Network called"))

    def test_preselected_fixture_cannot_be_changed(self):
        (self.plan_path.parent / "task.csv").write_text(compare.FIXTURE + "INV-NEW,X,1,USD,paid\n")
        with self.assertRaises(ValueError):
            compare.load_plan(self.plan_path)

    def test_observed_usage_ceiling_breach_stops_further_calls(self):
        calls = []
        def sender(*args):
            calls.append(args)
            item = self.transport()
            response = json.loads(item["body"])
            response["usage"]["completion_tokens"] = self.plan["settings"]["max_output_tokens"] + 1
            item["body"] = compare.canonical(response)
            return item
        result = self.run_fake(sender)
        self.assertEqual(len(calls), 1)
        self.assertIn("stopped_reason", result)
        self.assertTrue(result["records"][0]["attempts"][0]["token_ceiling_exceeded"])

    def test_import_missing_settings_and_timing_remain_unknown(self):
        _, _, _, plan_hash = compare.load_plan(self.plan_path)
        exported = {"source_label": "FABRICATED UNIT TEST EXPORT, NOT PROVIDER EVIDENCE",
                    "plan_file_sha256": plan_hash,
                    "records": [{"side": "candidate", "example_id": compare.EXAMPLE_ID,
                                 "attempts": [{"status": "completed", "response": json.loads(self.transport(usage=False)["body"])}]}]}
        path = self.root / "fabricated-export.json"
        path.write_text(json.dumps(exported))
        result = compare.import_export(self.plan_path, path, self.root / "imported")
        attempt = result["records"][0]["attempts"][0]
        self.assertFalse(attempt["settings_verified"])
        self.assertIsNone(attempt["request_sha256"])
        self.assertIsNone(attempt["elapsed_seconds"])
        self.assertIsNone(attempt["calculated_tariff_usd"])
        self.assertFalse(result["summary"]["comparison"]["both_passed_with_verified_settings"])

    def test_prompt_hash_is_identical_but_request_hash_tracks_model_settings(self):
        result = self.run_fake(lambda *args: self.transport())
        first, second = (r["attempts"][0] for r in result["records"])
        self.assertEqual(first["prompt_sha256"], second["prompt_sha256"])
        self.assertNotEqual(first["request_sha256"], second["request_sha256"])


if __name__ == "__main__":
    unittest.main()
