param([string]$videoUrl)

if (-not $videoUrl) {
    $videoUrl = Read-Host "Enter video URL"
}

try {
    $formats = yt-dlp -J --skip-download $videoUrl | ConvertFrom-Json | Select-Object -ExpandProperty formats | ForEach-Object { "$($_.format_id) - $($_.resolution)" }

    if (-not $formats) {
        Write-Host "No video formats found."
        exit 1
    }

    $selectedFormat = $formats | Out-GridView -Title 'Select a format' -OutputMode Single

    if (-not $selectedFormat) {
        Write-Host "No format selected."
        exit 1
    }

    $formatId = ($selectedFormat -split ' - ')[0]
    $extension = (yt-dlp -J --skip-download $videoUrl | ConvertFrom-Json).formats | Where-Object { $_.format_id -eq $formatId } | Select-Object -ExpandProperty ext
    $title = [guid]::NewGuid().ToString()
    $downloadUrl = yt-dlp -g $videoUrl --format $formatId

    if ($downloadUrl) {
        yt-dlp -o "$title.$extension" $downloadUrl
    } else {
        Write-Host "Error: Failed to retrieve download URL for the selected format."
        exit 1
    }
}
catch {
    Write-Host "An error occurred: $_"
    exit 1
}
