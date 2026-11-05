# Google Ads – Quality Control Automation

## Descripción del proyecto

Proyecto de automatización de controles de calidad de datos sobre diferentes entidades de Google Ads, desarrollado mediante Python, Google Ads API y SQL.

El objetivo es detectar inconsistencias, valores incorrectos y posibles desviaciones en los datos de las cuentas publicitarias, automatizando las comprobaciones que permiten garantizar su integridad y coherencia.

El proyecto está compuesto por seis programas independientes, cada uno especializado en una entidad de Google Ads.

## Objetivos

- Automatizar los procesos de control de calidad de los datos de Google Ads.
- Detectar valores incorrectos, inconsistencias y posibles errores de configuración.
- Contrastar los datos obtenidos de la API con catálogos de referencia almacenados en SQL.
- Aplicar reglas de validación específicas para cada entidad.
- Reducir la necesidad de comprobaciones manuales y mejorar la fiabilidad de los datos.

## Controles de calidad implementados

El proyecto incluye seis controles independientes:

| Control | Descripción |
|---|---|
| Ads | Validación de anuncios y sus atributos. |
| Ad Groups | Comprobación de la integridad y coherencia de los grupos de anuncios. |
| Asset Groups | Validación de los grupos de recursos de campañas. |
| Campaigns | Comprobación de los atributos y parámetros de configuración de las campañas. |
| Accounts | Validación de los datos y parámetros de las cuentas publicitarias. |
| Keywords | Comprobación de los valores y atributos de las palabras clave. |

Cada programa aplica un conjunto de reglas de validación adaptadas a las características de la entidad correspondiente.

## Funcionamiento

El proceso de control de calidad se basa principalmente en dos fuentes de información:

**1. Google Ads API**

Obtención de los datos mediante consultas GAQL (Google Ads Query Language), que permiten acceder a los diferentes recursos y atributos de las cuentas publicitarias.

**2. Catálogos de referencia SQL**

En aquellos controles que lo requieren, los datos obtenidos de Google Ads se contrastan con catálogos SQL que contienen los valores canónicos esperados.

Estos catálogos actúan como fuente de referencia para identificar discrepancias entre los datos existentes y los valores que deberían tener.

### Tipos de validaciones

Se implementan diferentes estrategias de comprobación según las características de cada dato:

- **Validación contra catálogos:** comparación de los valores obtenidos de Google Ads con los valores canónicos almacenados en SQL.
- **Validación de valores esperados:** comprobación de que determinados campos contienen un valor específico.
- **Validación de valores no permitidos:** detección de valores que no deberían estar presentes.
- **Validación de consistencia:** comprobación de que los atributos cumplen las reglas y condiciones establecidas.

## Tecnologías utilizadas

- **Python:** desarrollo de los programas y lógica de validación.
- **Google Ads API:** acceso a los datos de las entidades publicitarias.
- **GAQL:** lenguaje de consulta para obtener información de Google Ads.
- **SQL Server:** consulta de catálogos de referencia y contraste de información.

## Estructura del proyecto

El repositorio contiene seis programas independientes, organizados según la entidad de Google Ads que se desea validar.

Cada programa implementa sus propias consultas, reglas de validación y comprobaciones específicas.

## Contexto de desarrollo

Este proyecto fue desarrollado como parte de la experiencia profesional en el ámbito de Data Engineering y automatización de procesos de calidad de datos.

El código publicado ha sido adaptado para su presentación como portfolio técnico, eliminando referencias a sistemas, accesos y recursos internos de la empresa.


