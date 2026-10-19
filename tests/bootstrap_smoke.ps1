# Windows-only, isolated bootstrap smoke test. Never touches an existing user project.
$ErrorActionPreference = 'Stop'
$HarnessRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$Bootstrap = Join-Path $HarnessRoot 'scripts/bootstrap-project.ps1'
$Preflight = Join-Path $HarnessRoot 'scripts/check_agent_entry.py'
$Project = Join-Path ([IO.Path]::GetTempPath()) ('denys-harness-ci-' + [Guid]::NewGuid().ToString('N'))
$ProjectCreated = $false

try {
    New-Item -ItemType Directory -Path $Project | Out-Null
    $ProjectCreated = $true
    & $Bootstrap -ProjectPath $Project

    foreach ($Path in @('AGENTS.md','GEMINI.md','CLAUDE.md','AI.md','.harness/START-HERE.md','.agents/skills')) {
        if (-not (Test-Path (Join-Path $Project $Path))) {
            throw "Bootstrap missed $Path"
        }
    }

    & python $Preflight --project $Project --agent all
    if ($LASTEXITCODE -ne 0) { throw 'Static agent-entry preflight failed after bootstrap' }

    # A repeat bootstrap must preserve existing user content without -Force.
    $Gemini = Join-Path $Project 'GEMINI.md'
    Add-Content -Path $Gemini -Value '# existing user customization' -Encoding utf8
    $Before = Get-Content -Raw -Path $Gemini
    & $Bootstrap -ProjectPath $Project
    $After = Get-Content -Raw -Path $Gemini
    if ($Before -cne $After) { throw 'Repeat bootstrap overwrote existing content' }

    & python $Preflight --project $Project --agent all
    if ($LASTEXITCODE -ne 0) { throw 'Preflight failed after idempotent bootstrap' }
    Write-Host 'Bootstrap smoke passed (new project, all adapters, idempotent rerun).'
}
finally {
    # Exact disposable directory is created by this test; never clean a shared path.
    if ($ProjectCreated -and (Test-Path -LiteralPath $Project)) {
        $Owned = Get-Item -LiteralPath $Project -Force
        $TempRoot = (Get-Item -LiteralPath ([IO.Path]::GetTempPath())).FullName.TrimEnd('\', '/')
        if (($Owned.Attributes -band [IO.FileAttributes]::ReparsePoint) -or
            $Owned.Parent.FullName.TrimEnd('\', '/') -ne $TempRoot -or
            $Owned.Name -notmatch '^denys-harness-ci-[0-9a-f]{32}$') {
            throw 'Refusing cleanup: disposable directory identity changed.'
        }
        Remove-Item -LiteralPath $Project -Recurse -Force
    }
}
