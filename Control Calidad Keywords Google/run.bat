@echo off
setlocal ENABLEDELAYEDEXPANSION

REM ==================================================
REM CONFIGURACIÓN BASE
REM ==================================================

REM Obtener directorio del script
set SCRIPT_DIR=%~dp0
cd /d %SCRIPT_DIR%

REM ==================================================
REM ACTIVAR ENTORNO VIRTUAL (SI EXISTE)
REM ==================================================

IF EXIST ".venv\Scripts\activate.bat" (
    echo [INFO] Activando entorno virtual...
    call .venv\Scripts\activate.bat
)

REM ==================================================
REM INSTALAR DEPENDENCIAS (SI EXISTE requirements.txt)
REM ==================================================

IF EXIST "requirements.txt" (
    echo [INFO] Instalando dependencias...
    pip install -r requirements.txt
)

REM ==================================================
REM EJECUCIÓN DEL PROCESO
REM ==================================================

echo.
echo ==========================================
echo Iniciando QC Keywords...
echo ==========================================
echo.

python src\main_v2.1.py

REM ==================================================
REM CÓDIGO DE SALIDA
REM ==================================================

IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo ==========================================
    echo ERROR EN EJECUCION
    echo Codigo salida: %ERRORLEVEL%
    echo ==========================================
    echo.
    exit /b %ERRORLEVEL%
)

echo.
echo ==========================================
echo EJECUCION FINALIZADA CORRECTAMENTE
echo ==========================================
echo.

exit /b 0