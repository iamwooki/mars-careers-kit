param(
    [Parameter(Mandatory=$true)][string]$HtmlPath,
    [Parameter(Mandatory=$true)][string]$PdfPath
)
# HTML -> PDF via Edge headless (Windows 기본 탑재, 별도 설치 불필요)
$ErrorActionPreference = "Stop"

$edgeCandidates = @(
    "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "C:\Program Files\Microsoft\Edge\Application\msedge.exe"
)
$edge = $edgeCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $edge) { throw "msedge.exe를 찾을 수 없습니다. Chrome 경로로 대체하세요." }

$htmlFull = (Resolve-Path $HtmlPath).Path
$pdfFull  = [System.IO.Path]::GetFullPath($PdfPath)
$fileUrl  = "file:///" + ($htmlFull -replace '\\', '/')

& $edge --headless=new --disable-gpu --no-pdf-header-footer --no-first-run `
    --print-to-pdf="$pdfFull" $fileUrl | Out-Null

if (-not (Test-Path $pdfFull)) { throw "PDF 생성 실패: $pdfFull" }
Write-Output "OK: $pdfFull ($([math]::Round((Get-Item $pdfFull).Length/1KB)) KB)"
