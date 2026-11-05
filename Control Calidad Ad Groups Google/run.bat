@echo off

echo ================================
echo     QC AD GROUPS - RUN
echo ================================

cd /d %~dp0

python src/main_v1.py

echo.
echo ================================
echo     PROCESO FINALIZADO
echo ================================

pause