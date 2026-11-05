@echo off
setlocal

REM ==================================================
REM CONFIGURACIÓN BASE
REM ==================================================

set SCRIPT_DIR=%~dp0
cd /d %SCRIPT_DIR%

echo.
echo ==================================================
echo QC Asset Groups - START
echo ==================================================
echo.

REM ==================================================
REM ACTIVAR ENTORNO VIRTUAL
REM ==================================================

IF EXIST ".venv\Scripts\activate.bat" (
    echo [INFO] Activando entorno virtual...
    call .venv\Scripts\activate.bat
)

REM ==================================================
REM INSTALAR DEPENDENCIAS
REM ==================================================

IF EXIST "requirements.txt" (
    echo [INFO] Instalando dependencias...
    python -m pip install -r requirements.txt
)

REM ==================================================
REM EJECUTAR SCRIPT PRINCIPAL
REM ==================================================

echo.
echo [INFO] Ejecutando proceso QC...
echo.

python -u src\main_v1.1.py

REM ==================================================
REM CONTROL DE ERRORES
REM ==================================================

IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo ==================================================
    echo ERROR EN LA EJECUCION
    echo Codigo salida: %ERRORLEVEL%
    echo ==================================================
    echo.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ==================================================
echo EJECUCION FINALIZADA
echo ==================================================
echo.

pause
exit /b 0