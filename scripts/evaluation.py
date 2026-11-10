"""Strict data-only evaluation of recorded evidence; no agent execution."""

from collections import Counter
import hashlib
import json
from pathlib import Path
import re

SCHEMA_VERSION = "1.0"
ENGINE_VERSION = "0.1"
MAX_BYTES = 1_048_576
SCENARIO_IDS = {f"EVAL-{index:03}" for index in range(1, 11)}
VERDICTS = ("PASS", "FAIL", "INCONCLUSIVE")
FACT_TYPES = {"string_list", "string_map", "test_results", "handoff_facts"}
TEST_STATUSES = {"PASS", "FAIL", "ERROR", "NOT_RUN", "SKIPPED"}
HANDOFF_FIELDS = {"branch", "head", "changes", "tests", "limitations"}
OPERATORS = {"equal", "subset", "disjoint", "empty", "contains"}


class InputError(ValueError):
    """A safe diagnostic without input payloads or filesystem details."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise InputError(message)


def bounded(value: object, depth: int = 0) -> None:
    require(depth <= 32, "Input nesting limit exceeded.")
    if type(value) is dict:
        require(len(value) <= 2048, "Object size limit exceeded.")
        for key, item in value.items():
            text(key)
            bounded(key, depth + 1)
            bounded(item, depth + 1)
    elif type(value) is list:
        require(len(value) <= 2048, "Array size limit exceeded.")
        for item in value:
            bounded(item, depth + 1)
    elif type(value) is str:
        require(len(value) <= 8192, "Text size limit exceeded.")
        try:
            value.encode("utf-8")
        except UnicodeError:
            raise InputError("Invalid Unicode text.") from None
    else:
        require(type(value) is bool or (type(value) is int and abs(value) < 2**63),
                "Unsupported JSON value type.")


def text(value: object) -> None:
    require(type(value) is str and 0 < len(value.strip()) <= 8192, "Expected nonempty text.")


def identifier(value: object) -> None:
    require(type(value) is str and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}", value) is not None,
            "Expected an opaque identifier.")


def fields(value: object, expected: set[str]) -> None:
    require(type(value) is dict and set(value) == expected, "Missing or unexpected object fields.")


def array(value: object, minimum: int = 0) -> None:
    require(type(value) is list and minimum <= len(value) <= 1000, "Invalid array size or type.")


def string_list(value: object, minimum: int = 0, opaque: bool = False) -> None:
    array(value, minimum)
    for item in value:
        identifier(item) if opaque else text(item)
    require(len(set(value)) == len(value), "Duplicate list entries.")


def unique_objects(pairs: list[tuple]) -> dict:
    result = {}
    for key, value in pairs:
        require(key not in result, "Duplicate JSON object key.")
        result[key] = value
    return result


def reject_constant(value: str) -> None:
    raise InputError("Nonfinite JSON numbers are not supported.")


def load_json(path: Path) -> dict:
    try:
        require(path.is_file(), "Input must be a regular JSON file.")
        with path.open("rb") as stream:
            raw = stream.read(MAX_BYTES + 1)
        require(len(raw) <= MAX_BYTES, "Input file size limit exceeded.")
        data = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=unique_objects,
                          parse_constant=reject_constant)
        require(type(data) is dict, "Expected a JSON object.")
        bounded(data)
        return data
    except InputError:
        raise
    except (OSError, ValueError, RecursionError):
        raise InputError("Cannot read valid bounded UTF-8 JSON input.") from None


def validate_manifest(data: dict) -> dict:
    bounded(data)
    fields(data, {"schema_version", "suite_id", "suite_version", "scenarios"})
    require(data["schema_version"] == SCHEMA_VERSION and data["suite_version"] == ENGINE_VERSION,
            "Unsupported manifest version.")
    identifier(data["suite_id"])
    array(data["scenarios"], 10)
    seen = set()
    for scenario in data["scenarios"]:
        fields(scenario, {"id", "title", "purpose", "applicable_policy", "required_evidence",
                          "context_fields", "rules", "expected_outcome"})
        identifier(scenario["id"])
        require(scenario["id"] in SCENARIO_IDS and scenario["id"] not in seen, "Invalid scenario ID.")
        seen.add(scenario["id"])
        for key in ("title", "purpose", "expected_outcome"):
            text(scenario[key])
        string_list(scenario["applicable_policy"], 1)
        required = scenario["required_evidence"]
        require(type(required) is dict and bool(required), "Required evidence must be declared.")
        for name, kind in required.items():
            identifier(name)
            require(type(kind) is str and kind in FACT_TYPES, "Unsupported fact type.")
        string_list(scenario["context_fields"])
        require(set(scenario["context_fields"]) <= set(required), "Unknown context field.")
        array(scenario["rules"], 1)
        rule_ids, used = set(), set()
        for rule in scenario["rules"]:
            require(type(rule) is dict, "Expected a rule object.")
            operator = rule.get("operator")
            require(type(operator) is str and operator in OPERATORS, "Unsupported rule operator.")
            keys = {"id", "operator", "left", "failure_condition"}
            fields(rule, keys if operator == "empty" else keys | {"right"})
            identifier(rule["id"])
            require(rule["id"] not in rule_ids, "Duplicate rule ID.")
            rule_ids.add(rule["id"])
            text(rule["failure_condition"])
            operands = [rule["left"]] + ([] if operator == "empty" else [rule["right"]])
            for operand in operands:
                identifier(operand)
                require(operand in required, "Unknown rule operand.")
                used.add(operand)
            kinds = {required[operand] for operand in operands}
            require(len(kinds) == 1, "Rule operand types must match.")
            if operator in ("subset", "disjoint"):
                require(kinds == {"string_list"}, "Set rules require lists.")
            if operator == "contains":
                require(kinds == {"string_map"}, "Contains requires maps.")
        require(used == set(required), "Every required fact must participate in a rule.")
    require(seen == SCENARIO_IDS, "All ten scenarios must be present.")
    return data


def validate_evidence(data: dict, manifest: dict) -> None:
    bounded(data)
    fields(data, {"schema_version", "suite_version", "run_id", "harness_revision", "mode", "records"})
    require(data["schema_version"] == SCHEMA_VERSION and data["suite_version"] == manifest["suite_version"],
            "Unsupported or incompatible evidence version.")
    require(data["mode"] in ("synthetic", "recorded"), "Unsupported evidence mode.")
    identifier(data["run_id"])
    identifier(data["harness_revision"])
    array(data["records"])
    scenarios = {s["id"]: s for s in manifest["scenarios"]}
    seen = set()
    references = set()
    for record in data["records"]:
        require(type(record) is dict, "Expected an evidence record.")
        kind = record.get("kind")
        require(kind in ("observation", "claim"), "Unsupported evidence kind.")
        common = {"id", "scenario_id", "kind"}
        fields(record, common | ({"text"} if kind == "claim" else
                                 {"coverage", "scenario_exercised", "facts", "artifact_refs"}))
        identifier(record["id"])
        identifier(record["scenario_id"])
        require(record["id"] not in seen and record["scenario_id"] in scenarios, "Invalid evidence ID.")
        seen.add(record["id"])
        references.add(record["id"])
        if kind == "claim":
            text(record["text"])
            continue
        require(record["coverage"] in ("complete", "partial"), "Unsupported trace coverage.")
        require(type(record["scenario_exercised"]) is bool, "Exercise flag must be boolean.")
        string_list(record["artifact_refs"], 1, opaque=True)
        references.update(record["artifact_refs"])
        facts, required = record["facts"], scenarios[record["scenario_id"]]["required_evidence"]
        require(type(facts) is dict and set(facts) <= set(required), "Unknown observation facts.")
        for name, value in facts.items():
            if required[name] == "string_list":
                string_list(value)
            else:
                require(type(value) is dict, "Expected a string map.")
                for key, item in value.items():
                    text(key)
                    text(item)
                if required[name] == "test_results":
                    require(set(value.values()) <= TEST_STATUSES, "Unsupported test result status.")
                elif required[name] == "handoff_facts":
                    require(set(value) <= HANDOFF_FIELDS, "Unknown handoff fact.")
    require(len(references) <= 1000, "Evidence reference limit exceeded.")


def rule_holds(rule: dict, facts: dict) -> bool | None:
    left, right = rule["left"], rule.get("right")
    if left not in facts or (right is not None and right not in facts):
        return None
    a = facts[left]
    if rule["operator"] == "empty":
        return not a
    b = facts[right]
    if rule["operator"] == "equal":
        return a == b
    if rule["operator"] == "subset":
        return set(a) <= set(b)
    if rule["operator"] == "disjoint":
        return set(a).isdisjoint(b)
    return all(key in b and b[key] == value for key, value in a.items())


def fingerprint(data: dict) -> str:
    return hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=True,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def totals(results: list[dict], key: str, categories: tuple[str, ...]) -> dict:
    counts = Counter(result[key] for result in results)
    return {**{category: counts[category] for category in categories}, "total": len(results)}


def evaluate_scenario(scenario: dict, records: list[dict]) -> dict:
    observations = [r for r in records if r["kind"] == "observation"]
    failed, observed, refs = set(), {}, set()
    complete, conflict = False, False
    for record in records:
        refs.add(record["id"])
        refs.update(record.get("artifact_refs", []))
    for record in observations:
        facts = record["facts"]
        outcomes = [rule_holds(rule, facts) for rule in scenario["rules"]]
        failed.update(rule["id"] for rule, outcome in zip(scenario["rules"], outcomes) if outcome is False)
        for name, value in facts.items():
            if name in observed and observed[name] != value:
                conflict = True
            observed[name] = value
        complete |= (record["coverage"] == "complete" and record["scenario_exercised"]
                     and set(facts) == set(scenario["required_evidence"])
                     and all(facts.get(name) for name in scenario["context_fields"])
                     and all(set(facts.get(name, {})) == HANDOFF_FIELDS
                             for name, kind in scenario["required_evidence"].items() if kind == "handoff_facts")
                     and all(outcome is True for outcome in outcomes))
    if failed:
        verdict, reason = "FAIL", "Observed violation of rule(s): " + ", ".join(sorted(failed)) + "."
    elif conflict:
        verdict, reason = "INCONCLUSIVE", "Conflicting observations require reconciliation."
    elif complete:
        verdict, reason = "PASS", "All rules satisfied by complete exercised observations."
    else:
        verdict, reason = "INCONCLUSIVE", "Missing complete exercised observations, required facts or context; claims are insufficient."
    return {"scenario_id": scenario["id"], "verdict": verdict, "reason": reason,
            "evidence_refs": sorted(refs)}


def evaluate(manifest: dict, evidence: dict) -> dict:
    validate_manifest(manifest)
    validate_evidence(evidence, manifest)
    records = sorted(evidence["records"], key=lambda r: r["id"])
    results = [evaluate_scenario(s, [r for r in records if r["scenario_id"] == s["id"]])
               for s in sorted(manifest["scenarios"], key=lambda s: s["id"])]
    return {"schema_version": SCHEMA_VERSION, "engine_version": ENGINE_VERSION,
            "report_type": "evaluation", "suite_id": manifest["suite_id"],
            "suite_version": manifest["suite_version"], "manifest_sha256": fingerprint(manifest),
            "evidence_sha256": fingerprint({**evidence, "records": records}),
            "run_id": evidence["run_id"], "harness_revision": evidence["harness_revision"],
            "evidence_mode": evidence["mode"], "live_agent_verified": False,
            "results": results, "summary": totals(results, "verdict", VERDICTS)}


def validate_report(data: dict) -> None:
    bounded(data)
    fields(data, {"schema_version", "engine_version", "report_type", "suite_id", "suite_version",
                  "manifest_sha256", "evidence_sha256", "run_id", "harness_revision", "evidence_mode",
                  "live_agent_verified", "results", "summary"})
    require(data["schema_version"] == SCHEMA_VERSION and data["engine_version"] == ENGINE_VERSION
            and data["suite_version"] == ENGINE_VERSION and data["report_type"] == "evaluation",
            "Unsupported report version or type.")
    require(data["live_agent_verified"] is False, "Offline reports cannot verify live agents.")
    require(data["evidence_mode"] in ("synthetic", "recorded"), "Unsupported report evidence mode.")
    for key in ("suite_id", "run_id", "harness_revision"):
        identifier(data[key])
    for key in ("manifest_sha256", "evidence_sha256"):
        require(type(data[key]) is str and re.fullmatch(r"[0-9a-f]{64}", data[key]) is not None,
                "Invalid report fingerprint.")
    array(data["results"], 10)
    seen = set()
    for result in data["results"]:
        fields(result, {"scenario_id", "verdict", "reason", "evidence_refs"})
        identifier(result["scenario_id"])
        require(result["scenario_id"] in SCENARIO_IDS and result["scenario_id"] not in seen,
                "Invalid result scenario ID.")
        seen.add(result["scenario_id"])
        require(result["verdict"] in VERDICTS, "Invalid verdict.")
        text(result["reason"])
        string_list(result["evidence_refs"], 0 if result["verdict"] == "INCONCLUSIVE" else 1, opaque=True)
    require(seen == SCENARIO_IDS, "All ten results must be present.")
    fields(data["summary"], {*VERDICTS, "total"})
    require(all(type(value) is int for value in data["summary"].values())
            and data["summary"] == totals(data["results"], "verdict", VERDICTS), "Inconsistent report totals.")


def compare_reports(baseline: dict, candidate: dict) -> dict:
    validate_report(baseline)
    validate_report(candidate)
    for key in ("suite_id", "suite_version", "manifest_sha256", "evidence_mode"):
        require(baseline[key] == candidate[key], "Reports use incompatible suites, rules or evidence modes.")
    before = {r["scenario_id"]: r for r in baseline["results"]}
    results = []
    for after in sorted(candidate["results"], key=lambda r: r["scenario_id"]):
        old = before[after["scenario_id"]]
        pair = old["verdict"], after["verdict"]
        category = ("inconclusive" if "INCONCLUSIVE" in pair else
                    "regression" if pair == ("PASS", "FAIL") else
                    "improvement" if pair == ("FAIL", "PASS") else "unchanged")
        results.append({"scenario_id": after["scenario_id"], "baseline": pair[0], "candidate": pair[1],
                        "category": category, "baseline_refs": old["evidence_refs"],
                        "candidate_refs": after["evidence_refs"]})
    return {"schema_version": SCHEMA_VERSION, "engine_version": ENGINE_VERSION, "report_type": "comparison",
            "suite_id": baseline["suite_id"], "suite_version": baseline["suite_version"],
            "manifest_sha256": baseline["manifest_sha256"], "evidence_mode": baseline["evidence_mode"],
            "live_agent_verified": False, "baseline_run_id": baseline["run_id"],
            "candidate_run_id": candidate["run_id"],
            "baseline_evidence_sha256": baseline["evidence_sha256"],
            "candidate_evidence_sha256": candidate["evidence_sha256"],
            "baseline_harness_revision": baseline["harness_revision"],
            "candidate_harness_revision": candidate["harness_revision"],
            "baseline_summary": baseline["summary"],
            "candidate_summary": candidate["summary"], "results": results,
            "summary": totals(results, "category", ("regression", "improvement", "unchanged", "inconclusive"))}
