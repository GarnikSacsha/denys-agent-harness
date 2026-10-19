param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectPath,

    [switch]$Force
)

$ErrorActionPreference = "Stop"

function Assert-PlainPath([string]$Path) {
    $Item = Get-Item -LiteralPath $Path -Force
    while ($null -ne $Item) {
        if ($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
            throw "Bootstrap does not follow symlinks or junctions: $($Item.FullName)"
        }
        if ($Item -is [IO.DirectoryInfo]) { $Item = $Item.Parent }
        else { $Item = $Item.Directory }
    }
}

function Assert-PlainTree([string]$Path) {
    Assert-PlainPath $Path
    if (Test-Path -LiteralPath $Path -PathType Container) {
        foreach ($Item in Get-ChildItem -LiteralPath $Path -Force) {
            Assert-PlainTree $Item.FullName
        }
    }
}

Assert-PlainPath $PSScriptRoot
Assert-PlainPath $ProjectPath
$HarnessRoot = (Get-Item -LiteralPath (Split-Path -Parent $PSScriptRoot)).FullName
$ResolvedProject = (Get-Item -LiteralPath $ProjectPath).FullName
if (-not (Test-Path -LiteralPath $ResolvedProject -PathType Container)) {
    throw 'ProjectPath must be an existing filesystem directory.'
}

$SourcePrefix = $HarnessRoot.TrimEnd('\', '/') + [IO.Path]::DirectorySeparatorChar
$TargetPrefix = $ResolvedProject.TrimEnd('\', '/') + [IO.Path]::DirectorySeparatorChar
if ($SourcePrefix.StartsWith($TargetPrefix, [StringComparison]::OrdinalIgnoreCase) -or
    $TargetPrefix.StartsWith($SourcePrefix, [StringComparison]::OrdinalIgnoreCase)) {
    throw 'Harness source and project destination must not overlap.'
}

foreach ($Source in @('AGENTS.md', 'GEMINI.md', 'CLAUDE.md', 'AI.md',
        '.harness/START-HERE.md', '.harness/templates/AGENTS.project.template.md')) {
    if (-not (Test-Path -LiteralPath (Join-Path $HarnessRoot $Source) -PathType Leaf)) {
        throw "Missing bootstrap source: $Source"
    }
}
foreach ($Source in @('.harness', '.agents/skills')) {
    if (-not (Test-Path -LiteralPath (Join-Path $HarnessRoot $Source) -PathType Container)) {
        throw "Missing bootstrap directory: $Source"
    }
}
foreach ($ManagedPath in @('AGENTS.md', 'GEMINI.md', 'CLAUDE.md', 'AI.md', '.harness', '.agents')) {
    Assert-PlainTree (Join-Path $HarnessRoot $ManagedPath)
    $Destination = Join-Path $ResolvedProject $ManagedPath
    if (Get-Item -LiteralPath $Destination -Force -ErrorAction SilentlyContinue) {
        Assert-PlainTree $Destination
    }
}

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
if ((Test-Path -LiteralPath $ProjectAgents) -and -not $Force) {
    Write-Host "Skipped existing file: $ProjectAgents"
}
else {
    $BaseContract = Get-Content -Raw -LiteralPath (Join-Path $HarnessRoot "AGENTS.md") -Encoding UTF8
    $ProjectTemplate = Get-Content -Raw -LiteralPath (Join-Path $HarnessRoot ".harness\templates\AGENTS.project.template.md") -Encoding UTF8
    $Combined = $BaseContract + "`r`n`r`n---`r`n`r`n" + $ProjectTemplate
    Set-Content -LiteralPath $ProjectAgents -Value $Combined -Encoding utf8
    Write-Host "Created: $ProjectAgents"
}

foreach ($Copy in $Copies) {
    if ((Test-Path -LiteralPath $Copy.Destination) -and -not $Force) {
        Write-Host "Skipped existing file: $($Copy.Destination)"
        continue
    }

    Copy-Item -LiteralPath $Copy.Source -Destination $Copy.Destination -Force:$Force
    Write-Host "Created: $($Copy.Destination)"
}

$HarnessContextDestination = Join-Path $ResolvedProject ".harness"
if ((Test-Path -LiteralPath $HarnessContextDestination) -and -not $Force) {
    Write-Host "Skipped existing directory: $HarnessContextDestination"
}
else {
    Copy-Item -LiteralPath (Join-Path $HarnessRoot ".harness") -Destination $ResolvedProject -Recurse -Force:$Force
    Write-Host "Created: $HarnessContextDestination"
}

$SkillsDestination = Join-Path $ResolvedProject ".agents\skills"
if ((Test-Path -LiteralPath $SkillsDestination) -and -not $Force) {
    Write-Host "Skipped existing directory: $SkillsDestination"
}
else {
    New-Item -ItemType Directory -Path (Join-Path $ResolvedProject ".agents") -Force | Out-Null
    Copy-Item -LiteralPath (Join-Path $HarnessRoot ".agents\skills") -Destination (Join-Path $ResolvedProject ".agents") -Recurse -Force:$Force
    Write-Host "Created: $SkillsDestination"
}

Write-Host "Bootstrap complete. Fill the placeholders in AGENTS.md before implementation."
