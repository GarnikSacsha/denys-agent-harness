param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectPath,

    [switch]$Force
)

$ErrorActionPreference = "Stop"
$HarnessRoot = Split-Path -Parent $PSScriptRoot
$ResolvedProject = Resolve-Path -Path $ProjectPath

$Copies = @(
    @{
        Source = Join-Path $HarnessRoot "GEMINI.md"
        Destination = Join-Path $ResolvedProject "GEMINI.md"
    },
    @{
        Source = Join-Path $HarnessRoot "CLAUDE.md"
        Destination = Join-Path $ResolvedProject "CLAUDE.md"
    },
    @{
        Source = Join-Path $HarnessRoot "AI.md"
        Destination = Join-Path $ResolvedProject "AI.md"
    }
)

$ProjectAgents = Join-Path $ResolvedProject "AGENTS.md"
if ((Test-Path $ProjectAgents) -and -not $Force) {
    Write-Host "Skipped existing file: $ProjectAgents"
}
else {
    $BaseContract = Get-Content -Raw -Path (Join-Path $HarnessRoot "AGENTS.md")
    $ProjectTemplate = Get-Content -Raw -Path (Join-Path $HarnessRoot ".harness\templates\AGENTS.project.template.md")
    $Combined = $BaseContract + "`r`n`r`n---`r`n`r`n" + $ProjectTemplate
    Set-Content -Path $ProjectAgents -Value $Combined -Encoding utf8
    Write-Host "Created: $ProjectAgents"
}

foreach ($Copy in $Copies) {
    if ((Test-Path $Copy.Destination) -and -not $Force) {
        Write-Host "Skipped existing file: $($Copy.Destination)"
        continue
    }

    Copy-Item -Path $Copy.Source -Destination $Copy.Destination -Force:$Force
    Write-Host "Created: $($Copy.Destination)"
}

$HarnessContextDestination = Join-Path $ResolvedProject ".harness"
if ((Test-Path $HarnessContextDestination) -and -not $Force) {
    Write-Host "Skipped existing directory: $HarnessContextDestination"
}
else {
    Copy-Item -Path (Join-Path $HarnessRoot ".harness") -Destination $ResolvedProject -Recurse -Force:$Force
    Write-Host "Created: $HarnessContextDestination"
}

$SkillsDestination = Join-Path $ResolvedProject ".agents\skills"
if ((Test-Path $SkillsDestination) -and -not $Force) {
    Write-Host "Skipped existing directory: $SkillsDestination"
}
else {
    New-Item -ItemType Directory -Path (Join-Path $ResolvedProject ".agents") -Force | Out-Null
    Copy-Item -Path (Join-Path $HarnessRoot ".agents\skills") -Destination (Join-Path $ResolvedProject ".agents") -Recurse -Force:$Force
    Write-Host "Created: $SkillsDestination"
}

Write-Host "Bootstrap complete. Fill the placeholders in AGENTS.md before implementation."
