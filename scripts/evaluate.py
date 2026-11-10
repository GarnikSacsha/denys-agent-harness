"""Evaluate offline evidence or compare reports without executing payloads."""

import argparse
import json
from pathlib import Path
import sys

if __package__:
    from .evaluation import MAX_BYTES, InputError, compare_reports, evaluate, load_json
else:
    from evaluation import MAX_BYTES, InputError, compare_reports, evaluate, load_json

DEFAULT_MANIFEST = Path(__file__).resolve().parents[1] / "evaluations/scenarios.v1.json"


def exit_code(report: dict) -> int:
    if report["report_type"] == "evaluation":
        counts = report["summary"]
        return 1 if counts["FAIL"] else 3 if counts["INCONCLUSIVE"] else 0
    return (1 if report["candidate_summary"]["FAIL"] or report["summary"]["regression"] else
            3 if report["summary"]["inconclusive"] else 0)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    evaluation = commands.add_parser("evaluate", help="Judge recorded evidence, not a live agent")
    evaluation.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    evaluation.add_argument("--evidence", type=Path, required=True)
    comparison = commands.add_parser("compare", help="Compare two compatible evaluation reports")
    comparison.add_argument("--baseline", type=Path, required=True)
    comparison.add_argument("--candidate", type=Path, required=True)
    for command in (evaluation, comparison):
        command.add_argument("--output", type=Path, help="Create a new report file; never overwrite")
    args = parser.parse_args()
    try:
        if args.command == "evaluate":
            report = evaluate(load_json(args.manifest), load_json(args.evidence))
        else:
            report = compare_reports(load_json(args.baseline), load_json(args.candidate))
        rendered = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
        if len(rendered.encode("utf-8")) > MAX_BYTES:
            rendered = json.dumps(report, separators=(",", ":"), sort_keys=True, ensure_ascii=True) + "\n"
        if len(rendered.encode("utf-8")) > MAX_BYTES:
            raise InputError("Report file size limit exceeded.")
        if args.output:
            with args.output.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(rendered)
        else:
            sys.stdout.buffer.write(rendered.encode("utf-8"))
        return exit_code(report)
    except InputError as exc:
        print(f"Evaluation input error: {exc}", file=sys.stderr)
        return 2
    except (OSError, UnicodeError):
        print("Cannot write report; output must be a new writable file.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
