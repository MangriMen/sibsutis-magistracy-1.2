param (
    [string]$inputFolder = ".\images"  # Папка по умолчанию
)

# Проверяем существование папки
if (-not (Test-Path $inputFolder -PathType Container)) {
    # Write-Error "Папка '$inputFolder' не найдена!"
    exit 1
}

# Обрабатываем все файлы в указанной папке
Get-ChildItem -Path "$inputFolder\*" | ForEach-Object {
    # Write-Host "Обработка файла: $($_.FullName)"
    java -jar RSAnalysis.jar $_.FullName
}

# Write-Host "Обработка завершена!"