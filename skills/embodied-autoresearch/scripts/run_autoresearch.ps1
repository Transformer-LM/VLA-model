#Requires -Version 5.1
<#
.SYNOPSIS
    Start or resume the embodied-autoresearch workflow in unattended Codex runs.

.DESCRIPTION
    This is an external terminal supervisor. It never enables approval or
    sandbox bypasses. It stops when state is complete, blocked, failed without
    recovery, or unchanged across two Codex invocations.
#>

[CmdletBinding()]
param(
    [string]$ProjectRoot = (Get-Location).Path,
    [string]$Direction = 'VLA and World Action Models for long-horizon robot manipulation',
    [switch]$Resume,
    [switch]$DryRun,
    [ValidateRange(1, 12)]
    [int]$MaxAgentRuns = 3,
    [string]$Model = ''
)

$ErrorActionPreference = 'Stop'
$ProjectRoot = [System.IO.Path]::GetFullPath($ProjectRoot).TrimEnd('\')
if (-not (Test-Path -LiteralPath $ProjectRoot -PathType Container)) {
    throw "Project root does not exist: $ProjectRoot"
}

$SkillRoot = Split-Path -Parent $PSScriptRoot
$Bootstrap = Join-Path $PSScriptRoot 'bootstrap.py'
$StateScript = Join-Path $PSScriptRoot 'research_state.py'
foreach ($required in @($Bootstrap, $StateScript)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
        throw "Required script is missing: $required"
    }
}

$ProjectPython = Join-Path $ProjectRoot '.agents\runtime\research-skills\python-utf8.cmd'
if (Test-Path -LiteralPath $ProjectPython -PathType Leaf) {
    $PythonCommand = $ProjectPython
} else {
    $Python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $Python) {
        $Python = Get-Command python3 -ErrorAction SilentlyContinue
    }
    if (-not $Python) {
        throw 'Python was not found.'
    }
    $PythonCommand = $Python.Source
}

$Codex = Get-Command codex -ErrorAction SilentlyContinue
if (-not $Codex -and -not $DryRun) {
    throw 'Codex CLI was not found.'
}

function Invoke-ResearchPython {
    param([string]$Script, [string[]]$Arguments)
    $output = & $PythonCommand $Script @Arguments 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw ($output -join [Environment]::NewLine)
    }
    return ($output -join [Environment]::NewLine)
}

$BootstrapArguments = @('--root', $ProjectRoot, '--direction', $Direction)
if ($Resume) {
    # Bootstrap naturally reuses an active run; the switch documents intent.
}
if ($DryRun) {
    $BootstrapArguments += '--dry-run'
    Invoke-ResearchPython -Script $Bootstrap -Arguments $BootstrapArguments
    exit 0
}

Invoke-ResearchPython -Script $Bootstrap -Arguments $BootstrapArguments | Write-Host

$SupervisorDir = Join-Path $ProjectRoot '.aris\autoresearch\supervisor'
New-Item -ItemType Directory -Force -Path $SupervisorDir | Out-Null
$NoProgressCount = 0

for ($iteration = 1; $iteration -le $MaxAgentRuns; $iteration++) {
    $BeforeRaw = Invoke-ResearchPython -Script $StateScript -Arguments @('--root', $ProjectRoot, 'status', '--json')
    $Before = $BeforeRaw | ConvertFrom-Json
    if ($Before.overall_status -eq 'completed') {
        Write-Host "AutoResearch is complete: $($Before.run_id)"
        exit 0
    }
    if ($Before.overall_status -eq 'blocked') {
        Write-Host "AutoResearch is blocked: $($Before.action | ConvertTo-Json -Compress)"
        exit 2
    }

    $OutputPath = Join-Path $SupervisorDir ("codex-run-{0:D2}.txt" -f $iteration)
    $Prompt = @'
Use $embodied-autoresearch to resume the active run in this project. Continue
through as many sequential phases as the available evidence, resources, and
authority permit. Read every dependency skill before using it, update the
deterministic run state before and after each phase, preserve raw evidence and
negative results, and stop after recording any genuine blocker. Do not invoke
the external supervisor recursively. Do not write a paper.
'@
    $CodexArguments = @(
        'exec',
        '-C', $ProjectRoot,
        '--sandbox', 'workspace-write',
        '--skip-git-repo-check',
        '--output-last-message', $OutputPath
    )
    if (-not [string]::IsNullOrWhiteSpace($Model)) {
        $CodexArguments += @('--model', $Model)
    }
    $CodexArguments += $Prompt

    Write-Host "Starting Codex AutoResearch pass $iteration/$MaxAgentRuns..."
    & $Codex.Source @CodexArguments
    $CodexExit = $LASTEXITCODE

    $AfterRaw = Invoke-ResearchPython -Script $StateScript -Arguments @('--root', $ProjectRoot, 'status', '--json')
    $After = $AfterRaw | ConvertFrom-Json
    if ($After.overall_status -eq 'completed') {
        Write-Host "AutoResearch is complete: $($After.run_id)"
        exit 0
    }
    if ($After.overall_status -eq 'blocked') {
        Write-Host "AutoResearch recorded a blocker: $($After.action | ConvertTo-Json -Compress)"
        exit 2
    }

    $BeforeHistory = @($Before.history).Count
    $AfterHistory = @($After.history).Count
    if ($After.updated_at -eq $Before.updated_at -and $AfterHistory -le $BeforeHistory) {
        $NoProgressCount++
    } else {
        $NoProgressCount = 0
    }
    if ($NoProgressCount -ge 2) {
        Write-Warning 'Stopping after two Codex passes with no state progress.'
        exit 3
    }
    if ($CodexExit -ne 0) {
        Write-Warning "Codex exited with code $CodexExit; state progressed, so one bounded resume is allowed."
    }
}

Write-Warning "AutoResearch remains active after $MaxAgentRuns Codex passes. Resume with this script after inspecting state."
exit 3

