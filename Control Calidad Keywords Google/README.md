# QC Google Ads Entities

Proceso de control de calidad (QC) para validar entidades de Google Ads:

* Keywords
* Sitelinks
* Callouts
* Snippets

---

## 📌 Descripción

Este proceso permite validar automáticamente reglas de negocio sobre campañas de Google Ads, incluyendo:

* Concordancia de keywords (debe ser BROAD)
* Keywords rechazadas (no debe haber ninguna)
* Número mínimo de assets por campaña:

  * Sitelinks ≥ 8
  * Callouts ≥ 6
  * Snippets ≥ 1

El sistema está diseñado con arquitectura modular y soporte de reanudación mediante checkpoints.

---

## 🧱 Estructura del proyecto

```
project/
│
├── config/
│   ├── config.json
│   └── controls.json
│
├── src/
│   ├── main.py
│   │
│   ├── core/
│   │   ├── logger.py
│   │   ├── checkpoint_manager.py
│   │   ├── control_loader.py
│   │   ├── control_validator.py
│   │   └── input_validator.py
│   │
│   ├── context/
│   │   ├── context_builder.py
│   │   └── data/
│   │       ├── keyword_data.py
│   │       └── asset_data.py
│   │
│   ├── controls/
│   │   ├── kw_correct_match.py
│   │   ├── kw_rechazadas.py
│   │   ├── sitelinks.py
│   │   ├── callouts.py
│   │   └── snippets.py
│   │
│   └── output/
│       ├── aggregator.py
│       └── output_writer.py
│
├── checkpoints/
├── logs/
├── output/
│   ├── resumen/
│   └── errores/
│
├── requirements.txt
└── run.bat
```

---

## ⚙️ Configuración

### `config.json`

```json
{
  "process": {
    "name": "qc_googleads_entities",
    "python_version_target": "3.11",
    "max_rows": 10000,
    "run_id_reference": null
  },
  "paths": {
    "input_csv_path": "input/input.csv",
    "output_dir": "output",
    "logs_dir": "logs",
    "checkpoint_dir": "checkpoints",
    "jotlib_path": "C:/ruta/a/jot_lib"
  }
}
```

---

## 🔁 Reanudación de ejecuciones (Checkpoint)

El proceso permite reanudar ejecuciones incompletas.

### Nuevo run

```json
"run_id_reference": null
```

👉 Genera un nuevo `run_id`

---

### Reanudar ejecución

```json
"run_id_reference": "20260414_120121"
```

👉 Reutiliza checkpoint existente:

```
checkpoints/checkpoint_20260414_120121.json
```

---

## ▶️ Ejecución

### Opción recomendada

```
run.bat
```

Incluye:

* Activación de entorno virtual
* Instalación de dependencias
* Control de errores

---

### Ejecución manual

```
python src/main.py
```

---

## 📥 Input

CSV con las siguientes columnas:

| Campo       | Obligatorio |
| ----------- | ----------- |
| customer_id | ✅           |
| campaign_id | opcional    |
| ad_group_id | opcional    |

---

## 📤 Outputs

### 📊 Resumen

Ruta:

```
output/resumen/
```

1 fila por entidad validada (campaign / ad_group según control)

Campos principales:

* customer_id
* campaign_id
* entity_type
* controles_error → `"0"` o `"1, 3"`

---

### ❌ Errores

Ruta:

```
output/errores/
```

1 fila por error detectado:

* control_id
* descripcion
* valores encontrados
* entidad afectada

---

## 🧠 Lógica de controles

### Keywords

* ✅ Concordancia correcta → BROAD
* ❌ Rechazadas → no permitido

---

### Assets (nivel campaña)

* Sitelinks ≥ 8
* Callouts ≥ 6
* Snippets ≥ 1

---

## 🧩 Arquitectura

### Context Builder

* Construye entidades desde GAQL
* Enriquecimiento con:

  * campaign_assets_count

---

### Controles

* Ejecutados dinámicamente desde `controls.json`
* Filtrados por:

  * entity_type
  * scope

---

### Checkpoint

* Evita reprocesar entidades
* Basado en:

```
customer_id | entity_type | entity_id
```

---

## 🛠 Debug

El sistema incluye logs detallados:

### Keywords

```
[DEBUG][KEYWORD]
```

### Assets

```
[DEBUG][ASSET]
```

Permite validar:

* Mapeo de enums
* Datos GAQL reales

---

## 📦 Dependencias

Instalar con:

```
pip install -r requirements.txt
```

---

## 🚀 Estado del proyecto

✔ Keywords funcionando
✔ Assets funcionando
✔ Controles implementados
✔ Checkpoints activos
✔ Outputs estructurados
✔ Debug completo

---

## 🔮 Futuras mejoras

* Persistencia en SQL Server
* Auditoría histórica por run_id
* Dashboard de resultados
* Ejecución paralela
* Alertas automáticas
