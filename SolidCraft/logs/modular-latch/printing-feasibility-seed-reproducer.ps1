# Throwaway assembly seed; original master/printing definitions stay in recovery.
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression.FileSystem
Add-Type -AssemblyName System.IO.Compression
$projectRoot = 'C:/Projects/Sherman P Seat Adapter'
$outputPath = Join-Path $projectRoot 'SolidCraft/models/experiments/modular-assembly-seed.sc'
if (Test-Path -LiteralPath $outputPath) { throw 'Spike destination already exists' }
Copy-Item -LiteralPath (Join-Path $projectRoot 'SolidCraft/models/seat-adapter.sc') -Destination $outputPath
$archive = [IO.Compression.ZipFile]::Open($outputPath,[IO.Compression.ZipArchiveMode]::Update)
try {
  $entry = $archive.GetEntry('document.json')
  $reader = [IO.StreamReader]::new($entry.Open())
  $document = $reader.ReadToEnd() | ConvertFrom-Json
  $reader.Dispose()
  $document.features = @()
  $document.components = @($document.components | Where-Object name -ne 'AdapterBody')
  $document.occurrences = @($document.occurrences | Where-Object component -ne 74)
  $document.name = 'SeatAdapter'
  $document.visibility.hidden_occurrences = @()
  $entry.Delete()
  $writer = [IO.StreamWriter]::new($archive.CreateEntry('document.json').Open(),[Text.UTF8Encoding]::new($false))
  $writer.Write((ConvertTo-Json -Depth 100 -Compress -InputObject $document))
  $writer.Dispose()
  foreach ($cached in @($archive.Entries | Where-Object FullName -like 'cache/*')) { $cached.Delete() }
} finally { $archive.Dispose() }
