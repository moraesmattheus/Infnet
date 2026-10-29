@echo off
REM ==============================================================================
REM ARQUIVO: abrir_no_emulador.bat
REM DATA/HORA: 29/10/2026 18:05
REM AUTOR: Antigravity / Mattheus
REM FINALIDADE: Atalho de 1 clique para iniciar o servidor web do frontend da
REM            Infnet e abrir automaticamente no emulador Android Pixel_Orion.
REM ==============================================================================

echo [1/4] Verificando conexao com o emulador...
adb -s emulator-5554 shell input keyevent 82 >nul 2>&1
adb -s emulator-5554 shell input keyevent 3 >nul 2>&1

echo [2/4] Criando ponte de rede do computador para o emulador (porta 8080)...
adb -s emulator-5554 reverse tcp:8080 tcp:8080

echo [3/4] Garantindo que o servidor local esta ativo...
netstat -ano | findstr ":8080 " >nul 2>&1
if errorlevel 1 (
    echo Iniciando servidor Python na porta 8080...
    start /b python -m http.server 8080 --directory "Infnet_App_Dados antiga versao\frontend_completo"
    timeout /t 2 /nobreak >nul
)

echo [4/4] Abrindo o site no Google Chrome do emulador Pixel_Orion...
adb -s emulator-5554 shell am start -a android.intent.action.VIEW -d "http://localhost:8080" -n com.android.chrome/com.google.android.apps.chrome.Main

echo.
echo =====================================================================
echo  Sucesso! O site da Infnet foi aberto na tela do seu Pixel_Orion.
echo =====================================================================
