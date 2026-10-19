"""Static preflight for a Harness-enabled project, not proof of agent loading."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

AGENTS = ("codex", "gemini", "claude", "generic")
ADAPTERS = {
    "gemini": "GEMINI.md",
    "claude": "CLAUDE.md",
    "generic": "AI.md",
}
IMPORT = re.compile(r"(?m)^@\./AGENTS\.md\s*$")


def check_project(project: Path, agent: str = "all") -> dict:
    root = project.expanduser().resolve()
    checks: list[dict[str, object]] = []

    def add(label: str, valid: bool, detail: str) -> None:
        checks.append({"check": label, "passed": bool(valid), "detail": detail})

    def read(relative: str) -> str | None:
        path = root / relative
        if not path.is_file():
            add(f"file:{relative}", False, "missing file")
            return None
        try:
            content = path.read_text(encoding="utf-8")
        except (UnicodeError, OSError) as exc:
            add(f"file:{relative}", False, f"unreadable UTF-8: {type(exc).__name__}")
            return None
        add(f"file:{relative}", bool(content.strip()), "present, nonempty" if content.strip() else "empty file")
        return content

    contract = read("AGENTS.md")
    router = read(".harness/START-HERE.md")
    if contract is not None:
        add("contract:startup", "## Startup protocol" in contract, "AGENTS.md startup section")
    if router is not None:
        add("router:contract", "../AGENTS.md" in router, "context router points to AGENTS.md")

    skills = root / ".agents" / "skills"
    skill_files = sorted(skills.glob("*/SKILL.md")) if skills.is_dir() else []
    add("skills:discovered", bool(skill_files), "at least one .agents/skills/*/SKILL.md")

    selected = AGENTS if agent == "all" else (agent,)
    for selected_agent in selected:
        adapter = ADAPTERS.get(selected_agent)
        if adapter is None:
            continue  # Codex's repository entry point is AGENTS.md itself.
        adapter_text = read(adapter)
        if adapter_text is None:
            continue
        if selected_agent in ("gemini", "claude"):
            add(f"adapter:{selected_agent}:import", bool(IMPORT.search(adapter_text)), "standalone @./AGENTS.md import")
        else:
            add("adapter:generic:contract", "AGENTS.md" in adapter_text, "explicit AGENTS.md reference")
        add(f"adapter:{selected_agent}:router", ".harness/START-HERE.md" in adapter_text, "explicit context-router reference")

    ready = all(bool(item["passed"]) for item in checks)
    return {
        "project_root": str(root),
        "agent": agent,
        "status": "static_ready" if ready else "blocked",
        "runtime_loading_verified": False,
        "checks": checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=Path.cwd(), help="Harness-enabled repository root")
    parser.add_argument("--agent", choices=(*AGENTS, "all"), default="all")
    parser.add_argument("--json", action="store_true", help="Machine-readable report")
    args = parser.parse_args()
    result = check_project(args.project, args.agent)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Agent entry preflight: {result['status']} ({result['agent']})")
        for item in result["checks"]:
            print(f"  {'PASS' if item['passed'] else 'FAIL'} {item['check']}: {item['detail']}")
        print("Runtime loading is NOT verified; perform the manual agent handshake.")
    return 0 if result["status"] == "static_ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
