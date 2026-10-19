"""Deterministic checks for the static agent-integration preflight."""

from __future__ import annotations

from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

from scripts.check_agent_entry import check_project

ROOT = Path(__file__).resolve().parents[1]


class TestAgentEntry(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory(prefix="harness-entry-test-")
        self.root = Path(self.tempdir.name)
        (self.root / ".harness").mkdir()
        (self.root / ".agents" / "skills" / "example").mkdir(parents=True)
        (self.root / "AGENTS.md").write_text("# Contract\n## Startup protocol\n", encoding="utf-8")
        (self.root / ".harness" / "START-HERE.md").write_text(
            "Read `../AGENTS.md` first.\n", encoding="utf-8"
        )
        (self.root / ".agents" / "skills" / "example" / "SKILL.md").write_text(
            "---\nname: example\ndescription: test\n---\n", encoding="utf-8"
        )
        for name in ("GEMINI.md", "CLAUDE.md"):
            (self.root / name).write_text(
                "# Entry\n@./AGENTS.md\nRead `.harness/START-HERE.md`.\n", encoding="utf-8"
            )
        (self.root / "AI.md").write_text(
            "Read `AGENTS.md` and `.harness/START-HERE.md`.\n", encoding="utf-8"
        )

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_all_agents_static_ready_but_not_runtime_verified(self) -> None:
        report = check_project(self.root, "all")
        self.assertEqual(report["status"], "static_ready")
        self.assertFalse(report["runtime_loading_verified"])

    def test_missing_contract_blocks_entry(self) -> None:
        (self.root / "AGENTS.md").unlink()
        report = check_project(self.root, "codex")
        self.assertEqual(report["status"], "blocked")
        self.assertTrue(any(not item["passed"] for item in report["checks"]))

    def test_missing_skill_blocks_entry(self) -> None:
        (self.root / ".agents" / "skills" / "example" / "SKILL.md").unlink()
        self.assertEqual(check_project(self.root, "all")["status"], "blocked")

    def test_missing_adapter_import_blocks_only_relevant_agent(self) -> None:
        (self.root / "GEMINI.md").write_text(
            "Read AGENTS.md and `.harness/START-HERE.md`.\n", encoding="utf-8"
        )
        self.assertEqual(check_project(self.root, "gemini")["status"], "blocked")
        self.assertEqual(check_project(self.root, "claude")["status"], "static_ready")

    def test_router_missing_blocks_entry(self) -> None:
        (self.root / ".harness" / "START-HERE.md").unlink()
        self.assertEqual(check_project(self.root, "codex")["status"], "blocked")

    def test_repository_entries(self) -> None:
        # The repository itself should remain a valid Harness-enabled project.
        self.assertEqual(check_project(ROOT, "all")["status"], "static_ready")

    def test_invalid_skill_blocks_even_when_another_skill_is_valid(self) -> None:
        bad = self.root / ".agents/skills/bad/SKILL.md"
        bad.parent.mkdir()
        for content in (b"", b"\xff", b"garbage", b"---\nname: bad\ndescription: test\n",
                        b"---\nname: bad\ndescription: \n---\n",
                        b"---\nname: bad\nname: duplicate\ndescription: test\n---\n"):
            with self.subTest(content=content):
                bad.write_bytes(content)
                self.assertEqual(check_project(self.root)["status"], "blocked")

    def test_skill_must_be_a_file(self) -> None:
        path = self.root / ".agents/skills/example/SKILL.md"
        path.unlink()
        path.mkdir()
        self.assertEqual(check_project(self.root)["status"], "blocked")

    def test_wrong_relative_references_block(self) -> None:
        for path, content in (
            (".harness/START-HERE.md", "Read [contract](../../AGENTS.md)."),
            ("GEMINI.md", "@./AGENTS.md\nRead `missing/.harness/START-HERE.md`."),
            ("AI.md", "Read `wrong/AGENTS.md` and `.harness/START-HERE.md`."),
        ):
            with self.subTest(path=path):
                target = self.root / path
                original = target.read_bytes()
                target.write_text(content, encoding="utf-8")
                self.assertEqual(check_project(self.root)["status"], "blocked")
                target.write_bytes(original)

    def test_routed_context_must_be_readable_and_nonempty(self) -> None:
        router = self.root / ".harness/START-HERE.md"
        router.write_text("Read `../AGENTS.md` then [security](SECURITY.md).", encoding="utf-8")
        target = self.root / ".harness/SECURITY.md"
        self.assertEqual(check_project(self.root)["status"], "blocked")
        for content in (b"", b"\xff"):
            target.write_bytes(content)
            self.assertEqual(check_project(self.root)["status"], "blocked")
        target.write_text("# Security\nRules\n", encoding="utf-8")
        self.assertEqual(check_project(self.root)["status"], "static_ready")

    def test_import_inside_example_or_comment_is_not_active(self) -> None:
        for content in ("```text\n@./AGENTS.md\n```", "<!--\n@./AGENTS.md\n-->"):
            with self.subTest(content=content):
                (self.root / "CLAUDE.md").write_text(
                    content + "\nRead `.harness/START-HERE.md`.\n", encoding="utf-8")
                self.assertEqual(check_project(self.root, "claude")["status"], "blocked")

    def test_cli_broken_skill_returns_blocked_json_and_failure(self) -> None:
        (self.root / ".agents/skills/example/SKILL.md").write_bytes(b"\xff")
        process = subprocess.run(
            [sys.executable, str(ROOT / "scripts/check_agent_entry.py"),
             "--project", str(self.root), "--json"], capture_output=True, text=True)
        self.assertEqual(process.returncode, 1, process.stderr)
        self.assertEqual(json.loads(process.stdout)["status"], "blocked")

    def test_cli_reports_runtime_unverified(self) -> None:
        process = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "check_agent_entry.py"),
             "--project", str(self.root), "--agent", "all", "--json"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertIn('"runtime_loading_verified": false', process.stdout)


if __name__ == "__main__":
    unittest.main()
