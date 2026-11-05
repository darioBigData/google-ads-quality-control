@echo off
REM =====================================================
REM Lanzador del proceso de Control de Calidad Google Ads
REM =====================================================

REM Fijar encoding UTF-8
chcp 65001 > nul

REM Establecer directorio raíz del proyecto
cd /d %~dp0

echo =========================================
echo Iniciando proceso Control Calidad Google Ads
echo Directorio: %cd%
echo =========================================

REM Comprobar Python
python --version
if errorlevel 1 (
    echo ERROR: Python no esta disponible en el PATH
    pause
    exit /b 1
)

REM Instalar dependencias (si existe requirements.txt)
if exist requirements.txt (
    echo Instalando dependencias...
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
) else (
    echo WARNING: No se encuentra requirements.txt. Se continua sin instalar dependencias.
)

REM Ejecutar proceso principal
echo Ejecutando proceso principal...
python src\main_v3.4.py

REM Fin
echo =========================================
echo Proceso finalizado
echo =========================================

pause
