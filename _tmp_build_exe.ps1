$ErrorActionPreference = "Stop"

$PythonExe = "C:\Users\victor\anaconda3\envs\pytorch\python.exe"
if (-not (Test-Path $PythonExe)) {
    $PythonExe = "python"
}

& $PythonExe -m PyInstaller --clean --noconfirm FormulaOCR.spec

$SourceDir = Join-Path $PSScriptRoot "dist\FormulaOCR"
$ReleaseDir = Join-Path $PSScriptRoot "dist\公式识别"
$SourceExe = Join-Path $SourceDir "FormulaOCR.exe"
$ReleaseExe = Join-Path $ReleaseDir "公式识别.exe"

if (Test-Path $ReleaseDir) {
    Remove-Item -LiteralPath $ReleaseDir -Recurse -Force
}

Copy-Item -LiteralPath $SourceDir -Destination $ReleaseDir -Recurse
Rename-Item -LiteralPath (Join-Path $ReleaseDir "FormulaOCR.exe") -NewName "公式识别.exe"

$requiredFiles = @(
    "_internal\PySide6\QtCore.pyd",
    "_internal\PySide6\Qt6Core.dll",
    "_internal\PySide6\shiboken6.abi3.dll",
    "_internal\PySide6\python3.dll",
    "_internal\PySide6\python312.dll",
    "_internal\models\unimernet_tiny\unimernet_tiny.pth",
    "_internal\assets\MML2OMML.XSL"
)

foreach ($relativePath in $requiredFiles) {
    $fullPath = Join-Path $ReleaseDir $relativePath
    if (-not (Test-Path $fullPath)) {
        throw "Missing required packaged file: $relativePath"
    }
}

$UsageText = @"
双击运行：公式识别.exe

请保留整个“公式识别”文件夹，不要只单独拷贝 exe。
_internal 文件夹包含 Python 运行库、Qt、OCR 模型和程序资源，缺失后会无法启动。

如果要移动到其他电脑，请复制整个 dist\公式识别 文件夹。
"@

$UsageText | Set-Content -LiteralPath (Join-Path $ReleaseDir "使用说明.txt") -Encoding UTF8

Write-Host ""
Write-Host "Build complete: dist\公式识别\公式识别.exe"

