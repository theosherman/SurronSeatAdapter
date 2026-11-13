param(
  [Parameter(Mandatory=$true)][ValidateSet('Read','Write')][string]$Mode,
  [Parameter(Mandatory=$true)][string]$InputPath,
  [Parameter(Mandatory=$true)][string]$DocumentPath,
  [string]$OutputPath,
  [string]$ExpectedSha256
)
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.IO.Compression.FileSystem
Add-Type -AssemblyName System.IO.Compression
$source=[IO.Path]::GetFullPath($InputPath)
if ((Get-Item -LiteralPath $source).Length -gt 268435456) { throw 'Native input exceeds 256 MB bound' }
function Get-AssetInventory($archive) {
  $assets=@()
  foreach($entry in $archive.Entries) {
    if ($entry.FullName.StartsWith('blobs/')) {
      $stream=$entry.Open(); $hasher=[Security.Cryptography.SHA256]::Create()
      try { $digest=[BitConverter]::ToString($hasher.ComputeHash($stream)).Replace('-','').ToLowerInvariant() }
      finally { $stream.Dispose();$hasher.Dispose() }
      $assets+=@{name=$entry.FullName;bytes=$entry.Length;sha256=$digest}
    }
  }
  return @($assets | Sort-Object { $_.name })
}
if ($Mode -eq 'Read') {
  $archive=[IO.Compression.ZipFile]::OpenRead($source)
  try {
    $entry=$archive.GetEntry('document.json')
    if (!$entry -or $entry.Length -gt 16777216) { throw 'Missing or oversized native document' }
    $stream=$entry.Open();$destination=[IO.File]::Open([IO.Path]::GetFullPath($DocumentPath),[IO.FileMode]::CreateNew,[IO.FileAccess]::Write)
    try {$stream.CopyTo($destination)} finally {$stream.Dispose();$destination.Dispose()}
    @{assets=@(Get-AssetInventory $archive);cacheEntries=@($archive.Entries|Where-Object {$_.FullName.StartsWith('cache/')}).Count} | ConvertTo-Json -Depth 8 -Compress
  } finally {$archive.Dispose()}
} else {
  if (!$ExpectedSha256) {throw 'Expected source hash is required'}
  $actual=(Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLowerInvariant()
  if ($actual -ne $ExpectedSha256.ToLowerInvariant()) {throw 'Source changed since capture'}
  $target=[IO.Path]::GetFullPath($OutputPath)
  if ($target -eq $source -or (Test-Path -LiteralPath $target)) {throw 'Output exists or would overwrite source'}
  $document=[IO.Path]::GetFullPath($DocumentPath)
  if ((Get-Item -LiteralPath $document).Length -gt 16777216) {throw 'Document exceeds 16 MB bound'}
  Copy-Item -LiteralPath $source -Destination $target
  $archive=[IO.Compression.ZipFile]::Open($target,[IO.Compression.ZipArchiveMode]::Update)
  try {
    $archive.GetEntry('document.json').Delete()
    $entry=$archive.CreateEntry('document.json');$stream=$entry.Open();$inputStream=[IO.File]::OpenRead($document)
    try {$inputStream.CopyTo($stream)} finally {$stream.Dispose();$inputStream.Dispose()}
    foreach($cached in @($archive.Entries|Where-Object {$_.FullName.StartsWith('cache/')})) {$cached.Delete()}
  } finally {$archive.Dispose()}
  @{ok=$true;path=$target}|ConvertTo-Json -Compress
}
