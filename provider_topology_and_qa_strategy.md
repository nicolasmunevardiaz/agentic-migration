# Topologia De Adapters Y Estrategia QA

## Proposito

Este documento define la topologia tecnica inicial para llevar archivos heterogeneos de proveedores hacia datasets Silver confiables. El alcance actual es Raw/Bronze -> Silver. Todo lo que ocurra despues de Silver queda fuera de esta estrategia inicial.

El objetivo es que cada adapter sea facil de explicar, probar, depurar y mejorar. QA no es solo una lista de validaciones: es el feedback loop que permite descubrir problemas, corregirlos y volver a ejecutar con evidencia clara.

## Alcance

Incluye:

- Descubrimiento de archivos Raw y creacion de manifiestos.
- Extraccion Bronze con metadata de parseo y lineage.
- Adapters por proveedor que transforman registros parseados hacia contratos Silver.
- Quarantine para archivos ilegibles, filas invalidas y mappings no resueltos.
- Evidencia QA que indique que fallo, donde fallo y que decision se debe tomar.

No incluye:

- Modelos posteriores a Silver.
- Validaciones funcionales posteriores a Silver.
- Convenciones de codigos para reglas.
- Orquestacion final de produccion.
- Decisiones semanticas automatizadas sin aprobacion humana.

## Topologia Objetivo

```text
Archivos del proveedor
  |
  v
Manifest Raw
  - path del archivo
  - proveedor
  - entidad candidata
  - formato
  - tamano
  - checksum
  - timestamp de discovery
  |
  v
Parser compartido por formato
  - csv / txt / json / xml / fixed-width cuando aplique
  - emite filas parseadas + metadata de parseo
  - envia archivos o filas no legibles a quarantine
  |
  v
Adapter del proveedor
  - nombres de campos especificos
  - limpieza de fechas, enums, codigos e IDs
  - flags de mapping no resuelto
  - razones de quarantine a nivel fila
  |
  v
Bronze
  - payload parseado
  - lineage de origen
  - estado de parseo
  - estado del adapter
  |
  v
Silver
  - entidades tipadas
  - nombres normalizados
  - lineage obligatorio
  - controles tecnicos de calidad
  |
  v
Evidencia QA + cola de revision humana
```

## Modelo De Adapter

Un adapter es la frontera tecnica entre la forma real de un proveedor y el contrato Silver compartido. No debe resolver preguntas posteriores a Silver. Su trabajo es hacer explicito como se interpreta la fuente y que tan confiable es esa interpretacion.

Cada adapter debe declarar:

- Source binding: donde se esperan los archivos del proveedor/entidad y como se agrupan.
- Estrategia de formato: que parser usa cada tipo de archivo y que opciones requiere.
- Mapping de campos: campo fuente, campo Silver, transformacion, confianza y estado de revision.
- Estrategia de tipos: fechas, timestamps, numericos, booleanos, identificadores y codigos.
- Estrategia de quarantine: que falla bloquea archivo, que falla aisla fila y que falla solo advierte.
- Estrategia de lineage: que metadata debe sobrevivir en Bronze y Silver.
- Fixtures de prueba: ejemplos pequenos positivos y negativos que prueban el comportamiento.

Siempre que sea posible, el adapter debe ser configuration-first. El codigo especifico por proveedor solo se justifica cuando el formato, la limpieza o la normalizacion realmente lo requieran.

## Como Se Conecta Un Adapter A La Fuente

Para planearlo, cada adapter se conecta mediante un perfil de fuente:

```text
perfil del proveedor
  -> perfil de entidad
    -> patrones de archivo esperados
    -> formato esperado
    -> opciones del parser
    -> expectativas de schema
    -> mapping de campos
    -> salida de quarantine
    -> salida de evidencia QA
```

En desarrollo local, el perfil puede apuntar a carpetas locales. En Databricks, el mismo perfil deberia apuntar a ubicaciones gobernadas de datos. El adapter no debe hardcodear paths; debe recibir las ubicaciones por configuracion del ambiente.

Flujo del adapter:

1. Lee las entradas del manifest para un proveedor/entidad.
2. Selecciona el parser segun formato declarado o detectado.
3. Convierte cada registro a un row envelope comun con metadata de origen.
4. Aplica mapping y normalizacion especifica del proveedor.
5. Escribe registros validos hacia Bronze y candidatos Silver.
6. Escribe registros invalidos a quarantine con razon clara.
7. Emite evidencia QA para la ejecucion.

## Human In The Loop Por Adapter

La revision humana es obligatoria cuando la decision cambia significado, no cuando solo hay un error tecnico evidente.

Puntos de revision:

- Cobertura de fuente: confirmar que los archivos descubiertos representan el alcance esperado del proveedor/entidad.
- Mapping de campos: aprobar mappings inciertos antes de promoverlos a Silver.
- Interpretacion de tipos: aprobar fechas ambiguas, campos mixtos, IDs con ceros a la izquierda y codigos clinicos o financieros.
- Quarantine recurrente: revisar razones repetidas y decidir si se corrige el adapter o se documenta un problema de fuente.
- Contrato Silver: aprobar columnas requeridas, nullability, claves candidatas y lineage obligatorio.

La salida de cada revision debe ser pequena y trazable: decision, owner, fecha, evidence path y siguiente accion.

## Contrato Bronze

Bronze es la capa tecnica de aterrizaje para datos parseados. Debe estar cerca de la fuente, pero ser consultable y auditable.

Cada registro Bronze debe incluir:

- Proveedor y entidad.
- Referencia estable al archivo fuente.
- Checksum del archivo fuente.
- Referencia de fila de origen.
- Identificador de ejecucion.
- Estado y error de parser cuando aplique.
- Estado y error de adapter cuando aplique.
- Payload parseado o columnas parseadas.
- Hash del registro cuando exista una representacion estable.

Bronze debe conservar suficiente informacion para reconstruir Silver cuando cambie un mapping, schema o regla de calidad.

## Contrato Silver

Silver es la primera capa normalizada y tipada. Debe seguir siendo tecnica, no analitica.

Cada entidad Silver debe definir:

- Nombre de entidad.
- Columnas requeridas.
- Tipos de datos.
- Nullability.
- Clave primaria candidata.
- Claves foraneas candidatas cuando existan tecnicamente.
- Columnas de lineage obligatorias.
- Criterios de quarantine.
- Thresholds de warning aceptados.

Silver nunca debe inventar valores silenciosamente. Si un valor no se puede mapear o tipar con confianza, la evidencia queda en Bronze y la fila se envia a quarantine o revision humana.

## QA Como Feedback Loop

```text
ejecutar adapter
  -> recolectar evidencia
  -> clasificar hallazgos
  -> asignar owner
  -> corregir parser / mapping / contrato / fuente
  -> repetir las mismas pruebas
```

Resultados posibles:

- Stop pipeline: la ejecucion no es confiable para continuar.
- Quarantine data: se aisla el archivo o fila afectada y se continua con lo valido.
- Warn: se continua, pero el hallazgo queda visible para revision.

## Contrato De Evidencia QA

Cada prueba automatizada debe producir evidencia machine-readable. Evitar codigos como explicacion principal; usar nombres descriptivos.

Campos minimos:

- test_name
- test_family
- stage
- provider
- entity
- source_file
- source_file_checksum
- row_reference cuando aplique
- outcome
- decision
- expected
- observed
- failure_count
- evidence_path
- executed_at

La evidencia debe permitir que otro ingeniero reproduzca el problema sin leer logs completos.

## Familias De Pruebas

### Unit Tests De Datos

Prueban el comportamiento mas pequeno de un parser o adapter en aislamiento.

Ejemplos:

- Un parser CSV maneja headers, delimitadores, filas vacias y valores con comillas.
- Un parser JSON maneja objeto, arreglo y line-delimited records.
- Un adapter preserva IDs con ceros a la izquierda, normaliza fechas y mapea enums conocidos.
- Una fila invalida produce la razon de quarantine esperada.

Evidencia esperada: fixture, input, output esperado, output observado y diff.

### Tests De Integracion

Prueban que parser, adapter, quarantine y escritura Bronze/Silver funcionen juntos para un proveedor/entidad.

Ejemplos:

- Un archivo de pacientes se parsea hacia Bronze y filas validas llegan a Silver.
- Filas con fechas invalidas van a quarantine mientras las validas continuan.
- Errores del adapter conservan proveedor, entidad, archivo y referencia de fila.

Evidencia esperada: archivos de entrada, conteos de salida, conteos de quarantine y referencias seguras.

### Tests End-To-End / System Tests

Prueban el camino completo Raw/Bronze -> Silver sobre un dataset pequeno y controlado.

Ejemplos:

- Un archivo representativo por proveedor/entidad pasa por discovery, parseo, Bronze, Silver, quarantine y evidencia QA.
- Un rerun con el mismo input produce los mismos conteos y no duplica registros Silver.

Evidencia esperada: resumen de ejecucion, conteos por etapa, resumen de quarantine y comparacion de rerun.

### Tests De Calidad De Datos

Prueban que Silver sea tecnicamente usable.

Ejemplos:

- Identificadores requeridos existen o la fila queda en quarantine.
- Fechas parsean correctamente y valores imposibles quedan marcados.
- Enums normalizados pertenecen al set aprobado.
- Campos criticos no superan thresholds de null-rate.

Evidencia esperada: columna fallida, descripcion de regla, filas impactadas, threshold y referencias de fila.

### Tests De Esquema

Prueban que Bronze y Silver respeten contratos tecnicos aprobados.

Ejemplos:

- Existen columnas obligatorias de lineage.
- Columnas Silver tienen nombres, tipos y nullability esperados.
- Campos fuente nuevos se reportan en vez de ignorarse.
- Campos removidos o renombrados se detectan antes de romper mappings.

Evidencia esperada: schema diff, campos agregados, campos faltantes, cambios de tipo y proveedor/entidad impactado.

### Tests De Regresion De Datos

Prueban que los edge cases ya conocidos sigan funcionando cuando evolucionen los adapters.

Ejemplos:

- Fixtures aprobados siguen produciendo los mismos resultados Bronze y Silver.
- Filas malformadas ya corregidas siguen llegando a la misma razon de quarantine.
- Cambios de mapping aparecen como diff intencional y revisable.

Evidencia esperada: version del fixture, salida anterior, salida nueva y diferencias aprobadas/no aprobadas.

### Tests De Reconciliacion De Datos

Prueban que no se pierdan ni dupliquen registros entre etapas.

Ejemplos:

- Filas parseadas = filas Bronze validas + filas en quarantine.
- Filas candidatas Bronze = filas Silver aceptadas + filas Silver en quarantine.
- Checksums en Bronze coinciden con el manifest Raw.
- Reprocesar el mismo archivo no crea duplicados no intencionales.

Evidencia esperada: conteos por proveedor/entidad/archivo, formula de reconciliacion, diferencias y decision.

## Direccion De Ejecucion En Databricks

Databricks debe ser el runtime protagonista para escalar el flujo, mientras que la ejecucion local sirve para iterar rapido con fixtures pequenas.

Direccion recomendada:

- Desarrollar adapters con fixtures pequenas y reproducibles.
- Ejecutar parseo, materializacion Bronze/Silver y QA a escala en Databricks cuando el contrato del adapter sea estable.
- Guardar Bronze, Silver, quarantine y evidencia QA en ubicaciones gobernadas dentro de Databricks.
- Usar capacidades declarativas de calidad de datos de Databricks cuando encajen con reglas simples por fila.
- Usar orquestacion de Databricks para ejecuciones programadas, reruns y observabilidad.
- Mantener la logica del adapter versionada para que el mismo comportamiento pueda probarse localmente y desplegarse en Databricks.

Los agentes de Databricks pueden evaluarse como apoyo para resumir evidencia QA, preparar paquetes de revision humana y explicar fallas repetidas. No deben reemplazar pruebas deterministicas de parser, adapter, schema o reconciliacion.

## Estructura Minima Recomendada

```text
src/parsers/
src/adapters/
src/contracts/
src/quarantine/
tests/unit/
tests/integration/
tests/system/
tests/fixtures/
metadata/manifests/
metadata/qa/
docs/adapter_decisions/
```

## Que Evitar

- No agregar capas posteriores a Silver antes de estabilizar Raw/Bronze -> Silver.
- No usar IDs de reglas como explicacion principal del comportamiento QA.
- No hardcodear paths de proveedor, ambientes o ubicaciones cloud en el codigo del adapter.
- No coercionar campos ambiguos silenciosamente.
- No descartar filas invalidas sin conservar evidencia.
- No permitir que agentes tomen decisiones semanticas sin aprobacion humana.
