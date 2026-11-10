"""Exercise the real bootstrap in disposable directories on Windows."""

from pathlib import Path
import shutil
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(sys.platform == "win32", "Windows bootstrap")
class TestBootstrap(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="harness-bootstrap-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "source"
        self.source.mkdir()
        for name in ("AGENTS.md", "GEMINI.md", "CLAUDE.md", "AI.md"):
            shutil.copy2(ROOT / name, self.source / name)
        for name in (".harness", ".agents", "scripts"):
            shutil.copytree(ROOT / name, self.source / name,
                            ignore=shutil.ignore_patterns("__pycache__"))
        self.shells = [path for name in ("powershell", "pwsh") if (path := shutil.which(name))]
        self.assertTrue(self.shells, "No supported PowerShell interpreter available")

    def run_bootstrap(self, shell: str, target: Path, force: bool = False) -> subprocess.CompletedProcess:
        return subprocess.run(
            [shell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
             str(self.source / "scripts/bootstrap-project.ps1"), "-ProjectPath", str(target)]
            + (["-Force"] if force else []), capture_output=True, timeout=30)

    def snapshot(self) -> dict:
        return {str(p.relative_to(self.root)): p.read_bytes()
                for p in self.root.rglob("*") if p.is_file()}

    def test_unicode_and_repeat_preserve_all_files(self) -> None:
        for index, shell in enumerate(self.shells):
            with self.subTest(shell=shell):
                target = self.root / f"project space \u0423\u043a\u0440\u0430\u0457\u043d\u0430 {index}"
                target.mkdir()
                result = self.run_bootstrap(shell, target)
                self.assertEqual(result.returncode, 0, result.stderr)
                contract = (self.source / "AGENTS.md").read_text(encoding="utf-8")
                self.assertTrue((target / "AGENTS.md").read_text(encoding="utf-8-sig").startswith(contract))
                for path in target.rglob("*.md"):
                    with path.open("ab") as stream:
                        stream.write(b"\n# user customization\n")
                before = self.snapshot()
                result = self.run_bootstrap(shell, target)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(self.snapshot(), before)

    def test_overlapping_paths_fail_before_any_write(self) -> None:
        child = self.source / "child"
        child.mkdir()
        for shell in self.shells:
            for target in (self.source, child, self.root):
                with self.subTest(shell=shell, target=target):
                    before = self.snapshot()
                    result = self.run_bootstrap(shell, target, force=True)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertEqual(self.snapshot(), before)

    def test_missing_source_fails_before_any_write(self) -> None:
        (self.source / "CLAUDE.md").unlink()
        target = self.root / "project"
        target.mkdir()
        before = self.snapshot()
        result = self.run_bootstrap(self.shells[0], target)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.snapshot(), before)

    def test_literal_brackets_in_project_path(self) -> None:
        target = self.root / "project [literal]"
        target.mkdir()
        result = self.run_bootstrap(self.shells[0], target)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((target / "AGENTS.md").is_file())

    def test_force_refreshes_managed_files_and_preserves_unrelated_content(self) -> None:
        target = self.root / "project"
        target.mkdir()
        result = self.run_bootstrap(self.shells[0], target)
        self.assertEqual(result.returncode, 0, result.stderr)
        (target / "GEMINI.md").write_text("custom", encoding="utf-8")
        unrelated = target / ".harness/user-note.txt"
        unrelated.write_bytes(b"keep")
        result = self.run_bootstrap(self.shells[0], target, force=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((target / "GEMINI.md").read_bytes(), (self.source / "GEMINI.md").read_bytes())
        self.assertEqual(unrelated.read_bytes(), b"keep")
        self.assertFalse((target / ".harness/.harness").exists())
        self.assertFalse((target / ".agents/skills/skills").exists())

    def test_smoke_does_not_clean_directory_it_failed_to_create(self) -> None:
        env = os.environ.copy()
        env["TEMP"] = env["TMP"] = str(self.root)
        smoke = str(ROOT / "tests/bootstrap_smoke.ps1").replace("'", "''")
        command = """
function New-Item {
    param($ItemType, $Path)
    $global:Collision = $Path
    [IO.Directory]::CreateDirectory($Path) | Out-Null
    [IO.File]::WriteAllText((Join-Path $Path 'sentinel'), 'keep')
    throw 'Simulated collision: caller does not own this directory'
}
try { & 'SMOKE_PATH' } catch { }
if (-not $global:Collision) { exit 2 }
if (-not (Test-Path -LiteralPath (Join-Path $global:Collision 'sentinel'))) { exit 3 }
""".replace("SMOKE_PATH", smoke)
        result = subprocess.run([self.shells[0], "-NoProfile", "-Command", command],
                                env=env, capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_junction_alias_cannot_bypass_overlap_guard(self) -> None:
        alias = self.root / "alias"
        command = "New-Item -ItemType Junction -Path '{}' -Target '{}' | Out-Null".format(
            str(alias).replace("'", "''"), str(self.source).replace("'", "''"))
        result = subprocess.run([self.shells[0], "-NoProfile", "-Command", command],
                                capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.addCleanup(alias.rmdir)
        contract = (self.source / "AGENTS.md").read_bytes()
        result = self.run_bootstrap(self.shells[0], alias, force=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((self.source / "AGENTS.md").read_bytes(), contract)
