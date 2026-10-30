# Setup Guide General

## [NOMBRE COMPLETO DEL CURSO]

| Control documental | Información |
|---|---|
| Clave del curso | [CLAVE] |
| Versión del documento | [VERSIÓN] |
| Estado | [BORRADOR / VALIDADO] |
| Instructor responsable | [NOMBRE] |
| Fecha de elaboración | [AAAA-MM-DD] |
| Fecha de última validación | [AAAA-MM-DD] |
| Repositorio de laboratorios | [URL] |
| Rama y revisión analizada | [RAMA Y COMMIT / ETIQUETA] |
| Alcance revisado | [TOTAL DE CAPÍTULOS, PRÁCTICAS Y DOCUMENTOS REVISADOS] |
| Modalidad del entorno | [LOCAL / WEB / CLOUD / VIRTUALIZADO / HÍBRIDO] |

> **Instrucciones para el instructor — eliminar antes de entregar:** completar los campos entre corchetes y duplicar las filas o bloques necesarios. Revisar todo el repositorio antes de llenar la guía. Consolidar requisitos comunes y dependencias puntuales necesarias, sin organizar el documento por práctica. Conservar únicamente las secciones y plataformas aplicables. Eliminar instrucciones de llenado, ejemplos y campos pendientes de la versión validada. No incluir teoría, ejercicios ni soluciones académicas. No registrar secretos. Distinguir requisitos del repositorio, recomendaciones del instructor y comprobaciones realmente ejecutadas.

# Objetivo

[DESCRIBIR EL ENTORNO QUE SE PREPARARÁ PARA TODO EL CURSO, SUS COMPONENTES PRINCIPALES Y LA CONDICIÓN GENERAL PARA CONSIDERARLO LISTO.]

# Requisitos de Hardware

| Recurso | Mínimo requerido | Recomendado | Observaciones |
|---|---|---|---|
| Procesador y arquitectura | [VALOR] | [VALOR] | [OBSERVACIÓN] |
| Memoria RAM | [VALOR] | [VALOR] | [OBSERVACIÓN] |
| Espacio libre | [VALOR] | [VALOR] | [INCLUIR IMÁGENES, DATOS Y ENTORNOS SI APLICAN] |
| Pantalla | [VALOR] | [VALOR] | [OBSERVACIÓN] |
| Conectividad | [VALOR] | [VALOR] | [VELOCIDAD O CONDICIÓN DE RED, SI ESTÁ DEFINIDA] |
| [OTRO RECURSO NECESARIO] | [VALOR] | [VALOR] | [GPU, VIRTUALIZACIÓN O PERIFÉRICO, SOLO SI APLICA] |

# Sistemas Operativos Compatibles

| Sistema operativo | Edición y versión | Arquitectura | Condición de soporte o validación |
|---|---|---|---|
| [SISTEMA] | [EDICIÓN Y VERSIÓN] | [ARQUITECTURA] | [VALIDADO / COMPATIBLE SEGÚN FABRICANTE / RESTRICCIÓN] |

[INDICAR LA PLATAFORMA BASE DEL CURSO Y LAS DIFERENCIAS DE PREPARACIÓN ENTRE LAS ALTERNATIVAS ADMITIDAS. NO DECLARAR COMO PROBADAS PLATAFORMAS QUE NO SE HAYAN VALIDADO.]

# Software Requerido

| Componente | Edición y versión requerida | Arquitectura | Obligatorio u opcional | Fuente oficial |
|---|---|---|---|---|
| [SOFTWARE / RUNTIME / SDK / IDE / CLI / NAVEGADOR] | [VERSIÓN] | [ARQUITECTURA] | [CONDICIÓN] | [URL] |

[PARA SERVICIOS SAAS SIN VERSIÓN FIJABLE, INDICAR “SERVICIO ADMINISTRADO” Y REGISTRAR FECHA, EDICIÓN VISIBLE Y CONFIGURACIÓN. NO INVENTAR NÚMEROS DE VERSIÓN.]

# Herramientas y Dependencias

## Paquetes, frameworks y componentes adicionales

| Dependencia | Versión o restricción | Componente que la necesita | Método de instalación o habilitación |
|---|---|---|---|
| [DEPENDENCIA] | [VERSIÓN] | [COMPONENTE] | [MÉTODO] |

[IDENTIFICAR TAMBIÉN DEPENDENCIAS QUE LOS LABORATORIOS ASUMEN DISPONIBLES. INDICAR EL MANIFIESTO, LOCKFILE O WRAPPER EXISTENTE CUANDO CORRESPONDA.]

## Licencias, cuentas y permisos

| Recurso o servicio | Licencia o suscripción | Cuenta o rol requerido | Permiso mínimo | Responsable de habilitación |
|---|---|---|---|---|
| [RECURSO] | [LICENCIA] | [TIPO DE CUENTA / ROL] | [PERMISO] | [RESPONSABLE] |

[INDICAR CÓMO SE ENTREGAN LOS ACCESOS POR EL CANAL AUTORIZADO. NO PEGAR CONTRASEÑAS, TOKENS, CLAVES, COOKIES NI CÓDIGOS MFA.]

# Instalación y Configuración

## 1. Obtener los materiales

- Repositorio o paquete autorizado: [URL O UBICACIÓN].
- Revisión que se utilizará: [COMMIT / ETIQUETA / VERSIÓN].
- Directorio de trabajo: [RUTA COMPLETA POR SISTEMA OPERATIVO].
- Archivos de entrada o plantillas que deben estar disponibles: [LISTADO Y UBICACIÓN].

[INDICAR EL MÉTODO REAL PARA DESCARGAR, CLONAR O ACCEDER AL MATERIAL. DIFERENCIAR LOS ARCHIVOS DISTRIBUIDOS DE LOS QUE SE CREAN DURANTE EL CURSO.]

## 2. Instalar o habilitar los componentes

[ORDENAR LOS PASOS SEGÚN SUS DEPENDENCIAS. DUPLICAR ESTE BLOQUE POR COMPONENTE NECESARIO, NO POR PRÁCTICA. PARA SERVICIOS WEB, DOCUMENTAR HABILITACIÓN Y ACCESO EN LUGAR DE INVENTAR UNA INSTALACIÓN LOCAL.]

### [COMPONENTE]

1. [OBTENER LA VERSIÓN REQUERIDA DESDE LA FUENTE OFICIAL].
2. [INSTALAR O HABILITAR CON LAS OPCIONES NECESARIAS].
3. [APLICAR LA CONFIGURACIÓN COMÚN].
4. [COMPROBAR EL RESULTADO].

**Plataforma y terminal:** [SISTEMA OPERATIVO Y SHELL].

```text
[REEMPLAZAR POR COMANDOS REALES Y USAR LA ETIQUETA CORRECTA: powershell, bat, bash, ETC.]
```

**Resultado esperado:** [VERSIÓN, RUTA, ESTADO O MENSAJE QUE DEBE OBTENERSE].

## 3. Preparar archivos de configuración

| Archivo | Ruta completa o relativa a la raíz definida | Configuración necesaria | Origen |
|---|---|---|---|
| [ARCHIVO] | [RUTA] | [PARÁMETROS SIN SECRETOS] | [INCLUIDO EN REPOSITORIO / CREAR / ENTREGAR] |

[INCLUIR EL CONTENIDO BASE SOLO SI ES NECESARIO PARA PREPARAR EL ENTORNO. INDICAR CÓMO RESOLVER VALORES ESPECÍFICOS DEL CLIENTE SIN EXPONER CREDENCIALES.]

# Variables de Entorno

| Variable | Propósito | Valor o formato esperado | Alcance | Método de configuración |
|---|---|---|---|---|
| [NOMBRE] | [PROPÓSITO] | [VALOR NO SENSIBLE O REFERENCIA A SECRETO] | [SESIÓN / USUARIO / PROYECTO / SERVICIO] | [MÉTODO] |

**Configuración — [SISTEMA OPERATIVO Y SHELL]:**

```text
[COMANDOS REALES PARA DEFINIR LAS VARIABLES NECESARIAS]
```

**Verificación sin exponer secretos:**

```text
[COMANDOS PARA VALIDAR PRESENCIA, FORMATO O VALORES NO SENSIBLES]
```

# Configuración Base para los Laboratorios

## Parámetros comunes

| Parámetro | Valor o convención | Observaciones |
|---|---|---|
| Raíz de trabajo | [RUTA] | [UBICACIÓN LOCAL O CLOUD] |
| [ENTORNO / REGIÓN / PROYECTO / NAMESPACE] | [VALOR] | [OBSERVACIÓN] |
| [PUERTO / URL BASE / ZONA HORARIA] | [VALOR] | [OBSERVACIÓN] |
| [OTRO PARÁMETRO COMÚN] | [VALOR] | [OBSERVACIÓN] |

## Estructura de carpetas

[DOCUMENTAR SOLO LAS CARPETAS NECESARIAS PARA EL SETUP Y LOS COMANDOS PARA PREPARARLAS, SI APLICAN. INDICAR CUÁLES DEBEN REUTILIZARSE.]

## Recursos compartidos

| Recurso | Nombre o identificador | Estructura o configuración base | Responsable de creación |
|---|---|---|---|
| [BASE DE DATOS / LISTA / BUCKET / COLA / BIBLIOTECA / CONEXIÓN] | [NOMBRE] | [CONFIGURACIÓN] | [RESPONSABLE] |

[CUANDO SE REQUIERAN ESQUEMAS, COLUMNAS O TIPOS, DOCUMENTARLOS AQUÍ. DEFINIR AISLAMIENTO ENTRE PARTICIPANTES, PERMISOS Y REUTILIZACIÓN DE RECURSOS. NO PRECONSTRUIR LOS EJERCICIOS.]

## Correcciones de coherencia

| Inconsistencia o dependencia omitida | Configuración unificada | Ajuste necesario en las copias de trabajo |
|---|---|---|
| [HALLAZGO] | [CRITERIO VALIDADO] | [AJUSTE Y SU ALCANCE] |

[REGISTRAR DIFERENCIAS DE VERSIONES, RUTAS, NOMBRES O ACCESOS QUE AFECTEN LA PREPARACIÓN. NO CAMBIAR REGLAS DE NEGOCIO COMO SI FUERAN REQUISITOS DE INSTALACIÓN.]

# Servicios Externos Requeridos

| Servicio | URL, endpoint o región | Uso | Acceso requerido |
|---|---|---|---|
| [SERVICIO] | [VALOR] | [PROPÓSITO] | [CUENTA / ROL / CONEXIÓN] |

## Configuración de red

| Origen | Destino | Protocolo y puerto | Sentido | Condición |
|---|---|---|---|---|
| [ORIGEN] | [HOST / DOMINIO / SERVICIO] | [PROTOCOLO Y PUERTO] | [ENTRANTE / SALIENTE / LOCAL] | [REQUISITO] |

[INDICAR DNS, PROXY, VPN, CERTIFICADOS, COOKIES O REGLAS DE FIREWALL SOLO CUANDO APLIQUEN. ENLAZAR LA LISTA OFICIAL DE ENDPOINTS SI ES DINÁMICA.]

# Creación de Entornos / Máquinas Virtuales / Emuladores

[CONSERVAR SOLO LAS MODALIDADES QUE REALMENTE UTILICE EL CURSO.]

| Elemento | Tipo o plataforma | Imagen y versión | Recursos asignados | Red o región | Persistencia |
|---|---|---|---|---|---|
| [NOMBRE] | [ENTORNO VIRTUAL / VM / CONTENEDOR / CLÚSTER / EMULADOR / ENTORNO CLOUD] | [VERSIÓN] | [CPU / RAM / DISCO, SI APLICA] | [CONFIGURACIÓN] | [DATOS O VOLÚMENES] |

1. [CREAR O APROVISIONAR].
2. [CONFIGURAR RED, ACCESO Y ALMACENAMIENTO].
3. [INICIAR Y VALIDAR].
4. [INDICAR ARRANQUE, DETENCIÓN Y REUTILIZACIÓN; INCLUIR CONTROL DE COSTOS SI APLICA].

```text
[COMANDOS REALES O PROCEDIMIENTO WEB NECESARIO]
```

# Validación del Entorno

| ID | Componente o capacidad | Procedimiento | Resultado esperado | Evidencia mínima |
|---|---|---|---|---|
| V-01 | [COMPONENTE] | [PRUEBA DE PREPARACIÓN] | [CRITERIO OBSERVABLE] | [SALIDA / REGISTRO / CAPTURA AUTORIZADA] |
| V-02 | [COMPONENTE] | [PRUEBA DE PREPARACIÓN] | [CRITERIO OBSERVABLE] | [EVIDENCIA] |

**Criterio de entorno listo:** [INDICAR QUÉ VALIDACIONES DEBEN APROBARSE Y CÓMO SE TRATAN LOS COMPONENTES OPCIONALES].

[VALIDAR CON UNA CUENTA EQUIVALENTE A LA DEL PARTICIPANTE. DISTINGUIR INSTALACIÓN, CONECTIVIDAD, AUTENTICACIÓN, PERMISOS Y EJECUCIÓN FUNCIONAL. NO PRESENTAR UN HTTP 200 O LA EXISTENCIA DE UN ARCHIVO COMO PRUEBA SUFICIENTE DE ACCESO O FUNCIONAMIENTO.]

# Comandos de Verificación

[DUPLICAR EL BLOQUE POR TECNOLOGÍA Y SISTEMA APLICABLE. USAR COMANDOS OFICIALES, RUTAS COMPLETAS CUANDO CORRESPONDA Y WRAPPERS DEL REPOSITORIO CUANDO EXISTAN. NO INCLUIR COMANDOS DE TECNOLOGÍAS AJENAS AL CURSO.]

## [COMPONENTE O CAPACIDAD]

**Plataforma y terminal:** [SISTEMA OPERATIVO Y SHELL].  
**Directorio de ejecución:** [RUTA COMPLETA].  
**Prerrequisito:** [ENTORNO ACTIVO, SESIÓN AUTENTICADA O SERVICIO INICIADO].

```text
[COMANDO REAL DE VERIFICACIÓN]
```

**Resultado esperado:**

```text
[SALIDA, VERSIÓN O ESTADO ESPERADO]
```

**Interpretación:** [QUÉ ACREDITA LA PRUEBA Y QUÉ COMPROBACIÓN ADICIONAL REQUIERE].

[SI LA TECNOLOGÍA SE VALIDA ÚNICAMENTE EN UNA INTERFAZ WEB, DOCUMENTAR LA SECUENCIA Y EL RESULTADO OBSERVABLE. NO INSTALAR UNA CLI O UN SDK SOLO PARA CREAR UN COMANDO DE VERIFICACIÓN.]

# Troubleshooting

| Síntoma | Causa probable | Comprobación | Corrección | Validación posterior |
|---|---|---|---|---|
| [PROBLEMA] | [CAUSA] | [DIAGNÓSTICO] | [ACCIÓN CONCRETA] | [PRUEBA QUE DEBE REPETIRSE] |

# Checklist Final

- [ ] Hardware y sistema operativo cumplen los requisitos aplicables.
- [ ] Versiones de software y dependencias coinciden con la configuración unificada.
- [ ] Licencias, cuentas y permisos están habilitados.
- [ ] Materiales, archivos de entrada y plantillas necesarios están disponibles.
- [ ] Carpetas y archivos de configuración están preparados.
- [ ] Variables de entorno necesarias están configuradas sin exponer secretos.
- [ ] Recursos y servicios requeridos están accesibles.
- [ ] Red, autenticación y conexiones funcionan desde la estación del participante.
- [ ] Entornos, máquinas o contenedores necesarios inician correctamente.
- [ ] Validaciones obligatorias completadas con los resultados esperados.
- [ ] Evidencias y fecha de validación registradas.
- [ ] Instrucciones de llenado, secciones no aplicables y campos pendientes eliminados.

[AJUSTAR EL CHECKLIST: ELIMINAR LOS PUNTOS QUE NO APLIQUEN Y AGREGAR LOS CONTROLES ESPECÍFICOS NECESARIOS.]

# Resumen

[DESCRIBIR BREVEMENTE LA CONFIGURACIÓN FINAL REQUERIDA PARA INICIAR EL CURSO, SIN RESUMIR LOS LABORATORIOS.]

## Registro de validación

| Fecha | Responsable | Plataforma o entorno probado | Resultado | Limitaciones o acciones pendientes |
|---|---|---|---|---|
| [AAAA-MM-DD] | [NOMBRE] | [SISTEMA / CUENTA DE LABORATORIO / ENTORNO] | [APTO / NO APTO] | [DETALLE O NINGUNA] |

[INDICAR EXPRESAMENTE QUÉ SE VALIDÓ Y QUÉ NO. NO MARCAR COMO VALIDADO UN ENTORNO CON BLOQUEOS EN COMPONENTES OBLIGATORIOS.]

## Referencias oficiales

| Documento o recurso | URL | Fecha de consulta |
|---|---|---|
| [DOCUMENTACIÓN DEL FABRICANTE / INSTALACIÓN / LICENCIAMIENTO / COMPATIBILIDAD] | [URL] | [AAAA-MM-DD] |
