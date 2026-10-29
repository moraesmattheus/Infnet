# ==============================================================================
# SCRIPT: abrir_no_emulador.ps1
# DATA/HORA: 29/10/2026 18:05
# AUTOR: Antigravity / Mattheus
# FINALIDADE: Script em PowerShell para automatizar a abertura do site legado
#            da Infnet dentro do emulador Android Pixel_Orion.
# ==============================================================================

Write-Host "[1/4] Desbloqueando tela do emulador..." -ForegroundColor Cyan
adb -s emulator-5554 shell input keyevent 82 | Out-Null
adb -s emulator-5554 shell input keyevent 3 | Out-Null

Write-Host "[2/4] Criando ponte de rede reversa (localhost:8080)..." -ForegroundColor Cyan
adb -s emulator-5554 reverse tcp:8080 tcp:8080

Write-Host "[3/4] Verificando servidor local na porta 8080..." -ForegroundColor Cyan
$listening = netstat -ano | Select-String ":8080\s"
if (-not $listening) {
    Write-Host "Iniciando servidor local..." -ForegroundColor Yellow
    $pastaFrontend = Join-Path $PSScriptRoot "Infnet_App_Dados antiga versao\frontend_completo"
    Start-Process -FilePath "python" -ArgumentList "-m", "http.server", "8080", "--directory", $pastaFrontend -WindowStyle Hidden
    Start-Sleep -Seconds 2
}

Write-Host "[4/4] Abrindo o Chrome no Pixel_Orion..." -ForegroundColor Cyan
adb -s emulator-5554 shell am start -a android.intent.action.VIEW -d "http://localhost:8080" -n com.android.chrome/com.google.android.apps.chrome.Main

Write-Host "`nSite aberto no emulador Pixel_Orion com sucesso!" -ForegroundColor Green
