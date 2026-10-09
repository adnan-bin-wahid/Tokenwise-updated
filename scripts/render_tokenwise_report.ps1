param(
    [string]$DocumentPath = 'Frineds_report/TokenWise_Final_Report_Updated.docx',
    [string]$PdfPath = 'tmp/report-review/TokenWise_Final_Report_Updated.pdf'
)

$ErrorActionPreference = 'Stop'
$documentFile = (Resolve-Path -LiteralPath $DocumentPath).Path
$pdfFile = [IO.Path]::GetFullPath((Join-Path (Get-Location) $PdfPath))
[IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($pdfFile)) | Out-Null
$word = $null
$document = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $word.AutomationSecurity = 3
    $document = $word.Documents.Open($documentFile, $false, $false, $false)
    $document.Repaginate()
    foreach ($contents in $document.TablesOfContents) {
        $contents.Update()
    }
    $document.Repaginate()
    $document.Save()
    $document.ExportAsFixedFormat($pdfFile, 17)
    Write-Output ('Rendered PDF: ' + $pdfFile)
    Write-Output ('Pages: ' + $document.ComputeStatistics(2))
} finally {
    if ($null -ne $document) {
        $document.Close(0)
        [Runtime.InteropServices.Marshal]::FinalReleaseComObject($document) | Out-Null
    }
    if ($null -ne $word) {
        $word.Quit()
        [Runtime.InteropServices.Marshal]::FinalReleaseComObject($word) | Out-Null
    }
}
