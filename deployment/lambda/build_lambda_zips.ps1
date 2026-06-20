param(
    [ValidateSet("x86_64", "arm64")]
    [string]$Architecture = "x86_64"
)

$ErrorActionPreference = "Stop"

$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$BuildRoot = Join-Path $ProjectRoot "deployment\lambda\build"
$OutputRoot = Join-Path $ProjectRoot "deployment\lambda\dist"
$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $Python)) {
    throw "Project virtual environment not found. Create .venv and install pip first."
}

foreach ($path in @($BuildRoot, $OutputRoot)) {
    $fullPath = [System.IO.Path]::GetFullPath($path)
    if (-not $fullPath.StartsWith($ProjectRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to modify a path outside the project workspace: $fullPath"
    }
    if (Test-Path -LiteralPath $fullPath) {
        Remove-Item -LiteralPath $fullPath -Recurse -Force
    }
    New-Item -ItemType Directory -Path $fullPath | Out-Null
}

if ($Architecture -eq "arm64") {
    $Platform = "manylinux2014_aarch64"
} else {
    $Platform = "manylinux2014_x86_64"
}

function Build-LambdaPackage {
    param(
        [string]$Name,
        [string]$RequirementsFile
    )

    $PackageDirectory = Join-Path $BuildRoot $Name
    $ZipPath = Join-Path $OutputRoot "$Name.zip"
    New-Item -ItemType Directory -Path $PackageDirectory | Out-Null

    & $Python -m pip install `
        --requirement $RequirementsFile `
        --target $PackageDirectory `
        --platform $Platform `
        --implementation cp `
        --python-version 3.12 `
        --abi cp312 `
        --only-binary=:all: `
        --upgrade

    if ($LASTEXITCODE -ne 0) {
        throw "Dependency installation failed for $Name"
    }

    Copy-Item -LiteralPath (Join-Path $ProjectRoot "app") `
        -Destination $PackageDirectory `
        -Recurse

    Get-ChildItem -Path $PackageDirectory -Directory -Recurse -Filter "__pycache__" |
        ForEach-Object {
            try {
                Remove-Item -LiteralPath $_.FullName -Recurse -Force -ErrorAction Stop
            } catch {
                Write-Warning "Could not remove cache directory $($_.FullName); continuing."
            }
        }
    Get-ChildItem -Path $PackageDirectory -File -Recurse -Include "*.pyc", "*.pyo" |
        ForEach-Object {
            try {
                Remove-Item -LiteralPath $_.FullName -Force -ErrorAction Stop
            } catch {
                Write-Warning "Could not remove cache file $($_.FullName); continuing."
            }
        }

    Compress-Archive -Path (Join-Path $PackageDirectory "*") `
        -DestinationPath $ZipPath `
        -CompressionLevel Optimal

    $Zip = Get-Item -LiteralPath $ZipPath
    Write-Host "$Name -> $($Zip.FullName) ($([math]::Round($Zip.Length / 1MB, 2)) MB)"
}

Build-LambdaPackage `
    -Name "fake-store-sftp-to-s3" `
    -RequirementsFile (Join-Path $PSScriptRoot "requirements-sftp.txt")

Build-LambdaPackage `
    -Name "fake-store-payment-processor" `
    -RequirementsFile (Join-Path $PSScriptRoot "requirements-payment-processor.txt")
