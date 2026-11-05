# Proceso de Control de Calidad de Asset Groups (Performance Max)

## Objetivo del proceso

Este proceso tiene como objetivo **validar la calidad, coherencia y configuración de los Asset Groups de campañas Performance Max de Google Ads**, asegurando que:

- Los **Asset Groups cumplen los requisitos mínimos de assets definidos por Google**.
- La **configuración de los assets es coherente con los estándares internos de JOT**.
- Los resultados son **trazables, auditables y reproducibles**.
- La arquitectura es **modular, consistente y escalable**, preparada para incorporar nuevos controles sin refactors.

El proceso se ejecuta actualmente en **modo batch manual**, con posibilidad de evolución a ejecución programada.

---

# Flujo general del proceso

1. Lectura de un fichero CSV de entrada con:
   - `customer_id`
   - `campaign_id` (opcional)

2. Para cada cuenta / campaña:

   - Se inicializa un **contexto de ejecución**.
   - Se recuperan los **Asset Groups de campañas Performance Max** vía Google Ads API.
   - Se recuperan los **assets asociados a cada Asset Group** si los controles lo requieren.

3. Para cada Asset Group:

   - Se construye un **contexto independiente**.
   - Se ejecutan los **controles habilitados**.

4. Cada control devuelve un resultado independiente:

   - `OK`
   - `ERROR`
   - `ERROR_TECNICO`
   - `SKIP`

5. Se generan **dos CSV de salida por ejecución**:

   - CSV **Resumen** (1 fila por Asset Group)
   - CSV **Detalle de errores** (1 fila por control con resultado `ERROR`)

6. Se generan **logs de ejecución** para garantizar trazabilidad del proceso.

---

# Principios de arquitectura

El sistema sigue una arquitectura basada en **modularidad y separación estricta de responsabilidades**.

### El `main`:

- Orquesta el proceso completo
- Inicializa servicios (Google Ads API)
- Lee el input CSV
- Ejecuta los controles
- Gestiona progreso y logs
- Genera los outputs

### El `context_builder`:

- Recupera datos desde Google Ads API
- Construye el contexto que usarán los controles
- Centraliza la lógica de acceso a datos

### Los controles:

- **No ejecutan GAQL ni consultas externas**
- Evalúan únicamente la información disponible en el `context`
- Devuelven un resultado estandarizado

### Los módulos `context/data`:

- Encapsulan las queries GAQL necesarias
- Proveen datos estructurados al `context_builder`

---

# Contexto compartido (`context`)

Todos los controles reciben el mismo objeto `context`, que incluye:

- `customer_id`
- `campaign_id`
- información de la cuenta (`account`)
- información de la campaña (`campaign`)
- información del asset group (`asset_group`)
- assets asociados (`images`, `logos`, `assets`)
- métricas internas del proceso (`metrics`)

Ejemplo simplificado:
context = {

"customer_id": "...",
"campaign_id": "...",

"account": {...},

"campaign": {
    "campaign_name": "...",
    "category_id": "..."
},

"asset_group": {
    "asset_group_id": "...",
    "asset_group_name": "..."
},

"images": [],
"logos": [],
"assets": [],
"asset_counts": {}

}


Esto permite:

- desacoplamiento total entre controles
- reutilización de lógica
- pruebas unitarias sencillas
- escalabilidad futura

---

# Controles del proceso

Actualmente el sistema incluye controles de validación sobre la calidad de los Asset Groups de campañas Performance Max.

## AG001 — Minimum Assets

Valida que el Asset Group contiene el número mínimo de assets recomendado por Google.

Ejemplos de validaciones:

- número mínimo de **headlines**
- número mínimo de **descriptions**
- presencia de **imágenes**
- presencia de **logo**

Resultado:

- `OK` si cumple los requisitos
- `ERROR` si falta algún asset obligatorio

---

## AG002 — Final URL Domain

Valida que el dominio de la `final_url` del Asset Group coincide con el dominio esperado según los estándares definidos.

Objetivo:

- evitar redirecciones a dominios incorrectos
- detectar configuraciones inconsistentes

---

## AG003 — Business Name

Valida que el **Business Name utilizado en los assets** coincide con el destino esperado definido para la cuenta.

Este control ayuda a detectar:

- inconsistencias de branding
- configuraciones incorrectas en assets

---

## AG004 — Asset Group Name vs Campaign

Valida que el **nombre del Asset Group es coherente con el nombre de la campaña**.

Este control busca detectar:

- errores de nomenclatura
- duplicidades
- inconsistencias estructurales

---

## AG005 — Call To Action

Valida que el **Call To Action utilizado en los assets** coincide con el estándar definido.

Actualmente se valida:


CALL_TO_ACTION_SELECTION = LEARN_MORE


---

## AG006 — Image Category

Valida que las imágenes utilizadas en el Asset Group cumplen los criterios definidos para la categoría de campaña.

---

## AG007 — Logo Destination

Valida que los logos utilizados en el Asset Group corresponden al destino correcto de la cuenta.

---

# Logs

- Ubicación: `/logs`
- Formato: TXT
- Un log por ejecución

Cada ejecución genera un fichero:


logs/run_YYYYMMDD_HHMMSS.txt


El log incluye:

- inicio del proceso
- usuario que ejecuta el proceso
- número de Asset Groups procesados
- número de resultados OK
- número de resultados con error
- número de llamadas a Google Ads API
- duración total del proceso

---

# Estructura de carpetas


/qc_asset_groups_google_ads
│
├── config/ # Configuración del proceso
├── controls/ # Controles de validación
├── src/ # Lógica principal del proceso
│
├── input/ # CSV de entrada
├── output/ # Resultados por ejecución
│ ├── resumen/
│ └── errores/
│
├── logs/ # Logs de ejecución
│
├── requirements.txt
├── run.bat
└── README.md


---

# Configuración

## config.json

Define:

- rutas de input, output y logs
- ruta a `jot_lib`
- configuración del proceso
- controles activos

## controls.json

Define:

- todos los controles existentes
- parámetros asociados a cada control

El `main` decide qué controles ejecutar en función de esta configuración.

---

# Input

El proceso espera un CSV en:


input/input.csv


Estructura:


customer_id;campaign_id


- `customer_id` → obligatorio
- `campaign_id` → opcional

Si `campaign_id` no se especifica, el proceso evaluará **todas las campañas Performance Max de la cuenta**.

---

# Outputs

Cada ejecución genera:

### Resumen


output/resumen/output_resumen_YYYYMMDD_HHMMSS.csv


Contiene una fila por Asset Group evaluado.

### Detalle de errores


output/errores/output_detalle_errores_YYYYMMDD_HHMMSS.csv


Contiene una fila por control que haya resultado `ERROR`.

---

# Estado actual del proyecto

- **Estado:** estable
- **Arquitectura:** modular y extensible
- **Controles activos:** AG001 – AG007
- **Ejecución:** batch manual

El sistema está preparado para:

- añadir nuevos controles
- ampliar fuentes de datos
- integrarse con persistencia futura en SQL Server

---

# Notas finales

Este proceso está diseñado para:

- mantener coherencia en la configuración de Asset Groups
- detectar errores de calidad en campañas Performance Max
- proporcionar resultados trazables y reproducibles

La arquitectura modular permite añadir nuevos controles sin modificar la lógica principal del proceso.