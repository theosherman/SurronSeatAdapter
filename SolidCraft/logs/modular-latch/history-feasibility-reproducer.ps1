# Throwaway feasibility test. Writes only an isolated native copy.
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression.FileSystem
Add-Type -AssemblyName System.IO.Compression
$projectRoot = 'C:/Projects/Sherman P Seat Adapter'
$inputPath = Join-Path $projectRoot 'SolidCraft/models/seat-adapter.sc'
$outputPath = Join-Path $projectRoot 'SolidCraft/models/experiments/modular-history-spike-v3.sc'
if (Test-Path -LiteralPath $outputPath) { throw 'Spike destination exists; preserve it before another trial' }
Copy-Item -LiteralPath $inputPath -Destination $outputPath
$archive = [IO.Compression.ZipFile]::Open($outputPath,[IO.Compression.ZipArchiveMode]::Update)
try {
  $entry = $archive.GetEntry('document.json')
  $reader = [IO.StreamReader]::new($entry.Open())
  $document = $reader.ReadToEnd() | ConvertFrom-Json
  $reader.Dispose()
  $master = @($document.components | Where-Object name -eq 'AdapterBody')
  if ($master.Count -ne 1) { throw 'Expected one AdapterBody component' }
  $placements = @($document.occurrences | Where-Object component -eq $master[0].id)
  if ($placements.Count -ne 1) { throw 'Expected exactly one master placement' }
  for ($row = 0; $row -lt 4; $row++) {
    for ($column = 0; $column -lt 4; $column++) {
      $expected = 0; if ($row -eq $column) { $expected = 1 }
      if ([Math]::Abs($placements[0].transform[$row][$column] - $expected) -gt 1e-12) { throw 'Nonidentity master placement requires an explicit coordinate migration' }
    }
  }
  $features = @($document.features | Where-Object component -eq $master[0].id)
  foreach ($feature in $features) { $feature.component = 0 }
  $document.features = $features
  $document.components = @()
  $document.occurrences = @()
  $document.name = 'Adapter Body'
  $document.visibility.hidden_occurrences = @()
  $entry.Delete()
  $writer = [IO.StreamWriter]::new($archive.CreateEntry('document.json').Open(),[Text.UTF8Encoding]::new($false))
  $writer.Write((ConvertTo-Json -Depth 100 -Compress -InputObject $document))
  $writer.Dispose()
  foreach ($cached in @($archive.Entries | Where-Object FullName -like 'cache/*')) { $cached.Delete() }
  Write-Output ('Native master feature count: ' + $features.Count)
} finally { $archive.Dispose() }
