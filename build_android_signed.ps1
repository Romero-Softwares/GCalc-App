<#!
.SYNOPSIS
Gera APK e AAB Android de release assinados com a chave do projeto.

.DESCRIPTION
As senhas nunca sao escritas em arquivos: se as variaveis de ambiente ainda
nao existirem, o PowerShell as solicita sem exibi-las durante esta execucao.
#>

[CmdletBinding()]
param(
    [ValidateSet("apk", "aab", "all")]
    [string]$Target = "all"
)

$ErrorActionPreference = "Stop"
$keystorePath = Join-Path $PSScriptRoot "chaveAppGcalc.keystore"

if (-not (Test-Path -LiteralPath $keystorePath -PathType Leaf)) {
    throw "Chave de assinatura nao encontrada: $keystorePath"
}

function Get-PlainTextSecret([string]$Prompt) {
    $secureValue = Read-Host -Prompt $Prompt -AsSecureString
    $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureValue)
    try {
        return [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
    }
    finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
    }
}

$env:FLET_ANDROID_SIGNING_KEY_STORE = $keystorePath
$env:FLET_ANDROID_SIGNING_KEY_ALIAS = "merotecdev"

if ([string]::IsNullOrWhiteSpace($env:FLET_ANDROID_SIGNING_KEY_STORE_PASSWORD)) {
    $env:FLET_ANDROID_SIGNING_KEY_STORE_PASSWORD = Get-PlainTextSecret "Senha do keystore"
}

if ([string]::IsNullOrWhiteSpace($env:FLET_ANDROID_SIGNING_KEY_PASSWORD)) {
    $env:FLET_ANDROID_SIGNING_KEY_PASSWORD = Get-PlainTextSecret "Senha da chave (pressione Enter se for a mesma do keystore)"
    if ([string]::IsNullOrWhiteSpace($env:FLET_ANDROID_SIGNING_KEY_PASSWORD)) {
        $env:FLET_ANDROID_SIGNING_KEY_PASSWORD = $env:FLET_ANDROID_SIGNING_KEY_STORE_PASSWORD
    }
}

$commonArgs = @(
    "build",
    "--module-name", "main",
    "--android-signing-key-store", $keystorePath,
    "--android-signing-key-alias", "merotecdev"
)

if ($Target -in @("apk", "all")) {
    & flet @commonArgs "apk"
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}

if ($Target -in @("aab", "all")) {
    & flet @commonArgs "aab" "--arch" "arm64-v8a"
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}

Write-Host "Build assinado concluido. Artefatos em build\\apk e build\\aab."
