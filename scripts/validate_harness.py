from __future__ import annotations

from pathlib import Path
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
    ".harness/WORKFLOWS.md",
    ".harness/PROJECT-PATTERNS.md",
    ".harness/templates/AGENTS.project.template.md",
    ".harness/templates/TASK.md",
    ".harness/templates/HANDOFF.md",
    ".harness/templates/DECISION.md",
)

SKILL_FILES = tuple((ROOT / ".agents" / "skills").glob("*/SKILL.md"))


def validate_skill(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        errors.append(f"{path.relative_to(ROOT)}: missing YAML frontmatter")
    if "\nname:" not in text or "\ndescription:" not in text:
        errors.append(f"{path.relative_to(ROOT)}: missing name or description")
    if "TODO" in text or "[TODO" in text:
        errors.append(f"{path.relative_to(ROOT)}: contains TODO placeholder")
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
    for required_heading in ("## Startup protocol", "## Scope and autonomy", "## Stopping criteria", "## Final handoff"):
        if required_heading not in agents_text:
            errors.append(f"AGENTS.md missing required section: {required_heading}")

    if errors:
        print("Harness validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Harness validation passed: {len(REQUIRED_FILES)} core files and {len(SKILL_FILES)} skills checked.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
