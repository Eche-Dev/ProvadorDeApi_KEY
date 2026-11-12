@echo off
title Probador de API Keys & REST APIs ⚡
cls
echo ===================================================================
echo               PROBADOR DE API KEYS & REST APIs ⚡
echo ===================================================================
echo.
echo  Selecciona la version que deseas iniciar:
echo.
echo   [1] Interfaz de Escritorio (Ventana nativa de Windows)
echo   [2] Interfaz Web (Se abre automaticamente en tu navegador)
echo   [3] Salir
echo.
echo ===================================================================
set /p opcion="Elige una opcion (1, 2 o 3): "

if "%opcion%"=="1" (
    echo Iniciando version Escritorio...
    start "" pythonw gui.py
    exit
)
if "%opcion%"=="2" (
    echo Iniciando version Web en el navegador...
    python app_web.py
    pause
    exit
)
if "%opcion%"=="3" (
    exit
)

echo Opcion invalida. Saliendo...
pause
