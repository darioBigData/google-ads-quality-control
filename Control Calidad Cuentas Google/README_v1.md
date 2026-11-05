# Proceso de Validación de Cuentas Google Ads

## Objetivo del proceso

Este proceso tiene como objetivo **validar la calidad, coherencia y configuración de las cuentas de Google Ads de JOT**, asegurando que:

- La **nomenclatura de la cuenta** sigue los estándares definidos.
- La **configuración real de la cuenta** es coherente con la información declarada en su nombre.
- Los resultados son **trazables, auditables y reproducibles**.
- La arquitectura es **modular, consistente y escalable**, preparada para crecer sin refactors.

El proceso se ejecuta actualmente en **modo batch manual**, con posibilidad de evolución a ejecución programada.

---

## Flujo general del proceso

1. Lectura de un fichero CSV de entrada con `customer_id` / Query SQL Server (Cuentas Activas Google).
2. Para cada cuenta:
   - Se inicializa un **contexto de ejecución** común.
   - Se obtiene la información básica de la cuenta vía **Google Ads API**.
   - Se ejecutan los **controles habilitados**.
3. Cada control devuelve un resultado independiente:
   - `OK`
   - `ERROR`
   - `ERROR_TECNICO`
   - `SKIP`
4. Se generan 2 **CSV de salida por ejecución** :
   - CSV Resumen (1 fila por cuenta)
   - CSV Detalle (1 fila por control que haya resultado ERROR)
5. Se generan logs con información clave de la ejecución mediante un .txt, además de un csv con el estado de la ejecución (checkpoint_YYYYMMDD_HHMMSS.csv)   

### Manejo de errores de acceso

Si una cuenta no es accesible (por ejemplo `CUSTOMER_NOT_ENABLED`):

- Se escribe una única fila en el CSV con:
  - `status = ERROR_TECNICO`
  - detalle informativo del motivo
- **No se ejecuta ningún control** para esa cuenta.

---

## Flujo output SQL Server

START
 └─ INSERT PROCESS_EXECUTION
      execution_status = 'EN_PROCESO'

FOR each account
 ├─ ejecutar controles
 ├─ calcular account_status
 ├─ calcular failed_controls
 └─ INSERT ACCOUNT_RUN

END
 └─ UPDATE PROCESS_EXECUTION
      execution_status = 'OK' | 'ERROR'
      execution_success = 1 | 0
      error_detail = ...


## Principios de arquitectura

- **Separación estricta de responsabilidades**:
  - El `main`:
    - Orquesta el proceso.
    - Ejecuta GAQL.
    - Inicializa servicios (Google Ads, SQL Server).
    - Construye el `context`.
    - Gestiona consola y output CSV.
  - Los controles:
    - **No ejecutan GAQL ni SQL** (salvo casos excepcionales justificados).
    - Evalúan únicamente el `context`.
    - Devuelven un resultado estandarizado.
- **Una fila por cuenta y control** en el output.
- **Configuración externa** (sin valores sensibles en código).
- **Trazabilidad completa** por ejecución.

---

## Contexto compartido (`context`)

Todos los controles reciben el mismo `context`, que incluye:

- Información de ejecución (fecha, usuario, servidor).
- Configuración (`config.json`).
- Datos de entrada (`customer_id`).
- Datos de cuenta obtenidos vía GAQL.
- Servicios inicializados (Google Ads, SQL Server).
- Resultados de controles previos.

Esto permite:
- Desacoplamiento total.
- Reutilización de lógica.
- Pruebas unitarias sencillas.
- Escalabilidad futura.

---


## Controles del proceso

### Control 1 — Nomenclatura de la cuenta

Valida que el **nombre completo de la cuenta** sigue la estructura oficial de JOT.

- Validación estructural del nombre completo de la cuenta.
- Validación por bloques.
- Uso de catálogos internos JOT (vía SQL Server).
- El bloque **Config_Geo** se valida de forma explícita contra catálogo corporativo, sin inferencias ni valores implícitos.
- Devuelve un **resultado global** por cuenta.
- En caso de error técnico, se indica el bloque que falla.

---

### Control 2 — Línea de negocio

Valida que la **línea de negocio declarada en el nombre de la cuenta** es coherente con los **tipos de campañas existentes** en Google Ads.

- Se excluyen campañas con estado `REMOVED`.
- Se incluyen campañas activas, en pausa, limitadas o en aprendizaje.
- Si la cuenta solo contiene campañas `REMOVED` → `SKIP`.

---

### Control 3 — Zona horaria

Valida que la **zona horaria configurada** en la cuenta coincide con la esperada según estándares JOT.

---

### Control 4 — Moneda

Valida la moneda de la cuenta.

- Actualmente, todas las cuentas JOT deben estar en **HKD**.

---

### Control 5 — Tracking template

•	Nivel cuenta.
•	Evalúa customer.tracking_url_template.
•	Se valida igualdad exacta con la string canónica del calálogo de templates de SQL Server
•	Usa un template canónico por Clave de concatenación (socio-destino-tipo landing-canal)

Este control está validado con tests reales y forzados.

---

### Control 6 — Final URL suffix

- Nivel: cuenta.
- Regla de negocio:
  - `None` o `""` → `OK`
  - Cualquier string con contenido → `ERROR`
- Se tiene en cuenta que GAQL devuelve `None` cuando el campo está vacío.

---

### Control 7 — Auto-tagging

- Nivel: cuenta.
- Evalúa `customer.auto_tagging_enabled`.
- El GAQL se ejecuta en el `main`; el control solo evalúa el contexto.

---

### Control 8 — Content suitability

- Confirmado: **nivel cuenta**.
- Objetivo: Validar que la cuenta tiene excluidos los dominios aparcados (Parked domains).
- Fuente de datos: Google Ads API (GAQL estándar).
- Entidad GAQL: customer_negative_criterion.
- Tipo de criterio: CONTENT_LABEL.
- Estado actual: IMPLEMENTADO.

---

### Control 9 — Content suitability (Excluded Placements)

Valida que la cuenta tiene excluidos, a nivel cuenta, todos los emplazamientos (webs / dominios) definidos en el catálogo corporativo obligatorio.

   - Nivel: cuenta.

   - Fuente Google Ads: customer_negative_criterion (PLACEMENT).

   - Fuente catálogo: SQL Server (legacy, no modificable).

   - Se aplica normalización canónica:

   - Eliminación de www.,

   - colapso de paths de país (/xx) al dominio base.

   - Si falta al menos un dominio requerido → ERROR.

   - Control probado con casos reales y forzados.

   - Estado: IMPLEMENTADO Y CERRADO.
---

### Control 10 - Cuenta de Facturación (JOT)

Valida que la cuenta de Google Ads tiene **activa** la configuración de facturación corporativa de JOT, 
identificando de forma tecnica cual es el billing setup activo.

**Alcance**

- Recupera los billing setups de la cuenta via Google Ads API (GAQL).

- Identifica el billing setup activo segun criterios tecnicos:

  - status = APPROVED

  - end_time_type = FOREVER

  - end_date_time vacio

- Valida que el payments account del setup activo sea el de JOT (3346-5368-2267-7514).

**Limitaciones**

- GAQL no permite identificar la facturacion activa en la UI.

- La validacion se basa solo en campos tecnicos del billing setup.

**Resultado del control**

- OK: billing activo con facturacion JOT.

- ERROR: billing activo sin facturacion JOT.

- ERROR_TECNICO: error GAQL o inconsistencia tecnica.

**Estado**  
IMPLEMENTADO · VALIDADO · CERRADO

### Control 11 — Cuenta de conversiones

•	Nivel cuenta.

•	Limitación técnica identificada:
  - GAQL solo indica si la cuenta hereda o no
  -	No permite saber exactamente qué MCC es el owner
  - Tampoco podemos diferenciar entre casos en los que la cuenta es heredada y casos en los que no existe ninguna cuenta de conversiones asignada
    (En ambas situaciones el parámetro devuelve None)
• Estado actual: SKIP.

Este control permanecerá a nivel informativo por ahora.

---

## Logs

- Ubicación: `/logs`
- Formato: TXT plano
- Un log por ejecución

### Contenido del log
El proceso genera un fichero de log por ejecución con información de **trazabilidad global del batch**.

El log incluye:

- **Inicio del proceso**, con:
  - identificador de ejecución (`run_id`)
  - usuario del sistema que lanza el proceso

- **Resumen final de la ejecución**, con:
  - número total de cuentas procesadas
  - número de cuentas con validación completa sin errores
  - número de cuentas con algún error (funcional o técnico)

- **Rutas de los ficheros de output generados**:
  - fichero de resumen (`output_resumen.csv`)
  - fichero de detalle de errores (`output_detalle_errores.csv`)

- **Fin del proceso**

Los errores técnicos **no se detallan individualmente en el log**, ya que:

- los errores funcionales se reflejan en el fichero `output_detalle_errores.csv`
- los errores técnicos se consolidan a nivel cuenta en el fichero `output_resumen.csv`


## Estructura de carpetas

/proceso_validacion_google_ads
│
├── config/     # Configuración del proceso y controles
├── controls/   # Controles de validación (lógica desacoplada)
├── src/        # Orquestación principal (main) y catálogos SQL
├── input/      # Ficheros de entrada (CSV)
├── output/     # Resultados por ejecución
├── logs/       # Logs por ejecución
│
├── run.bat     # Lanzador Windows
└── README.md

---

## Configuración

### `config.json`

Define:
- Rutas de input, output y logs.
- Controles a ejecutar.
- Parámetros de logging.
- Integración con SQL Server.
- Ruta a `jot_lib`.

### `controls.json`

- Define **todos los controles existentes**.
- El `main` decide cuáles ejecutar según `config.json`.

---

## Estado actual del proyecto

- **Estado**: estable, en pruebas funcionales avanzadas.
- **Controles activos**: 1 al 10.
- **Control 11**: Implementado únicamente a modo informativo (Debido a limitación técnica).
- **Output**: CSV por ejecución (Resumen & Detalle errores).
- **Persistencia en SQL Server**: Diseñada a nivel esquemático, no activa aún.

---

## Notas finales

Este proceso está diseñado para:

- No asumir reglas de negocio no confirmadas.
- Mantener coherencia y trazabilidad.
- Permitir evolución progresiva sin romper compatibilidad.

Cualquier nuevo control o endurecimiento de reglas se incorporará **solo tras confirmación explícita de negocio**.






