"""Keep external CI execution pinned to immutable revisions."""

from pathlib import Path
import re
import unittest


class TestCIContract(unittest.TestCase):
    def test_actions_use_full_commit_ids(self) -> None:
        workflow = Path(__file__).resolve().parents[1] / ".github/workflows/harness-ci.yml"
        actions = re.findall(r"(?m)^\s*uses:\s*(\S+)", workflow.read_text(encoding="utf-8"))
        self.assertTrue(actions)
        for action in actions:
            with self.subTest(action=action):
                self.assertRegex(action, r"^[\w.-]+/[\w./-]+@[0-9a-f]{40}$")
