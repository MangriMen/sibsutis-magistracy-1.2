param (
    [Parameter(Mandatory=$true)]
    [string]$InputFolder,

    [Parameter(Mandatory=$true)]
    [string]$OutputFolder,

    [Parameter(Mandatory=$true)]
    [string]$MessageFile
)

if (!(Test-Path $OutputFolder)) {
    New-Item -ItemType Directory -Path $OutputFolder | Out-Null
}

Get-ChildItem -Path $InputFolder -Filter *.bmp | ForEach-Object {
    $inputPath = $_.FullName
    $outputPath = Join-Path $OutputFolder ($_.BaseName + "_encoded.bmp")

    Write-Host "Processing: $($_.Name)"
    .\lab1.exe encode -m $MessageFile -i $inputPath -o $outputPath
}
