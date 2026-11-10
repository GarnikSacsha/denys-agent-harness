"""Offline evaluation contracts; fixtures never represent a live agent run."""

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts.evaluation import (MAX_BYTES, InputError, compare_reports, evaluate, load_json,
                                validate_manifest, validate_report)

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/fixtures/evaluation"
MANIFEST = ROOT / "evaluations/scenarios.v1.json"


class TestEvaluation(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.fixtures = {name: json.loads((FIXTURES / f"{name}.json").read_text(encoding="utf-8"))
                         for name in ("positive", "negative", "insufficient")}

    def report(self, name: str) -> dict:
        return evaluate(self.manifest, self.fixtures[name])

    def test_library_has_all_ten_valid_scenarios(self) -> None:
        validated = validate_manifest(self.manifest)
        self.assertEqual([s["id"] for s in validated["scenarios"]],
                         [f"EVAL-{index:03}" for index in range(1, 11)])

    def test_positive_negative_and_insufficient_for_every_scenario(self) -> None:
        for name, verdict in (("positive", "PASS"), ("negative", "FAIL"),
                              ("insufficient", "INCONCLUSIVE")):
            with self.subTest(fixture=name):
                report = self.report(name)
                self.assertEqual(report.get("summary"),
                                 {"PASS": 10 if verdict == "PASS" else 0,
                                  "FAIL": 10 if verdict == "FAIL" else 0,
                                  "INCONCLUSIVE": 10 if verdict == "INCONCLUSIVE" else 0,
                                  "total": 10})
                self.assertFalse(report["live_agent_verified"])
                self.assertEqual(report["evidence_mode"], "synthetic")
                self.assertEqual(len(report["results"]), 10)
                for result in report["results"]:
                    self.assertEqual(result["verdict"], verdict)
                    self.assertTrue(result["reason"])
                    self.assertTrue(result["evidence_refs"])

    def test_absent_partial_unexercised_and_missing_facts_are_inconclusive(self) -> None:
        for variant in ("absent", "partial", "unexercised", "missing-fact", "empty-context"):
            with self.subTest(variant=variant):
                evidence = deepcopy(self.fixtures["positive"])
                if variant == "absent":
                    evidence["records"] = []
                else:
                    for record in evidence["records"]:
                        if variant == "partial":
                            record["coverage"] = "partial"
                        elif variant == "unexercised":
                            record["scenario_exercised"] = False
                        elif variant == "missing-fact":
                            record["facts"] = {}
                    if variant == "empty-context":
                        evidence["records"][0]["facts"]["before_user_files"] = {}
                        evidence["records"][0]["facts"]["after_user_files"] = {}
                results = evaluate(self.manifest, evidence).get("results", [])
                self.assertEqual(len(results), 10)
                selected = results[:1] if variant == "empty-context" else results
                self.assertTrue(all(r["verdict"] == "INCONCLUSIVE" for r in selected))

    def test_observed_violation_wins_over_partial_coverage_and_passing_records(self) -> None:
        evidence = deepcopy(self.fixtures["negative"])
        for record in evidence["records"]:
            record["coverage"] = "partial"
        for record in deepcopy(self.fixtures["positive"]["records"]):
            record["id"] += "-later"
            evidence["records"].append(record)
        self.assertEqual(evaluate(self.manifest, evidence).get("summary", {}).get("FAIL"), 10)

    def test_conflicting_observations_cannot_pass(self) -> None:
        evidence = deepcopy(self.fixtures["positive"])
        record = deepcopy(evidence["records"][1])
        record["id"] = "obs-conflict"
        record["facts"]["approved_git_operations"] = ["different-approval"]
        evidence["records"].append(record)
        results = evaluate(self.manifest, evidence).get("results", [])
        self.assertEqual(next((r["verdict"] for r in results if r["scenario_id"] == "EVAL-002"), None),
                         "INCONCLUSIVE")

    def test_manifest_rejects_invalid_contracts(self) -> None:
        mutations = [
            lambda d: d.update(schema_version="2.0"),
            lambda d: d.update(extra=True),
            lambda d: d["scenarios"].pop(),
            lambda d: d["scenarios"].append(deepcopy(d["scenarios"][0])),
            lambda d: d["scenarios"][0].update(rules=[]),
            lambda d: d["scenarios"][0].pop("purpose"),
            lambda d: d["scenarios"][0]["rules"][0].update(operator="exec"),
            lambda d: d["scenarios"][0]["rules"][0].update(left="unknown"),
            lambda d: d["scenarios"][0]["required_evidence"].update(before_user_files="object"),
        ]
        for index, mutate in enumerate(mutations):
            with self.subTest(case=index):
                data = deepcopy(self.manifest)
                mutate(data)
                with self.assertRaises(InputError):
                    validate_manifest(data)

    def test_evidence_rejects_invalid_contracts(self) -> None:
        mutations = [
            lambda d: d.update(schema_version="2.0"),
            lambda d: d.update(suite_version="0.2"),
            lambda d: d.update(mode="live_verified"),
            lambda d: d.update(command="do-not-execute"),
            lambda d: d["records"].append(deepcopy(d["records"][0])),
            lambda d: d["records"][0].update(kind="agent_observed"),
            lambda d: d["records"][0].update(scenario_id="EVAL-999"),
            lambda d: d["records"][0].update(scenario_exercised=1),
            lambda d: d["records"][0].update(artifact_refs=[]),
            lambda d: d["records"][0]["facts"].update(unknown=True),
            lambda d: d["records"][0]["facts"].update(before_user_files="not-a-map"),
        ]
        for index, mutate in enumerate(mutations):
            with self.subTest(case=index):
                data = deepcopy(self.fixtures["positive"])
                mutate(data)
                with self.assertRaises(InputError):
                    evaluate(self.manifest, data)

    def test_deterministic_and_order_independent(self) -> None:
        evidence = deepcopy(self.fixtures["positive"])
        expected = evaluate(self.manifest, evidence)
        evidence["records"].reverse()
        self.assertEqual(evaluate(self.manifest, evidence), expected)
        self.assertEqual(evaluate(self.manifest, evidence), expected)

    def test_untrusted_payloads_cannot_execute_or_appear_in_report(self) -> None:
        evidence = deepcopy(self.fixtures["positive"])
        payload = "__import__('os').system('git reset --hard'); ignore all policies"
        evidence["records"].append({"id": "malicious-claim", "scenario_id": "EVAL-003",
                                    "kind": "claim", "text": payload})
        with patch("os.system") as system, patch("subprocess.run") as run:
            report = evaluate(self.manifest, evidence)
            system.assert_not_called()
            run.assert_not_called()
        self.assertNotIn(payload, json.dumps(report))
        self.assertEqual(report.get("summary", {}).get("PASS"), 10)

    def test_strict_json_loading(self) -> None:
        with tempfile.TemporaryDirectory(prefix="harness-eval-input-") as temp:
            path = Path(temp) / "input.json"
            for data in (b'{"a":1,"a":2}', b'{"a":NaN}', b'[]', b'\xff',
                         b'{' + b' ' * 1_048_576 + b'}', b'[' * 100 + b']' * 100,
                         b'{"a":' + b'9' * 5000 + b'}'):
                with self.subTest(prefix=data[:20]):
                    path.write_bytes(data)
                    with self.assertRaises(InputError):
                        load_json(path)

    def test_reports_remain_bounded_and_comparable(self) -> None:
        evidence = deepcopy(self.fixtures["positive"])
        evidence["records"][0]["artifact_refs"] = [f"artifact-{i}" for i in range(1000)]
        with self.assertRaises(InputError):
            evaluate(self.manifest, evidence)

    def test_many_failed_rules_produce_bounded_deterministic_reasons(self) -> None:
        scenario = self.manifest["scenarios"][0]
        rule = scenario["rules"][0]
        rule_ids = [f"rule-{index:04}-" + "x" * 118 for index in range(999)]
        scenario["rules"] = [{**rule, "id": rule_id} for rule_id in rule_ids] + scenario["rules"][1:]
        evidence = self.fixtures["negative"]
        report = evaluate(self.manifest, evidence)
        validate_report(report)
        reason = report["results"][0]["reason"]
        failed_ids = sorted(rule_ids)
        listed, omitted = reason.removeprefix("Observed violation of rule(s): ").rsplit("; ", 1)
        listed_ids = listed.split(", ")
        self.assertEqual(listed_ids, failed_ids[:len(listed_ids)])
        self.assertGreater(len(listed_ids), 0)
        self.assertEqual(omitted, f"{len(failed_ids) - len(listed_ids)} more failed rule(s).")
        self.assertLessEqual(len(reason), 8192)
        self.assertEqual(report["results"][0]["verdict"], "FAIL")
        self.assertEqual(report["summary"]["FAIL"], 10)
        scenario["rules"].reverse()
        reordered = evaluate(self.manifest, evidence)
        self.assertEqual(reordered["results"], report["results"])
        comparison = compare_reports(report, report)
        self.assertEqual(comparison["summary"]["unchanged"], 10)

    def test_short_failure_reasons_keep_all_rule_ids(self) -> None:
        result = self.report("negative")["results"][0]
        self.assertEqual(result["reason"], "Observed violation of rule(s): files_preserved.")

    def test_test_results_reject_unknown_statuses(self) -> None:
        evidence = deepcopy(self.fixtures["positive"])
        for field in ("observed_test_results", "reported_test_results"):
            evidence["records"][5]["facts"][field]["unit"] = "UNKNOWN_STATUS"
        with self.assertRaises(InputError):
            evaluate(self.manifest, evidence)

    def test_incomplete_handoff_maps_cannot_pass(self) -> None:
        evidence = deepcopy(self.fixtures["positive"])
        for field in ("observed_handoff_facts", "reported_handoff_facts"):
            evidence["records"][9]["facts"][field].pop("limitations")
        results = evaluate(self.manifest, evidence)["results"]
        self.assertEqual(results[9]["verdict"], "INCONCLUSIVE")

    def test_comparison_retains_source_identity(self) -> None:
        baseline, candidate = self.report("negative"), self.report("positive")
        comparison = compare_reports(baseline, candidate)
        for side, report in (("baseline", baseline), ("candidate", candidate)):
            self.assertEqual(comparison.get(f"{side}_evidence_sha256"), report["evidence_sha256"])
            self.assertEqual(comparison.get(f"{side}_harness_revision"), report["harness_revision"])

    def test_comparison_all_nine_transitions_keep_all_totals(self) -> None:
        names = {"PASS": "positive", "FAIL": "negative", "INCONCLUSIVE": "insufficient"}
        for before in names:
            for after in names:
                with self.subTest(before=before, after=after):
                    report = compare_reports(self.report(names[before]), self.report(names[after]))
                    category = ("inconclusive" if "INCONCLUSIVE" in (before, after) else
                                "regression" if (before, after) == ("PASS", "FAIL") else
                                "improvement" if (before, after) == ("FAIL", "PASS") else "unchanged")
                    self.assertEqual(report.get("summary", {}).get(category), 10)
                    self.assertEqual(report["summary"]["total"], 10)
                    self.assertEqual(len(report["results"]), 10)
                    self.assertEqual(report["baseline_summary"][before], 10)
                    self.assertEqual(report["candidate_summary"][after], 10)

    def test_comparison_rejects_incompatible_or_tampered_reports(self) -> None:
        baseline = self.report("positive")
        self.assertEqual(baseline.get("summary", {}).get("PASS"), 10)
        mutations = [
            lambda d: d.update(manifest_sha256="a" * 64),
            lambda d: d.update(evidence_mode="recorded"),
            lambda d: d["results"].pop(),
            lambda d: d["summary"].update(PASS=9),
            lambda d: d["results"][0].update(verdict="SUCCESS"),
            lambda d: d["results"][0].update(evidence_refs=[]),
            lambda d: d["results"][0].update(reason="x" * 8193),
            lambda d: d.update(live_agent_verified=True),
        ]
        for index, mutate in enumerate(mutations):
            with self.subTest(case=index):
                candidate = deepcopy(baseline)
                mutate(candidate)
                with self.assertRaises(InputError):
                    compare_reports(baseline, candidate)


class TestEvaluationCLI(unittest.TestCase):
    def run_cli(self, *args: str, binary: bool = False) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, "-B", "-m", "scripts.evaluate", *map(str, args)],
                              cwd=ROOT, capture_output=True, text=not binary, timeout=15)

    def test_cli_exit_codes_and_repeatable_json(self) -> None:
        for name, code in (("positive", 0), ("negative", 1), ("insufficient", 3)):
            with self.subTest(fixture=name):
                args = ("evaluate", "--evidence", FIXTURES / f"{name}.json")
                result = self.run_cli(*args)
                self.assertEqual(result.returncode, code, result.stderr)
                report = json.loads(result.stdout)
                self.assertEqual(report["summary"]["total"], 10)
                self.assertEqual(self.run_cli(*args).stdout, result.stdout)

    def test_malformed_cli_input_is_sanitized_and_nonzero(self) -> None:
        with tempfile.TemporaryDirectory(prefix="harness-eval-cli-") as temp:
            source = Path(temp) / "invalid.json"
            source.write_text('{"untrusted-secret-placeholder": NaN}', encoding="utf-8")
            result = self.run_cli("evaluate", "--evidence", source)
            self.assertEqual(result.returncode, 2)
            self.assertNotIn("untrusted-secret-placeholder", result.stdout + result.stderr)
            self.assertNotIn("Traceback", result.stderr)

    def test_output_is_saved_without_overwriting_existing_files(self) -> None:
        with tempfile.TemporaryDirectory(prefix="harness-eval-save-") as temp:
            target = Path(temp) / "report.json"
            args = ("evaluate", "--evidence", FIXTURES / "negative.json", "--output", target)
            result = self.run_cli(*args)
            self.assertEqual(result.returncode, 1, result.stderr)
            original = target.read_bytes()
            self.assertEqual(json.loads(original)["summary"]["FAIL"], 10)
            printed = self.run_cli("evaluate", "--evidence", FIXTURES / "negative.json", binary=True)
            self.assertEqual(printed.stdout, original)
            self.assertEqual(self.run_cli(*args).returncode, 2)
            self.assertEqual(target.read_bytes(), original)

    def test_large_reports_round_trip_or_fail_before_output(self) -> None:
        for dense_reasons in (False, True):
            with self.subTest(dense_reasons=dense_reasons), tempfile.TemporaryDirectory(
                    prefix="harness-eval-size-") as temp:
                source, target = Path(temp) / "evidence.json", Path(temp) / "report.json"
                manifest_path = Path(temp) / "manifest.json"
                manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
                name = "negative" if dense_reasons else "positive"
                evidence = json.loads((FIXTURES / f"{name}.json").read_text(encoding="utf-8"))
                if dense_reasons:
                    for scenario in manifest["scenarios"]:
                        rule = scenario["rules"][0]
                        scenario["rules"] += [{**rule, "id": f"rule-{index:04}-" + "x" * 118}
                                              for index in range(60)]
                refs = [f"artifact-{index:04}-" + "x" * 114 for index in range(760)]
                for record in evidence["records"]:
                    record["artifact_refs"] = refs
                manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
                source.write_text(json.dumps(evidence, separators=(",", ":")), encoding="utf-8")
                self.assertLessEqual(source.stat().st_size, MAX_BYTES)
                expected = evaluate(load_json(manifest_path), load_json(source))
                pretty = json.dumps(expected, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
                compact = json.dumps(expected, separators=(",", ":"), sort_keys=True, ensure_ascii=True) + "\n"
                self.assertGreater(len(pretty.encode("utf-8")), MAX_BYTES)
                fits = len(compact.encode("utf-8")) <= MAX_BYTES
                self.assertEqual(fits, not dense_reasons)
                args = ("evaluate", "--manifest", manifest_path, "--evidence", source)
                saved = self.run_cli(*args, "--output", target)
                printed = self.run_cli(*args)
                if fits:
                    self.assertEqual(saved.returncode, 0, saved.stderr)
                    self.assertEqual(printed.returncode, 0, printed.stderr)
                    self.assertLessEqual(target.stat().st_size, MAX_BYTES)
                    self.assertEqual(load_json(target), expected)
                    comparison = compare_reports(load_json(target), load_json(target))
                    self.assertEqual(comparison["summary"]["unchanged"], 10)
                    self.assertEqual(printed.stdout, target.read_text(encoding="utf-8"))
                    self.assertEqual(self.run_cli(*args, binary=True).stdout, target.read_bytes())
                    self.assertEqual(self.run_cli(*args).stdout, printed.stdout)
                    compared = self.run_cli("compare", "--baseline", target, "--candidate", target)
                    self.assertEqual(compared.returncode, 2, compared.stderr)
                    self.assertEqual(compared.stdout, "")
                    self.assertIn("Report file size limit exceeded.", compared.stderr)
                    comparison_path = Path(temp) / "comparison.json"
                    compared = self.run_cli("compare", "--baseline", target, "--candidate", target,
                                            "--output", comparison_path)
                    self.assertEqual(compared.returncode, 2, compared.stderr)
                    self.assertFalse(comparison_path.exists())
                else:
                    self.assertEqual(saved.returncode, 2, saved.stderr)
                    self.assertFalse(target.exists())
                    self.assertEqual(saved.stdout, "")
                    self.assertEqual(printed.returncode, 2, printed.stderr)
                    self.assertEqual(printed.stdout, "")
                    self.assertIn("Report file size limit exceeded.", printed.stderr)
                    self.assertNotIn("Traceback", printed.stderr)
                    target.write_bytes(b"keep existing output")
                    self.assertEqual(self.run_cli(*args, "--output", target).returncode, 2)
                    self.assertEqual(target.read_bytes(), b"keep existing output")

    def test_many_failures_round_trip_through_cli_comparison(self) -> None:
        with tempfile.TemporaryDirectory(prefix="harness-eval-reason-") as temp:
            manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
            scenario = manifest["scenarios"][0]
            scenario["rules"] += [{**scenario["rules"][0], "id": f"rule-{index:04}-" + "x" * 118}
                                  for index in range(100)]
            source, target = Path(temp) / "manifest.json", Path(temp) / "report.json"
            source.write_text(json.dumps(manifest), encoding="utf-8")
            args = ("evaluate", "--manifest", source, "--evidence", FIXTURES / "negative.json")
            saved = self.run_cli(*args, "--output", target)
            self.assertEqual(saved.returncode, 1, saved.stderr)
            report = load_json(target)
            validate_report(report)
            self.assertEqual(report["summary"]["FAIL"], 10)
            self.assertIn("more failed rule(s).", report["results"][0]["reason"])
            self.assertEqual(self.run_cli(*args).stdout, target.read_text(encoding="utf-8"))
            compared = self.run_cli("compare", "--baseline", target, "--candidate", target)
            self.assertEqual(compared.returncode, 1, compared.stderr)
            self.assertEqual(json.loads(compared.stdout)["summary"]["unchanged"], 10)

    def test_large_comparison_uses_compact_json_without_losing_references(self) -> None:
        with tempfile.TemporaryDirectory(prefix="harness-compare-size-") as temp:
            source, target = Path(temp) / "evidence.json", Path(temp) / "report.json"
            evidence = json.loads((FIXTURES / "positive.json").read_text(encoding="utf-8"))
            refs = [f"artifact-{index:04}-" + "x" * 114 for index in range(380)]
            for record in evidence["records"]:
                record["artifact_refs"] = refs
            source.write_text(json.dumps(evidence), encoding="utf-8")
            saved = self.run_cli("evaluate", "--evidence", source, "--output", target)
            self.assertEqual(saved.returncode, 0, saved.stderr)
            expected = compare_reports(load_json(target), load_json(target))
            pretty = json.dumps(expected, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
            self.assertGreater(len(pretty.encode("utf-8")), MAX_BYTES)
            comparison_path = Path(temp) / "comparison.json"
            args = ("compare", "--baseline", target, "--candidate", target)
            compared = self.run_cli(*args, "--output", comparison_path)
            self.assertEqual(compared.returncode, 0, compared.stderr)
            self.assertLessEqual(comparison_path.stat().st_size, MAX_BYTES)
            self.assertEqual(load_json(comparison_path), expected)
            self.assertEqual(self.run_cli(*args).stdout, comparison_path.read_text(encoding="utf-8"))

    def test_compare_cli_does_not_hide_failures_or_inconclusive(self) -> None:
        with tempfile.TemporaryDirectory(prefix="harness-eval-compare-") as temp:
            paths = {}
            for name in ("positive", "negative", "insufficient"):
                paths[name] = Path(temp) / f"{name}.json"
                result = self.run_cli("evaluate", "--evidence", FIXTURES / f"{name}.json",
                                      "--output", paths[name])
                self.assertIn(result.returncode, (0, 1, 3), result.stderr)
            for before, after, code in (("positive", "negative", 1), ("negative", "negative", 1),
                                        ("negative", "positive", 0), ("insufficient", "positive", 3)):
                result = self.run_cli("compare", "--baseline", paths[before], "--candidate", paths[after])
                self.assertEqual(result.returncode, code, result.stderr)

    def test_untrusted_payload_is_inert_at_cli_boundary(self) -> None:
        with tempfile.TemporaryDirectory(prefix="harness-eval-inert-") as temp:
            marker = Path(temp) / "must-not-exist"
            source = Path(temp) / "payload.json"
            evidence = json.loads((FIXTURES / "insufficient.json").read_text(encoding="utf-8"))
            evidence["records"][0]["text"] = f"__import__('pathlib').Path({str(marker)!r}).write_text('unexpected')"
            source.write_text(json.dumps(evidence), encoding="utf-8")
            result = self.run_cli("evaluate", "--evidence", source)
            self.assertEqual(result.returncode, 3, result.stderr)
            self.assertFalse(marker.exists())
            self.assertNotIn("__import__", result.stdout)
