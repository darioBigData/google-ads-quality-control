# QC Ads Google Ads

## Qué hace el proceso

Este proceso ejecuta un Control de Calidad (QC) sobre anuncios de Google Ads a partir de un CSV de entrada.

Flujo:
1. Lee el input CSV.
2. Consulta anuncios en Google Ads mediante jot_lib.
3. Construye un contexto por anuncio.
4. Ejecuta controles desacoplados definidos en `config/controls.json`.
5. Genera un CSV de resumen y un CSV de errores.
6. Registra logs por ejecución.
7. Guarda checkpoint para reanudación.

## Estructura

```text
qc_ads_google/
├─ config/
│  ├─ config.json
│  └─ controls.json
├─ controls/
│  ├─ ad_status.py
│  ├─ ad_type.py
│  └─ ad_final_url.py
├─ input/
│  └─ input.csv
├─ logs/
├─ output/
│  ├─ resumen/
│  └─ errores/
├─ resume/
│  └─ checkpoints/
├─ src/
│  ├─ main.py
│  ├─ core/
│  ├─ context/
│  ├─ input_providers/
│  ├─ output/
│  └─ utils/
├─ run.bat
├─ requirements.txt
└─ README.md

Configuración

Revisar:

jotlib_path
input_file
controls_file
log_folder
output.resumen_folder
output.errores_folder
resume.checkpoint_folder
limits.max_rows_per_execution
Input

Separador: ;

Campos:

customer_id obligatorio
campaign_id opcional
ad_group_id opcional

Comportamiento:

solo customer_id: todos los anuncios del cliente
campaign_id: filtra por campaña
ad_group_id: filtra por grupo de anuncios
Controles incluidos
Ad Status
Ad Type
Ad Final URL
Ejecución

En Windows:

Completar config/config.json.
Colocar el CSV en input/input.csv.
Ejecutar run.bat.
Outputs
Resumen

Carpeta: output/resumen

Campos:

execution_user
customer_id
campaign_id
ad_group_id
ad_id
campaign_name
ad_group_name
ad_type
status_global
total_controles
controles_error
error_tecnico
checkpoint_status
Errores

Carpeta: output/errores

Campos:

execution_user
customer_id
campaign_id
ad_group_id
ad_id
campaign_name
ad_group_name
control_id
control_name
severity
valor_esperado
valor_encontrado
detalle
Logs

Se genera un log por ejecución en logs/log_YYYYMMDD_HHMMSS.txt.

Checkpoint

Se guarda en resume/checkpoints/checkpoint_ads_<run_id>.json.

Errores frecuentes
jotlib_path inválido
input no encontrado
falta customer_id
error de autenticación Google Ads
filtros sin resultados
Notas
No hay IA en este proceso.
No hay histórico acumulado.
No hay SQL Server para outputs en esta versión.
La ejecución es manual.
Los controles se cargan dinámicamente desde config/controls.json.