from __future__ import annotations

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "README.md",
    "AGENTS.md",
    "GEMINI.md",
    "CLAUDE.md",
    "AI.md",
    ".harness/START-HERE.md",
    ".harness/PROFILE.md",
    ".harness/POLICIES.md",
    ".harness/SECURITY.md",
    ".harness/CODE-QUALITY.md",
    ".harness/WORKFLOWS.md",
    ".harness/PROJECT-PATTERNS.md",
    ".harness/templates/AGENTS.project.template.md",
    ".harness/templates/TASK.md",
    ".harness/templates/HANDOFF.md",
    ".harness/templates/DECISION.md",
    ".harness/templates/SECURITY.project.template.md",
    ".harness/templates/THREAT-MODEL.md",
    ".harness/templates/DATA-INVENTORY.md",
    ".harness/templates/ACCESS-MATRIX.md",
    ".harness/templates/CODE-REVIEW.md",
    ".harness/templates/INCIDENT-RESPONSE.md",
    ".harness/templates/DEPLOYMENT-GATE.md",
)

SKILL_FILES = tuple((ROOT / ".agents" / "skills").glob("*/SKILL.md"))


def validate_skill(path: Path) -> list[str]:
    errors: list[str] = []
    label = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path.name
    try:
        text = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as exc:
        return [f"{label}: unreadable skill ({type(exc).__name__})"]
    lines = text.splitlines()
    if not lines or lines[0] != "---" or "---" not in lines[1:]:
        return [f"{label}: missing or unclosed frontmatter"]
    fields: dict[str, str] = {}
    for line in lines[1:lines.index("---", 1)]:
        if not line.strip():
            continue
        match = re.fullmatch(r"(name|description):[ \t]+(.+)", line)
        if not match:
            errors.append(f"{label}: expected flat name/description fields")
            continue
        key, value = match.groups()
        value = value.strip()
        if key in fields or not value or value[0] in "\"'[{|>&*!#" or ": " in value:
            errors.append(f"{label}: invalid or duplicate {key}")
        fields[key] = value
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", fields.get("name", "")):
        errors.append(f"{label}: invalid or missing name")
    if not fields.get("description"):
        errors.append(f"{label}: missing description")
    if "TODO" in text or "[TODO" in text:
        errors.append(f"{label}: contains TODO placeholder")
    return errors


def main() -> int:
    errors: list[str] = []

    for relative in REQUIRED_FILES:
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"Missing required file: {relative}")
        elif not path.read_text(encoding="utf-8").strip():
            errors.append(f"Required file is empty: {relative}")

    if not SKILL_FILES:
        errors.append("No skills found under .agents/skills")
    for skill_file in SKILL_FILES:
        errors.extend(validate_skill(skill_file))

    agents_text = (ROOT / "AGENTS.md").read_text(encoding="utf-8") if (ROOT / "AGENTS.md").exists() else ""
    for required_heading in ("## Startup protocol", "## Scope and autonomy", "## Security gate", "## Code quality and independent review gate", "## Stopping criteria", "## Final handoff"):
        if required_heading not in agents_text:
            errors.append(f"AGENTS.md missing required section: {required_heading}")
    for required_phrase in ("RED → GREEN → REFACTOR", "TDD exception"):
        if required_phrase not in agents_text:
            errors.append(f"AGENTS.md missing required TDD contract: {required_phrase}")

    required_sections = {
        ".harness/SECURITY.md": (
            "## Data classification",
            "## Agent execution boundary",
            "## Database safety",
            "## Incident response",
        ),
        ".harness/CODE-QUALITY.md": (
            "## Test quality",
            "### TDD exceptions",
            "## Review independence",
            "## Finding severity",
            "## Acceptance gate",
        ),
        ".harness/WORKFLOWS.md": (
            "## Security review gate",
            "## Code review gate",
        ),
    }
    for relative, headings in required_sections.items():
        path = ROOT / relative
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        for heading in headings:
            if heading not in text:
                errors.append(f"{relative} missing required section: {heading}")

    if errors:
        print("Harness validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Harness validation passed: {len(REQUIRED_FILES)} core files and {len(SKILL_FILES)} skills checked.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
