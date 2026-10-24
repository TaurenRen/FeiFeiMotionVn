# Apply the Windows fixes to a huashu-motion checkout.
#
#   powershell -ExecutionPolicy Bypass -File apply.ps1 -Repo C:\path\to\huashu-motion
#
# Two routes, in order:
#   1. git apply  - keeps any local work, fails cleanly if the context moved
#   2. copy       - drops in the five finished files from files\ (use when upstream changed under us;
#                   it overwrites those five files only, and backs each one up as *.orig first)
# Then it proves the patch worked: `om new` must produce more than index.html.

param(
  [Parameter(Mandatory = $true)][string]$Repo,
  [switch]$ForceCopy
)

$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoPath = (Resolve-Path $Repo).Path
$om = Join-Path $repoPath 'cli\om.js'

if (-not (Test-Path $om)) { throw "no cli\om.js under $repoPath — is that a huashu-motion checkout?" }

$files = @(
  'cli\om.js',
  'cli\lib\fsx.js',
  'cli\lib\fork.js',
  'cli\lib\voice.js',
  'cli\lib\samples-build.js'
)

$applied = $false
if (-not $ForceCopy) {
  Push-Location $repoPath
  try {
    git apply --3way (Join-Path $here '0001-windows.patch') 2>$null
    if ($LASTEXITCODE -eq 0) { $applied = $true; Write-Host 'patched with git apply' }
    else { Write-Host 'git apply did not take (context moved?) — falling back to copying the finished files' }
  } catch {
    Write-Host 'git apply unavailable — falling back to copying the finished files'
  } finally { Pop-Location }
}

if (-not $applied) {
  foreach ($f in $files) {
    $src = Join-Path $here (Join-Path 'files' $f)
    $dst = Join-Path $repoPath $f
    if (-not (Test-Path $src)) { throw "missing $src — the files\ payload is incomplete" }
    $dir = Split-Path -Parent $dst
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    if ((Test-Path $dst) -and -not (Test-Path "$dst.orig")) { Copy-Item $dst "$dst.orig" }
    Copy-Item $src $dst -Force
    Write-Host "copied $f"
  }
}

Write-Host ''
Write-Host '== verifying =='
$node = if ($env:OM_NODE) { $env:OM_NODE } else { 'node' }
& $node $om doctor

$tmp = Join-Path $env:TEMP ("om-patchcheck-" + [guid]::NewGuid().ToString('N').Substring(0, 8))
try {
  & $node $om new $tmp --template kinetic-type | Out-Null
  $count = (Get-ChildItem -Path $tmp -Recurse -File).Count
  if ($count -le 1) {
    throw "om new produced $count file(s) — the fs.cpSync fix is NOT in effect (expected ~33)"
  }
  Write-Host "om new -> $count files  OK"
  $check = & $node $om check $tmp 2>&1 | Out-String
  if ($check -match '(\d+) errors' -and [int]$Matches[1] -gt 0) {
    Write-Warning "om check still reports $($Matches[1]) error(s) on a fresh template:"
    Write-Host $check
  } else { Write-Host 'om check -> 0 errors  OK' }
}
finally {
  if (Test-Path $tmp) { Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue }
}

Write-Host ''
Write-Host 'done. next: node cli/om.js new my-film --template keynote-ui ; node cli/om.js studio my-film'
