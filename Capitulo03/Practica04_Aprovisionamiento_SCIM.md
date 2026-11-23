# Práctica 4. Aprovisionamiento automático mediante SCIM 2.0

**Módulo 3 · Aprovisionamiento automático mediante SCIM 2.0** · Duración aproximada: **100 minutos**

## Objetivos

Al terminar la práctica podrás:

- Probar un endpoint SCIM 2.0 con PowerShell y leer sus respuestas.
- Configurar el aprovisionamiento de Microsoft Entra hacia una aplicación fuera de la galería.
- Ajustar **attribute mappings** (directos, constantes y expresiones), el **matching attribute** y **scoping filters**.
- Probar altas, cambios, desactivaciones y usuarios fuera de alcance con **Provision on demand**.
- Ejecutar el ciclo inicial y analizar los **provisioning logs** junto con el registro del endpoint.

## Antes de empezar

| Requisito | Cómo comprobarlo |
|---|---|
| Práctica 2 terminada | La aplicación **Portal de Proveedores (Lab)** existe con DYN-Compras, GRP-Compras-Jefes y GRP-Logistica asignados |
| URL y token del endpoint SCIM | Los entregó soporte: `https://scim-labXX.azurewebsites.net/scim/v2` y un token |

> **Cómo usar esta guía.** Cada paso tiene la acción, la explicación de las opciones y el resultado esperado. Mantén abierta en una pestaña la página de registro del endpoint: es la "vista de la aplicación" y muestra cada solicitud que envía Entra.

**Archivos que se modifican en esta práctica**

| Archivo (en `C:\Curso\recursos`) | Qué haces |
|---|---|
| `scripts\prueba-scim.ps1` | Lo creas en la Tarea 1 para probar el endpoint (archivo nuevo) |
| [`datos\mis-datos.txt`](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/datos/mis-datos.txt) | Registras la URL y el token del endpoint |

---

## Contexto

El fabricante del portal de proveedores ofrece un endpoint SCIM 2.0. Contoso quiere que:

| Requisito | Configuración |
|---|---|
| Solo compradores y personal de logística tengan cuenta en el portal | Alcance por asignación + scoping filter por departamento |
| La cuenta se cree con nombre, correo, puesto, departamento y número de empleado | Attribute mappings |
| El nombre visible tenga el formato "Nombre Apellido" | Expresión `Join` |
| Se informe la organización "Contoso" | Mapping constante |
| La cuenta se **desactive** (no se borre) cuando la persona sale o pierde el acceso | Comportamiento predeterminado: `active = false` |
| Un error de configuración no desactive cuentas en masa | Prevención de eliminaciones accidentales |

---

## Tarea 1. Probar el endpoint SCIM

**Paso 1.1.** Copia la URL y el token en [`mis-datos.txt`](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/datos/mis-datos.txt). En Edge abre:

- `https://scim-labXX.azurewebsites.net/registro?token=<tu-token>` (solicitudes recibidas)
- `https://scim-labXX.azurewebsites.net/cuentas?token=<tu-token>` (usuarios y grupos que tiene la "aplicación")

Ambas páginas están vacías.

**Paso 1.2.** En VS Code crea `C:\Curso\recursos\scripts\prueba-scim.ps1` con este contenido:

```powershell
# Práctica 4. Prueba del endpoint SCIM como lo usará Microsoft Entra
param(
    [Parameter(Mandatory)][string]$Url,     # https://scim-labXX.azurewebsites.net/scim/v2
    [Parameter(Mandatory)][string]$Token
)
$h = @{ Authorization = "Bearer $Token" }

# 1. Sin token: el endpoint debe rechazar la solicitud
try { Invoke-RestMethod "$Url/Users" | Out-Null }
catch { "1. Sin token -> HTTP $([int]$_.Exception.Response.StatusCode)" }

# 2. Capacidades del servidor
$spc = Invoke-RestMethod "$Url/ServiceProviderConfig" -Headers $h
"2. PATCH soportado: $($spc.patch.supported) | Filtros: $($spc.filter.supported)"

# 3. Búsqueda por userName, igual que la que hace Entra antes de crear
$r = Invoke-RestMethod "$Url/Users?filter=userName eq `"prueba.manual@contoso.com`"" -Headers $h
"3. Coincidencias: $($r.totalResults)"

# 4. Alta, desactivación y baja de un usuario de prueba
$cuerpo = @{
    schemas  = @("urn:ietf:params:scim:schemas:core:2.0:User")
    userName = "prueba.manual@contoso.com"
    active   = $true
    name     = @{ givenName = "Prueba"; familyName = "Manual" }
} | ConvertTo-Json -Depth 5
$u = Invoke-RestMethod "$Url/Users" -Method Post -Headers $h -Body $cuerpo -ContentType "application/scim+json"
"4a. Creado con id $($u.id)"
$patch = @{
    schemas    = @("urn:ietf:params:scim:api:messages:2.0:PatchOp")
    Operations = @(@{ op = "Replace"; path = "active"; value = $false })
} | ConvertTo-Json -Depth 5
$u2 = Invoke-RestMethod "$Url/Users/$($u.id)" -Method Patch -Headers $h -Body $patch -ContentType "application/scim+json"
"4b. active = $($u2.active)"
Invoke-RestMethod "$Url/Users/$($u.id)" -Method Delete -Headers $h | Out-Null
"4c. Eliminado"
```

**Paso 1.3.** Ejecútalo en PowerShell 7:

```powershell
cd C:\Curso\recursos\scripts
./prueba-scim.ps1 -Url https://scim-lab01.azurewebsites.net/scim/v2 -Token <tu-token>
```

Salida esperada:

```text
1. Sin token -> HTTP 401
2. PATCH soportado: True | Filtros: True
3. Coincidencias: 0
4a. Creado con id 5b1f0c7e-2d3a-4e6b-9f10-7a8c9d0e1f23
4b. active = False
4c. Eliminado
```

| Operación SCIM | Código esperado | Qué demuestra |
|---|---|---|
| Sin `Authorization` | 401 | El endpoint exige el token portador |
| `GET /Users?filter=userName eq "..."` | 200 con `totalResults: 0` | La búsqueda vacía no es un error (no debe responder 404) |
| `POST /Users` | 201 con `id` | El servidor genera el `id` que Entra guardará |
| `PATCH ... active=false` | 200 | Desactivación sin borrar |
| `DELETE /Users/{id}` | 204 | Baja definitiva |

Recarga la página `/registro`: aparecen las cinco solicitudes con su método, ruta, estado y cuerpo.

---

## Tarea 2. Conectar Entra con el endpoint

**Paso 2.1.** Abre **Enterprise apps › Portal de Proveedores (Lab) › Provisioning** y selecciona **Get started** (o **New configuration**, según la versión del portal):

| Campo | Valor | Explicación |
|---|---|---|
| Provisioning Mode | **Automatic** | Entra administra el ciclo de vida de las cuentas |
| Tenant URL | `https://scim-labXX.azurewebsites.net/scim/v2` | URL base: Entra agrega `/Users` y `/Groups` |
| Secret Token | tu token | Se envía como `Authorization: Bearer <token>` |

**Paso 2.2.** Selecciona **Test Connection**. Resultado esperado: "The supplied credentials are authorized to enable provisioning". En `/registro` verás una solicitud como:

```text
GET  /Users?filter=userName eq "a1b2c3d4-..."   200
```

Entra busca un usuario con un nombre aleatorio para comprobar que el endpoint responde y acepta el token. Selecciona **Save**.

---

## Tarea 3. Ajustar los attribute mappings

**Paso 3.1.** En **Mappings** selecciona **Provision Microsoft Entra ID Users**. Revisa la tabla de mappings predeterminados:

| Atributo de Entra | Atributo de la app (SCIM) | Observación |
|---|---|---|
| `userPrincipalName` | `userName` | **Matching precedence 1**: con este atributo Entra busca la cuenta antes de crearla |
| `Switch([IsSoftDeleted], , "False", "True", "True", "False")` | `active` | Convierte "eliminado o fuera de alcance" en `active = false` |
| `displayName` | `displayName` | Lo cambiarás por una expresión |
| `jobTitle` | `title` | |
| `mail` | `emails[type eq "work"].value` | |
| `givenName` / `surname` | `name.givenName` / `name.familyName` | |
| `employeeId` | `urn:...:enterprise:2.0:User:employeeNumber` | |
| `department` | `urn:...:enterprise:2.0:User:department` | |
| `manager` | `urn:...:enterprise:2.0:User:manager` | Referencia: Entra envía el `id` SCIM del jefe |

**Paso 3.2.** Selecciona el mapping de `displayName` y cámbialo:

| Campo | Valor | Efecto |
|---|---|---|
| Mapping type | **Expression** | El valor se calcula |
| Expression | `Join(" ", [givenName], [surname])` | "Ana López", aunque el `displayName` de Entra tenga otro formato |
| Target attribute | `displayName` | |
| Apply this mapping | Always | Se aplica al crear y en cada actualización |

Usa **Expression builder › Test expression** con `ana.lopez` para ver el resultado antes de guardar.

**Paso 3.3.** **Add New Mapping** con un valor constante:

| Campo | Valor |
|---|---|
| Mapping type | **Constant** |
| Constant Value | `Contoso` |
| Target attribute | `urn:ietf:params:scim:schemas:extension:enterprise:2.0:User:organization` |
| Apply this mapping | Always |

**Paso 3.4.** (Recomendado) Elimina los mappings que la aplicación no necesita: los de `addresses[...]`, `phoneNumbers[...]` y `preferredLanguage`. Enviar menos datos reduce errores y expone menos información personal.

**Paso 3.5.** En **Source Object Scope** agrega dos filtros (se combinan con **OR**):

| Filtro | Cláusula | Efecto |
|---|---|---|
| Scoping filter 1 "Compras" | `department` **EQUALS** `Compras` | Entran ana, luis y prueba.nube |
| Scoping filter 2 "Logística" | `department` **EQUALS** `Logística` | Entra pedro |

| Regla | Explicación |
|---|---|
| Cláusulas dentro de un filtro | Se combinan con AND |
| Filtros distintos | Se combinan con OR |
| Usuario que deja de cumplir el filtro | Se desactiva en la aplicación en el siguiente ciclo |

Selecciona **Save** en el filtro, en la página de mappings y confirma.

**Paso 3.6.** Vuelve a **Mappings** y abre **Provision Microsoft Entra ID Groups**. Deja **Enabled = Yes**: los grupos asignados también se crean en la aplicación, con sus miembros que estén en alcance.

---

## Tarea 4. Configurar el alcance y la protección

**Paso 4.1.** En **Settings**:

| Opción | Valor | Efecto |
|---|---|---|
| Send an email notification when a failure occurs | Activada, con tu cuenta | Aviso cuando el job entra en cuarentena |
| Prevent accidental deletion | Activada, umbral **10** | Si un ciclo va a desactivar o eliminar más de 10 cuentas, se detiene y espera aprobación (en producción el valor típico es mayor; aquí se usa 10 para el laboratorio) |
| Scope | **Sync only assigned users and groups** | Solo usuarios y grupos asignados a la enterprise app |

Selecciona **Save**.

**Paso 4.2.** Para probar un usuario asignado pero fuera del filtro, asigna directamente a `marta.ruiz` (Finanzas) en **Users and groups** con el rol **Comprador**.

---

## Tarea 5. Probar con Provision on demand

**Paso 5.1. Alta.** En **Provisioning › Provision on demand** busca `ana.lopez` y selecciona **Provision**.

Resultado esperado (cuatro pasos en verde):

```text
1. Import user ................................ Success
2. Determine if user is in scope ............... Success
3. Match user between source and target system  Success   (No matching user found -> se creará)
4. Perform action ............................. Success   Action: Create
```

En **4. Perform action › View details** verás los atributos enviados. En `/registro`:

```text
GET   /Users?filter=userName eq "ana.lopez@lab01.onmicrosoft.com"   200
POST  /Users                                                         201
```

| Paso | Qué evalúa Entra |
|---|---|
| Import user | Lee el usuario y sus atributos en Entra |
| Determine if user is in scope | Asignación + scoping filters |
| Match user | Busca en la aplicación con el matching attribute (`userName`) |
| Perform action | Create, Update, Disable u Other (sin cambios) |

**Paso 5.2. Fuera de alcance.** Provision on demand con `marta.ruiz`. Resultado esperado: el paso **Determine if user is in scope** indica que el usuario está **fuera de alcance** porque no cumple ningún scoping filter (`department = Finanzas`). No se envía nada a la aplicación.

**Paso 5.3. Cambio.** Provision on demand con `prueba.nube` (se crea). Después, en **Entra ID › Users › Prueba Nube › Edit properties › Job information**, escribe **Job title** = `Comprador Jr.` y guarda. Repite Provision on demand con `prueba.nube`.

Resultado esperado: **Action: Update**; en `/registro`:

```text
PATCH /Users/<id>   200   {"Operations":[{"op":"Replace","path":"title","value":"Comprador Jr."}], ...}
```

> Ana, Luis y Pedro vienen de Active Directory: sus atributos se cambian en AD (LAB-SRV01), no en Entra. Por eso esta prueba se hace con `prueba.nube`, que es solo de nube.

**Paso 5.4. Desactivación.** En **Users › Prueba Nube › Edit properties › Settings** desmarca **Account enabled** y guarda. Provision on demand con `prueba.nube`.

Resultado esperado: **Action: Disable**; en `/registro`, un `PATCH` con `"path":"active","value":"False"`. En `/cuentas`, `prueba.nube` aparece con `active = False`. Vuelve a habilitar la cuenta (Account enabled) al terminar.

**Paso 5.5. Grupo.** Provision on demand admite un grupo de hasta cinco miembros: busca `GRP-Logistica` y provisiónalo. En `/registro` verás la creación de `pedro.garcia` (si no existía), `POST /Groups` y un `PATCH /Groups/<id>` con `"op":"Add","path":"members"`.

---

## Tarea 6. Ciclo inicial y provisioning logs

**Paso 6.1.** En **Provisioning › Overview** selecciona **Start provisioning**. La sección **Current cycle status** muestra el **Initial cycle** y su avance. En el laboratorio termina en pocos minutos; selecciona **Refresh** para actualizar.

| Concepto | Explicación |
|---|---|
| Ciclo inicial | Evalúa **todos** los usuarios y grupos en alcance |
| Ciclos incrementales | Después, aproximadamente cada 40 minutos, solo procesan cambios |
| Provision on demand | No espera al ciclo: útil para probar y para casos urgentes |

**Paso 6.2.** Cuando el ciclo termine, abre `/cuentas`. Resultado esperado:

| Usuarios | Grupos |
|---|---|
| ana.lopez, luis.mendez, pedro.garcia, prueba.nube | DYN-Compras, GRP-Compras-Jefes, GRP-Logistica |

`marta.ruiz` no aparece (fuera de alcance) y `carla.diaz` tampoco (no asignada).

**Paso 6.3.** Abre **Provisioning logs** (en la aplicación) y filtra por **Status**:

| Filtro | Qué deberías ver |
|---|---|
| Success | Create de los usuarios y grupos; Update de los que ya existían por Provision on demand |
| Skipped | `marta.ruiz` con motivo de alcance; usuarios sin cambios |
| Failure | Ninguno (si aparece, abre **Troubleshooting and Recommendations**) |

Abre un registro **Create** y revisa **Modified Properties**: valores enviados de `displayName` ("Ana López"), `organization` ("Contoso") y `employeeNumber`.

**Paso 6.4.** Prueba el ciclo incremental: quita la asignación de `marta.ruiz` en **Users and groups** (ya no se necesita) y cambia el **Job title** de `prueba.nube` a `Comprador`. No uses Provision on demand. Después del siguiente ciclo incremental (hasta 40 minutos) verás el `PATCH` en `/registro`. Continúa con otras tareas mientras tanto.

> **Reto opcional (aprovisionamiento entrante por API).** En **Enterprise apps › New application** busca **API-driven provisioning to Microsoft Entra ID**, créala, configura **Provisioning Mode = Automatic** e inicia el aprovisionamiento. Copia el **Object ID** de la aplicación y el **Job ID** (Provisioning › Overview › View technical information). Edita [`datos\lote-rrhh.json`](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/datos/lote-rrhh.json) para usar tu dominio y ejecuta [`./carga-rrhh.ps1 -ServicePrincipalId <object-id> -JobId <job-id>`](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/scripts/carga-rrhh.ps1). Se crean Sofía Herrera (Compras) y Raúl Torres (Finanzas) en Entra; Sofía entra a `DYN-Compras` y, en el siguiente ciclo, al portal de proveedores. Elimina ambos usuarios al terminar.

---

## Resultado esperado

| Comprobación | Resultado |
|---|---|
| `prueba-scim.ps1` | 401 sin token; 201, 200 y 204 en alta, desactivación y baja |
| Test Connection | Credenciales autorizadas |
| Provision on demand | Create (ana), fuera de alcance (marta), Update y Disable (prueba.nube), grupo GRP-Logistica |
| Ciclo inicial | 4 usuarios y 3 grupos en `/cuentas` |
| Provisioning logs | Sin fallas; marta en Skipped |

**Lista de verificación**

- [ ] Probé el endpoint con PowerShell y entiendo cada código HTTP.
- [ ] Configuré Tenant URL y token, y la conexión fue exitosa.
- [ ] Ajusté mappings (expresión, constante) y scoping filters con OR.
- [ ] Configuré el umbral de eliminaciones accidentales y el alcance por asignación.
- [ ] Probé alta, fuera de alcance, cambio, desactivación y grupo con Provision on demand.
- [ ] Ejecuté el ciclo inicial y revisé los provisioning logs.

## Archivos completos

**`C:\Curso\recursos\scripts\prueba-scim.ps1`**

```powershell
# Práctica 4. Prueba del endpoint SCIM como lo usará Microsoft Entra
param(
    [Parameter(Mandatory)][string]$Url,     # https://scim-labXX.azurewebsites.net/scim/v2
    [Parameter(Mandatory)][string]$Token
)
$h = @{ Authorization = "Bearer $Token" }

# 1. Sin token: el endpoint debe rechazar la solicitud
try { Invoke-RestMethod "$Url/Users" | Out-Null }
catch { "1. Sin token -> HTTP $([int]$_.Exception.Response.StatusCode)" }

# 2. Capacidades del servidor
$spc = Invoke-RestMethod "$Url/ServiceProviderConfig" -Headers $h
"2. PATCH soportado: $($spc.patch.supported) | Filtros: $($spc.filter.supported)"

# 3. Búsqueda por userName, igual que la que hace Entra antes de crear
$r = Invoke-RestMethod "$Url/Users?filter=userName eq `"prueba.manual@contoso.com`"" -Headers $h
"3. Coincidencias: $($r.totalResults)"

# 4. Alta, desactivación y baja de un usuario de prueba
$cuerpo = @{
    schemas  = @("urn:ietf:params:scim:schemas:core:2.0:User")
    userName = "prueba.manual@contoso.com"
    active   = $true
    name     = @{ givenName = "Prueba"; familyName = "Manual" }
} | ConvertTo-Json -Depth 5
$u = Invoke-RestMethod "$Url/Users" -Method Post -Headers $h -Body $cuerpo -ContentType "application/scim+json"
"4a. Creado con id $($u.id)"
$patch = @{
    schemas    = @("urn:ietf:params:scim:api:messages:2.0:PatchOp")
    Operations = @(@{ op = "Replace"; path = "active"; value = $false })
} | ConvertTo-Json -Depth 5
$u2 = Invoke-RestMethod "$Url/Users/$($u.id)" -Method Patch -Headers $h -Body $patch -ContentType "application/scim+json"
"4b. active = $($u2.active)"
Invoke-RestMethod "$Url/Users/$($u.id)" -Method Delete -Headers $h | Out-Null
"4c. Eliminado"
```

**[`C:\Curso\recursos\datos\mis-datos.txt`](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/datos/mis-datos.txt)** (sección del endpoint)

```text
Endpoint SCIM (Práctica 4)
  Tenant URL .............................. https://scim-lab01.azurewebsites.net/scim/v2
  Token ................................... (el que entregó soporte)
```

**Configuración final del aprovisionamiento en Entra**

| Sección | Configuración |
|---|---|
| Admin Credentials | Tenant URL del endpoint y Secret Token |
| Mappings de usuarios | `displayName` = `Join(" ", [givenName], [surname])`; constante `Contoso` → `organization`; sin `addresses`, `phoneNumbers` ni `preferredLanguage`; matching `userPrincipalName` ↔ `userName` |
| Scoping filters | `department EQUALS Compras` OR `department EQUALS Logística` |
| Mappings de grupos | Habilitados |
| Settings | Notificación por correo; prevención de eliminaciones con umbral 10; Sync only assigned users and groups |
| Estado | Provisioning Status = On |

## Problemas comunes

| Síntoma | Causa | Solución |
|---|---|---|
| Test Connection falla con 401 | Token incorrecto o con espacios | Copia el token de nuevo, sin espacios ni comillas |
| Test Connection falla sin código | URL incorrecta o App Service detenido | Abre la URL raíz del endpoint en Edge; debe responder |
| `prueba-scim.ps1`: "No se puede enlazar el argumento" | Falta `-Url` o `-Token` | Pasa ambos parámetros |
| Provision on demand: usuario "out of scope" inesperado | El valor del departamento no coincide exactamente (acentos, espacios) | Revisa el atributo del usuario y la cláusula del filtro |
| `409 Conflict` al crear | La cuenta ya existe en la aplicación con el mismo userName | Entra la vinculará si el matching la encuentra; revisa mayúsculas y el atributo de coincidencia |
| No se puede editar el puesto de ana | Usuario sincronizado desde AD | Cámbialo en AD (LAB-SRV01) o usa `prueba.nube` |
| El cambio no llega a la aplicación | Aún no corre el ciclo incremental | Espera o usa Provision on demand |
| El job aparece en cuarentena | La mayoría de las operaciones falló (token o endpoint) | Corrige la causa y usa **Restart provisioning** |
