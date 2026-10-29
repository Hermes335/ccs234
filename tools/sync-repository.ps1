[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Repository,
    [Parameter(Mandatory = $true)][string]$ExpectedRemote,
    [string]$Branch = 'main',
    [string]$GitPath = 'git'
)

# Download updates only. Never push, reset, stash, clean, install, or run project code.
$ErrorActionPreference = 'Stop'
$env:GIT_TERMINAL_PROMPT = '0'
$env:GCM_INTERACTIVE = 'Never'
$env:GIT_OPTIONAL_LOCKS = '0'
$repoPath = (Resolve-Path -LiteralPath $Repository).Path
$syncDirectory = Join-Path $repoPath '.sync'
New-Item -ItemType Directory -Path $syncDirectory -Force | Out-Null
$logFile = Join-Path $syncDirectory 'auto-update.log'
$lockFile = Join-Path $syncDirectory 'auto-update.lock'
$repoLock = $null

function Write-SyncLog([string]$Message) {
    Add-Content -LiteralPath $logFile -Encoding UTF8 -Value ((Get-Date -Format 'yyyy-MM-ddTHH:mm:sszzz') + ' ' + $Message)
}

function Invoke-RepoGit([string[]]$Arguments) {
    # Windows PowerShell may turn native stderr into terminating errors; capture
    # it and use Git's actual exit code instead.
    $oldPreference = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $output = & $GitPath -c credential.interactive=false -c http.lowSpeedLimit=1024 -c http.lowSpeedTime=20 -C $repoPath @Arguments 2>&1
        $gitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $oldPreference
    }
    if ($gitCode -ne 0) {
        throw ('Git operation failed with exit code ' + $gitCode + ': ' + ($output -join ' '))
    }
    return ($output -join "`n").Trim()
}

try {
    try {
        $repoLock = [System.IO.File]::Open($lockFile, [System.IO.FileMode]::OpenOrCreate, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
    } catch [System.IO.IOException] {
        exit 0 # Another sync is already running.
    }
    if ((Test-Path -LiteralPath $logFile) -and (Get-Item -LiteralPath $logFile).Length -gt 524288) {
        Move-Item -LiteralPath $logFile -Destination (Join-Path $syncDirectory 'auto-update.previous.log') -Force
    }
    $remote = Invoke-RepoGit -Arguments @('remote', 'get-url', 'origin')
    if ($remote -ne $ExpectedRemote) {
        Write-SyncLog 'SKIPPED: origin differs from the configured repository.'
        exit 0
    }
    $currentBranch = Invoke-RepoGit -Arguments @('symbolic-ref', '--quiet', '--short', 'HEAD')
    if ($currentBranch -ne $Branch) {
        Write-SyncLog 'SKIPPED: a different branch is checked out.'
        exit 0
    }
    $dirty = Invoke-RepoGit -Arguments @('status', '--porcelain', '--untracked-files=normal')
    if ($dirty) {
        Write-SyncLog 'SKIPPED: local edits or untracked files exist. Commit or resolve them manually.'
        exit 0
    }
    Invoke-RepoGit -Arguments @('fetch', '--no-tags', 'origin', $Branch) | Out-Null
    # Recheck after fetch in case an editor changed files while the network ran.
    if (Invoke-RepoGit -Arguments @('status', '--porcelain', '--untracked-files=normal')) {
        Write-SyncLog 'SKIPPED: files changed during fetch.'
        exit 0
    }
    $before = Invoke-RepoGit -Arguments @('rev-parse', 'HEAD')
    $remoteHead = Invoke-RepoGit -Arguments @('rev-parse', ('refs/remotes/origin/' + $Branch))
    if ($before -eq $remoteHead) {
        Write-SyncLog ('CURRENT: ' + $before.Substring(0, 12))
        exit 0
    }
    # --ff-only refuses to merge divergent history and never rewrites local work.
    Invoke-RepoGit -Arguments @('merge', '--ff-only', ('refs/remotes/origin/' + $Branch)) | Out-Null
    $after = Invoke-RepoGit -Arguments @('rev-parse', 'HEAD')
    if ($after -eq $before) {
        Write-SyncLog 'SKIPPED: local branch is ahead. Local commits are never pushed automatically.'
    } else {
        Write-SyncLog ('UPDATED: ' + $before.Substring(0, 12) + ' -> ' + $after.Substring(0, 12))
    }
} catch {
    Write-SyncLog ('ERROR: ' + $_.Exception.Message)
    exit 1
} finally {
    if ($repoLock) { $repoLock.Dispose() }
}
