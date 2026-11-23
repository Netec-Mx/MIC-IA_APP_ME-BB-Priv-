# Práctica 1. Preparación del ambiente y análisis de escenarios de integración

**Módulo 1 · Arquitectura de integración de aplicaciones con Microsoft Entra** · Duración aproximada: **45 minutos**

## Objetivos

Al terminar la práctica podrás:

- Verificar que tu tenant de trabajo tiene las licencias, los roles, los usuarios y los grupos que usarán las prácticas 2 a 9.
- Registrar la autenticación multifactor (MFA) de los usuarios de prueba.
- Distinguir en el portal las **Enterprise applications** de los **App registrations**.
- Analizar seis aplicaciones de Contoso y elegir para cada una el protocolo de SSO, el mecanismo de aprovisionamiento y los datos que necesita.

## Antes de empezar

| Requisito | Cómo comprobarlo |
|---|---|
| Acceso por RDP a **LAB-CLIENT** | Recibiste de soporte la IP pública, el usuario `labadmin` y su contraseña |
| Cuenta `participante@labXX.onmicrosoft.com` y su contraseña inicial | Están en la hoja de datos que entregó soporte |
| Contraseña de los usuarios de prueba | Igual que la anterior |
| Un teléfono con **Microsoft Authenticator** | Lo usarás para tu cuenta y para los usuarios de prueba |

> **Cómo usar esta guía.** Cada paso tiene tres partes: la acción, una tabla que explica cada opción o parámetro y el resultado esperado. Si ya dominas el tema, sigue solo las acciones y compara con el resultado; si es tu primera vez, lee también las tablas. Los recuadros **Reto opcional** son para quien termine antes.
>
> **Convenciones.** `XX` es tu número de participante (los ejemplos usan `lab01`). Los menús del Microsoft Entra admin center se escriben en inglés, como aparecen en el portal; si tu portal está en español, los nombres equivalentes están en el mismo lugar.

**Archivos que se modifican en esta práctica**

| Archivo (en `C:\Curso\recursos`) | Qué haces |
|---|---|
| `datos\mis-datos.txt` | Registras los datos de tu ambiente que usarás en todo el curso |
| `datos\matriz-integracion.csv` | Completas la matriz de decisiones de las seis aplicaciones |

Al final de la guía está el contenido completo de ambos archivos como deben quedar.

---

## Contexto: el caso Contoso

En todo el curso trabajarás como parte del equipo de identidad de **Contoso**, una empresa de distribución que centraliza en Microsoft Entra el acceso a sus aplicaciones. Tu ambiente tiene dos partes:

| Componente | Qué representa |
|---|---|
| **Tenant de trabajo** `labXX.onmicrosoft.com` | El directorio corporativo de Contoso en Microsoft Entra |
| **LAB-SRV01** (dominio `contoso.local`) | El centro de datos: Active Directory, la intranet de RR. HH. y el ERP heredado |
| **LAB-CLIENT** | La computadora de un empleado que trabaja desde casa (fuera de la red corporativa) |

Los usuarios de prueba existen en Active Directory y se sincronizan a Microsoft Entra con Cloud Sync:

| Usuario | Departamento | Puesto | Grupos |
|---|---|---|---|
| `ana.lopez` | Compras | Compradora Sr. | DYN-Compras, Todos-Empleados |
| `luis.mendez` | Compras | Gerente de Compras | DYN-Compras, GRP-Compras-Jefes, Todos-Empleados |
| `marta.ruiz` | Finanzas | Analista de Finanzas | Todos-Empleados |
| `pedro.garcia` | Logística | Jefe de Almacén | GRP-Logistica, Todos-Empleados |
| `carla.diaz` | Recursos Humanos | Generalista de RR. HH. | GRP-RRHH, Todos-Empleados |
| `prueba.nube` | Compras | (usuario solo de nube) | DYN-Compras, Todos-Empleados |

---

## Tarea 1. Entrar al tenant de trabajo

**Paso 1.1.** Conéctate por RDP a **LAB-CLIENT** con `labadmin`. Abre **Microsoft Edge**.

**Paso 1.2.** Entra a `https://entra.microsoft.com` con `participante@labXX.onmicrosoft.com` y la contraseña inicial. El portal te pedirá:

1. Cambiar la contraseña (elige una que recuerdes durante las tres sesiones).
2. Registrar un método de MFA: instala o abre **Microsoft Authenticator** en tu teléfono, elige **Agregar cuenta › Cuenta profesional o educativa** y escanea el código QR.

| Concepto | Explicación |
|---|---|
| MFA obligatoria para administradores | Microsoft exige MFA para entrar a los portales de administración (Entra, Azure). Por eso se registra desde el primer inicio |
| Cuenta de laboratorio | Eres **Global Administrator** de tu tenant de laboratorio para no depender de permisos durante las prácticas. En producción se usan roles más acotados, como se vio en el Módulo 1 |

**Paso 1.3.** En el portal, abre **Entra ID › Overview**. Copia en `datos\mis-datos.txt` (ábrelo con VS Code desde `C:\Curso\recursos`):

- **Tenant ID** (GUID del tenant).
- **Primary domain** (`labXX.onmicrosoft.com`).

Resultado esperado: la página Overview muestra el nombre del tenant, el Tenant ID y la licencia **Microsoft Entra ID P2**.

**Paso 1.4.** Abre **Billing › Licenses › All products**.

| Columna | Qué observar |
|---|---|
| Product | `Microsoft Entra ID P2` (o Microsoft 365 E5 / EMS E5, que lo incluyen) |
| Total / Assigned | 7 asignadas: tu cuenta, los cinco usuarios sincronizados y `prueba.nube` |

---

## Tarea 2. Verificar el ambiente con Microsoft Graph PowerShell

**Paso 2.1.** Abre **PowerShell 7** (busca `pwsh` en el menú Inicio) y ejecuta:

```powershell
cd C:\Curso\recursos\scripts
./verificar-ambiente.ps1
```

Se abre una ventana de inicio de sesión: usa tu cuenta `participante@labXX.onmicrosoft.com`. La primera vez aparece una solicitud de **permisos** (consentimiento): marca **Consent on behalf of your organization** y acepta.

| Elemento | Explicación |
|---|---|
| `Connect-MgGraph -Scopes ...` | Inicia sesión en Microsoft Graph pidiendo solo permisos de lectura (`User.Read.All`, `Group.Read.All`, etc.) |
| Consentimiento | La aplicación "Microsoft Graph Command Line Tools" necesita que un administrador apruebe esos permisos una vez en el tenant |
| `-NoWelcome` | Omite el mensaje de bienvenida del módulo |
| El script | Solo **lee**: licencias, tu rol, los usuarios de prueba con sus atributos y licencia, sus métodos de MFA y los grupos |

Salida esperada (antes de la Tarea 3, la fila **MFA** de los usuarios de prueba dice `REVISAR`):

```text
Tenant: lab01.onmicrosoft.com   Cuenta: participante@lab01.onmicrosoft.com

Area      Elemento                            Estado  Detalle
----      --------                            ------  -------
Licencias AAD_PREMIUM_P2                      OK      Asignadas 7 de 7
Roles     participante@lab01.onmicrosoft.com  OK      Global Administrator
Usuarios  ana.lopez@lab01.onmicrosoft.com     OK      sincronizado | Compras | Compradora Sr. | EMP-00412 | licencia: AAD_PREMIUM_P2
MFA       ana.lopez@lab01.onmicrosoft.com     REVISAR 0 método(s) además de la contraseña
...
Grupos    DYN-Compras                         OK      3 miembro(s) | dinámico: user.department -eq "Compras"
Grupos    GRP-Proveedores                     OK      0 miembro(s) | asignado

12 elemento(s) por revisar.
```

**Paso 2.2.** Interpreta los resultados:

| Si ves… | Significa | Qué hacer |
|---|---|---|
| `sincronizado` en los cinco usuarios de Contoso | Cloud Sync funciona: los usuarios vienen de `contoso.local` | Nada |
| `nube` en `prueba.nube` | Usuario creado directamente en Entra | Nada: se usa para casos en que el usuario no existe en AD |
| `EMP-00412` en la columna de detalle | El atributo `employeeId` se sincroniza | Si sale vacío, avisa a soporte (mapeo de Cloud Sync) |
| `DYN-Compras: 3 miembro(s)` | La regla dinámica evaluó `department = Compras` (ana, luis y prueba.nube) | Si sale 0, espera unos minutos: la evaluación de grupos dinámicos no es inmediata |
| Fila de licencias en `REVISAR` | No hay licencias P2 disponibles o asignadas | Avisa a soporte antes de continuar |

---

## Tarea 3. Registrar la MFA de los usuarios de prueba

Las prácticas 5 y 7 aplican **acceso condicional** con MFA. Cada usuario de prueba necesita un método registrado. Puedes registrar varias cuentas en la misma app Microsoft Authenticator.

**Paso 3.1.** En Edge abre una **ventana InPrivate** (Ctrl+Mayús+N) y entra a `https://aka.ms/mysecurityinfo` con `ana.lopez@labXX.onmicrosoft.com`.

**Paso 3.2.** Cuando aparezca **More information required**, selecciona **Next** y registra Microsoft Authenticator (escanea el QR con tu teléfono). Cierra la ventana InPrivate.

| Opción | Efecto |
|---|---|
| Ventana InPrivate | Evita que la sesión de tu cuenta de administración se mezcle con la del usuario de prueba |
| Microsoft Authenticator | Método recomendado; también permite el inicio de sesión sin contraseña |
| "I want to use a different method" | Permite usar SMS si no puedes instalar la app (menos seguro; solo para laboratorio) |

**Paso 3.3.** Repite los pasos 3.1 y 3.2 con `luis.mendez`, `marta.ruiz`, `pedro.garcia` y `prueba.nube`. (`carla.diaz` es opcional.)

**Paso 3.4.** Vuelve a ejecutar `./verificar-ambiente.ps1`. Resultado esperado:

```text
MFA       ana.lopez@lab01.onmicrosoft.com     OK      1 método(s) además de la contraseña
...
Ambiente listo.
```

(Si no registraste a `carla.diaz`, su fila de MFA seguirá en `REVISAR`; es aceptable.)

---

## Tarea 4. Enterprise applications y App registrations

**Paso 4.1.** Abre **Entra ID › Enterprise apps › All applications**. Quita el filtro **Application type == Enterprise Applications** y vuelve a buscar.

| Qué observar | Explicación |
|---|---|
| Aparecen aplicaciones de Microsoft (Microsoft Graph Command Line Tools, Office 365…) | Son **service principals**: la presencia de esas aplicaciones en tu tenant |
| "Microsoft Graph Command Line Tools" | Se creó en la Tarea 2 cuando diste consentimiento; ahí se ven sus permisos (**Permissions**) |

**Paso 4.2.** Abre **Entra ID › App registrations › All applications**.

| Qué observar | Explicación |
|---|---|
| La lista está vacía (o casi) | Los **application objects** solo existen en el tenant que "es dueño" de la aplicación. Las apps de Microsoft tienen su application object en el tenant de Microsoft |
| En la Práctica 2 | Al crear la aplicación SAML aparecerá en **ambas** vistas: application object (App registrations) y service principal (Enterprise apps) |

---

## Tarea 5. Analizar los escenarios de integración de Contoso

**Paso 5.1.** En VS Code abre `C:\Curso\recursos\datos\escenarios-contoso.md` y lee las seis aplicaciones.

**Paso 5.2.** Abre `datos\matriz-integracion.csv` y completa una fila por aplicación. Usa estos criterios (del Módulo 1):

| Columna | Pregunta que responde | Opciones típicas |
|---|---|---|
| `Usuarios` | ¿Quién inicia sesión? | Empleados, socios/proveedores (B2B), clientes (CIAM) |
| `Ubicacion` | ¿Dónde vive la aplicación? | SaaS de galería, SaaS fuera de galería, desarrollo propio, on-premises |
| `Protocolo_SSO` | ¿Qué transporta la identidad? | SAML 2.0, OIDC/OAuth 2.0, application proxy con KCD o encabezados, External ID |
| `Aprovisionamiento` | ¿Cómo se crea y se desactiva la cuenta? | SCIM de galería, SCIM propio, no aplica, autoservicio |
| `Claims_o_datos_clave` | ¿Qué necesita saber la aplicación del usuario? | NameID, roles, atributos, encabezados, scopes |
| `Requisito_de_licencia` | ¿Qué función de Entra exige licencia? | P1 para grupos, acceso condicional y application proxy; MAU para externos |
| `Practica` | ¿Dónde se practica en el curso? | Número de práctica o "Referencia" |

> **Pista.** Si dentro de un valor necesitas una coma, usa punto y coma (`;`): la coma separa columnas en el CSV.

**Paso 5.3.** Compara tu matriz con `soluciones\matriz-integracion-solucion.csv` y discute las diferencias con el grupo. Puntos que suelen generar discusión:

| Aplicación | Pregunta de discusión |
|---|---|
| Portal de proveedores | ¿Por qué SAML y no OIDC, si OIDC es más moderno? (lo decide el fabricante: solo soporta SAML) |
| Intranet RR. HH. | ¿Por qué no hay aprovisionamiento? (la aplicación usa las cuentas de AD DS que ya existen) |
| ERP heredado | ¿Qué riesgo tiene confiar en un encabezado HTTP? (cualquiera que llegue directo al servidor podría falsificarlo) |
| Tienda en línea | ¿Por qué un external tenant y no invitados B2B? (escala, registro de autoservicio y separación del directorio corporativo) |

> **Reto opcional.** Agrega una séptima fila para una aplicación que conozcas de tu organización y justifica la decisión.

---

## Resultado esperado

| Comprobación | Resultado |
|---|---|
| `verificar-ambiente.ps1` | "Ambiente listo." (o solo `carla.diaz` sin MFA) |
| Licencias | 7 de 7 asignadas |
| Grupos dinámicos | DYN-Compras con 3 miembros; Todos-Empleados con 7 |
| `mis-datos.txt` | Tenant ID y dominio registrados |
| Matriz | Seis filas completas y comparadas con la solución |

**Lista de verificación**

- [ ] Inicié sesión en el Microsoft Entra admin center con MFA.
- [ ] Ejecuté `verificar-ambiente.ps1` y entiendo cada fila.
- [ ] Registré MFA para ana, luis, marta, pedro y prueba.nube.
- [ ] Puedo explicar la diferencia entre Enterprise applications y App registrations.
- [ ] Completé la matriz de integración y la comparé con la solución.

## Archivos completos

**`C:\Curso\recursos\datos\mis-datos.txt`** (sección completada en esta práctica; el resto se llena en las siguientes)

```text
DATOS DE MI AMBIENTE (se completan en la Práctica 1 y se usan en todo el curso)
==============================================================================

Número de participante (XX) .............. 01
Dominio del tenant de trabajo ............. lab01.onmicrosoft.com
ID del tenant de trabajo (Tenant ID) ...... 2b6c4f1e-7a2d-4c1b-9e35-0d8a3f6c1e41
Cuenta de administración .................. participante@lab01.onmicrosoft.com
Contraseña de los usuarios de prueba ...... (la entrega soporte; no la escribas aquí si compartes el equipo)
```

(El Tenant ID es un ejemplo: usa el de tu tenant.)

**`C:\Curso\recursos\datos\matriz-integracion.csv`**

```text
Aplicacion,Usuarios,Ubicacion,Protocolo_SSO,Aprovisionamiento,Claims_o_datos_clave,Requisito_de_licencia,Practica
ServiceNow,Empleados,SaaS (galeria),SAML 2.0 con plantilla de galeria,SCIM de galeria,NameID = UPN; roles por grupo,Entra ID Free (SSO); P1 para asignar grupos,Referencia (Modulo 2 y 3)
Portal de proveedores,Compras (empleados) y proveedores (B2B),SaaS fuera de galeria,SAML 2.0 fuera de galeria,SCIM 2.0 propio,NameID = correo; role (app roles); numeroEmpleado,P1 (grupos y acceso condicional); invitados por MAU,Practicas 2 a 4 y 7
Intranet RR. HH.,Empleados,On-premises (IIS con autenticacion de Windows),Application proxy + KCD,No aplica (cuentas de AD DS),SPN HTTP/hr.contoso.local; identidad delegada UPN,P1 (application proxy),Practicas 5 y 6
ERP heredado,Finanzas y logistica,On-premises (lee encabezados HTTP),Application proxy + SSO por encabezados,Interno del ERP,X-User = sAMAccountName; X-Email; X-Dept,P1 (application proxy),Practica 6
App movil de ventas,Fuerza de ventas,Desarrollo propio (movil + API),OpenID Connect y OAuth 2.0 con MSAL,No requiere,Scope api://pedidos/Orders.Read; roles en el access token,Entra ID Free; P1 para acceso condicional,Referencia (Modulo 1)
Tienda en linea,Clientes (consumidores),Desarrollo propio web,External ID (external tenant) con OIDC,Autoservicio con user flow,Nombre; pais; AceptaPromociones,External ID por MAU (primeros 50 000 sin costo),Practica 8
```

## Problemas comunes

| Síntoma | Causa | Solución |
|---|---|---|
| `Connect-MgGraph` no se reconoce | El módulo Microsoft.Graph no está instalado en PowerShell 7 | Usa `pwsh` (no Windows PowerShell 5.1); si persiste, avisa a soporte |
| "Need admin approval" al conectar Graph | No marcaste el consentimiento para la organización | Repite con tu cuenta de administración y marca **Consent on behalf of your organization** |
| Un usuario no aparece o sale como `nube` siendo de Contoso | Cloud Sync no lo ha sincronizado | Espera unos minutos o avisa a soporte para usar **Provision on demand** |
| `DYN-Compras` con 0 miembros | Procesamiento de la regla dinámica en curso | Espera 5 a 10 minutos y vuelve a ejecutar el script |
| No se muestra el QR de MFA | Ya existe un método registrado para ese usuario | Revisa `https://aka.ms/mysecurityinfo`: si ya aparece Authenticator, el usuario está listo |
| El CSV se ve en una sola columna en Excel | Excel usa punto y coma como separador regional | Edítalo en VS Code, o en Excel usa **Datos › Desde texto/CSV** con separador coma |
