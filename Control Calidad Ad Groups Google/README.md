# QC Ad Groups (Search & Display)

## 📌 Descripción

Proceso de Control de Calidad (QC) para Ad Groups de campañas Google Ads (Search y Display).

El sistema:

- Lee un input CSV con customer_id (obligatorio), campaign_id (opcional) y ad_group_id (opcional)
- Consulta datos mediante GAQL (Google Ads)
- Construye contexto por Ad Group
- Ejecuta controles modulares
- Genera outputs (resumen + detalle de errores)
- Registra logs por ejecución
- Permite reanudación mediante checkpoint
- Muestra progreso en consola

---

## 📥 Input

Ruta:

input/input.csv


Formato:


customer_id;campaign_id;ad_group_id
1234567890,987654321
1234567890,


### Reglas

- `customer_id` → obligatorio
- `campaign_id` → opcional
- `ad_group_id` → opcional

---

## ⚙️ Ejecución

En Windows:


run.bat


O manual:


python src/main.py


---

## 📁 Estructura del proyecto


/config
/input
/output
├── resumen
└── errores
/logs
/resume

/src
├── main.py
├── context/
├── checkpoint/
├── output/
├── core/
└── ...

/controls


---

##  Funcionamiento

### 1. Carga input
Se leen los registros del CSV

### 2. Construcción de contexto
Se obtiene información de Ad Groups mediante una única query GAQL optimizada

### 3. Ejecución de controles
Cada control:


run(context: dict) -> dict


Devuelve:

- control_id
- status (OK / ERROR / ERROR_TECNICO / SKIP)
- valor_esperado
- valor_encontrado
- detalle
- error_tecnico

---

### 4. Checkpoint

Clave:


customer_id + ad_group_id


Permite:

- reanudar ejecuciones
- evitar reprocesar

---

### 5. Outputs

#### 📊 Resumen

Ubicación:

/output/resumen/


Campos:

- execution_user
- customer_id
- customer_name
- campaign_id
- campaign_name
- ad_group_id
- ad_group_name
- status_global
- controles_error
- error_tecnico

---

#### ❌ Detalle errores

Ubicación:

/output/errores/


Campos:

- execution_user
- customer_id
- customer_name
- campaign_id
- campaign_name
- ad_group_id
- ad_group_name
- control_id
- status
- valor_esperado
- valor_encontrado
- detalle
- error_tecnico

---

## 📊 Logs

Ubicación:

/logs/log_<run_id>.txt


Incluye:

- inicio de ejecución
- carga de datos
- errores técnicos
- métricas finales
- duración

---

## 🔄 Progreso en consola

Se muestra avance cada 2%:


[PROGRESS] 10/200 ad groups procesados (5.00%)


---

## ⚙️ Configuración (config/config.json)

Permite configurar:

- rutas
- checkpoint
- logging
- controles a ejecutar
- progreso

---

## 🧪 Controles

Ubicación:


/controls


Estructura:


def run(context: dict) -> dict


---

## 🚀 Rendimiento

Optimizado para:

- 1 query GAQL por customer
- procesamiento batch
- sin queries por ad group

---

## ⚠️ Notas

- Los enums de Google Ads pueden requerir normalización
- `cpc_bid_micros` está en micros (1€ = 1,000,000)
- `bid_modifiers` puede generar múltiples filas (se agrupa)

---

## 🔮 Futuras mejoras

- integración completa con jot_lib
- normalización de enums
- control de interrupciones (CTRL+C)
- parámetros dinámicos por control
- logging avanzado
📄 requirements.txt
pandas

👉 (aunque ahora mismo no lo usas intensamente, es coherente con tus otros QC)

Si quieres ultra mínimo:

# vacío (solo librerías estándar)
📄 run.bat
@echo off

echo ================================
echo     QC AD GROUPS - RUN
echo ================================

cd /d %~dp0

python src/main.py

echo.
echo ================================
echo     PROCESO FINALIZADO
echo ================================

pause