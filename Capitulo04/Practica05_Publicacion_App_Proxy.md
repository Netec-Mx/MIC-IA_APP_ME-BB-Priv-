# Práctica 5. Publicación segura de una aplicación privada

**Módulo 4 · Acceso seguro a aplicaciones privadas con Microsoft Entra application proxy** · Duración aproximada: **70 minutos**

## Objetivos

Al terminar la práctica podrás:

- Verificar el estado del **private network connector** y su connector group.
- Comprobar que las aplicaciones privadas no son accesibles desde Internet.
- Publicar aplicaciones internas con **application proxy** y **preautenticación** de Microsoft Entra.
- Restringir el acceso por asignación y exigir **MFA** con acceso condicional.
- Validar el acceso desde una red externa y leer la evidencia en los sign-in logs.

## Antes de empezar

| Requisito | Cómo comprobarlo |
|---|---|
| Práctica 1 terminada | MFA registrada para ana, luis, marta y pedro |
| IP pública de LAB-SRV01 | Está en la hoja de datos que entregó soporte |
| Conexión a LAB-SRV01 | Desde LAB-CLIENT: `mstsc /v:<ip-publica-lab-srv01>` con `CONTOSO\labadmin` |

> **Cómo usar esta guía.** Cada paso tiene la acción, la explicación de las opciones y el resultado esperado. LAB-CLIENT representa la casa del empleado: **todas** las pruebas de acceso se hacen desde LAB-CLIENT, en ventanas InPrivate nuevas.

**Archivos que se modifican en esta práctica**

| Archivo | Qué haces |
|---|---|
| `C:\Curso\recursos\datos\mis-datos.txt` (LAB-CLIENT) | Registras las URL externas de las dos aplicaciones |

En Entra creas dos aplicaciones publicadas (**ERP heredado** e **Intranet RR. HH.**) y una política de acceso condicional; la configuración final está en la sección **Configuración final en Entra**.

---

## Contexto

En LAB-SRV01 (centro de datos de Contoso) hay dos sitios IIS que hoy solo funcionan dentro de la red:

| Aplicación | URL interna | Autenticación propia | SSO que se configurará |
|---|---|---|---|
| ERP heredado | `http://erp.contoso.local` | Ninguna: lee la identidad de encabezados HTTP | Encabezados (Práctica 6) |
| Intranet RR. HH. | `http://hr.contoso.local` | Autenticación integrada de Windows | Kerberos Constrained Delegation (Práctica 6) |

En esta práctica las publicas para que los empleados entren desde casa, sin VPN, sin abrir puertos de entrada y con MFA.

```text
LAB-CLIENT (casa) --HTTPS--> Entra + application proxy (nube) <==salida 443== conector (LAB-SRV01) --HTTP--> IIS
```

---

## Tarea 1. Verificar el conector

**Paso 1.1.** En el Microsoft Entra admin center abre **Global Secure Access › Connect › Connectors** (también disponible en **Entra ID › Enterprise apps › Application proxy**).

| Columna | Valor esperado | Explicación |
|---|---|---|
| Connector group | `CG-LAB` | Grupo creado por soporte; las aplicaciones se asignan a grupos, no a conectores |
| Connector | `LAB-SRV01` | Servidor donde corre el agente |
| Status | **Active** | El conector mantiene su conexión saliente con el servicio |
| Version | Versión vigente | Se actualiza sola mientras el servicio Updater esté en ejecución |

**Paso 1.2.** Conéctate por RDP a LAB-SRV01 y, en PowerShell como administrador, revisa los servicios:

```powershell
Get-Service WAPCsvc, WAPCUpdaterSvc | Format-Table Name, DisplayName, Status
```

Salida esperada:

```text
Name           DisplayName                                         Status
----           -----------                                         ------
WAPCsvc        Microsoft Entra private network connector           Running
WAPCUpdaterSvc Microsoft Entra private network connector updater   Running
```

---

## Tarea 2. Comprobar que las aplicaciones son privadas

**Paso 2.1.** En LAB-SRV01 confirma que ambos sitios funcionan dentro de la red:

```powershell
(Invoke-WebRequest http://erp.contoso.local -UseBasicParsing).StatusCode
(Invoke-WebRequest http://hr.contoso.local -UseDefaultCredentials -UseBasicParsing).Content
```

Resultado esperado: `200` y el HTML de la intranet con `Usuario: CONTOSO\labadmin`.

**Paso 2.2.** En LAB-CLIENT abre Edge y escribe `http://hr.contoso.local` y `http://erp.contoso.local`.

Resultado esperado: **No se puede acceder a este sitio** (el nombre no existe fuera de la red de Contoso y LAB-SRV01 no acepta tráfico HTTP desde Internet).

| Comprobación | Por qué importa |
|---|---|
| Sin DNS público ni puertos de entrada | La única forma de llegar será a través de application proxy, que exige autenticarse en Entra |
| El conector solo **sale** por 443 | No hay que publicar el servidor en una DMZ ni abrir el firewall de entrada |

---

## Tarea 3. Publicar el ERP heredado

**Paso 3.1.** Abre **Entra ID › Enterprise apps › New application › Add an on-premises application** y completa:

| Campo | Valor | Explicación |
|---|---|---|
| Name | `ERP heredado` | Nombre en el portal y en My Apps |
| Internal Url | `http://erp.contoso.local/` | URL que usa el conector; todo lo que esté debajo queda publicado |
| External Url | `https://erp-labXX.msappproxy.net/` (el portal propone el sufijo de tu tenant) | URL pública. Con un dominio propio verificado se podría usar, por ejemplo, `https://erp.contoso.com` |
| Pre Authentication | **Microsoft Entra ID** | El usuario debe autenticarse en Entra antes de llegar a la red |
| Connector Group | `CG-LAB` | Grupo de conectores que atenderá la aplicación |

En **Additional settings** deja:

| Opción | Valor | Efecto |
|---|---|---|
| Backend Application Timeout | Default | 85 segundos; "Long" amplía a 180 para aplicaciones lentas |
| Use HTTP-Only Cookie | Yes | El navegador no expone la cookie de sesión del proxy a scripts |
| Use Secure Cookie | Yes | La cookie solo viaja por HTTPS |
| Use Persistent Cookie | No | La sesión termina al cerrar el navegador |
| Translate URLs In Headers | Yes | Cambia `erp.contoso.local` por la URL externa en redirecciones |
| Translate URLs In Application Body | No | Solo se necesita si el HTML contiene enlaces internos fijos |

Selecciona **Add**. Copia la **External Url** en `mis-datos.txt`.

**Paso 3.2.** En **Users and groups** asigna `GRP-Logistica` y `DYN-Compras` (Default Access). En **Properties** confirma **Assignment required = Yes**.

**Paso 3.3.** En LAB-CLIENT abre una ventana InPrivate, entra a la External Url e inicia sesión con `ana.lopez`.

Resultado esperado: la página **ERP heredado - encabezados recibidos** con la lista de encabezados HTTP que llegaron al servidor (`Host`, `User-Agent`, `X-Forwarded-For`, entre otros). Todavía **no** aparece `X-User`: el SSO por encabezados se configura en la Práctica 6.

**Paso 3.4.** Repite con `marta.ruiz`. Resultado esperado: después de autenticarse, Entra muestra **AADSTS50105** (no está asignada). La solicitud nunca llegó a LAB-SRV01.

---

## Tarea 4. Publicar la intranet de RR. HH.

**Paso 4.1.** Crea otra aplicación con **Add an on-premises application**:

| Campo | Valor |
|---|---|
| Name | `Intranet RR. HH.` |
| Internal Url | `http://hr.contoso.local/` |
| External Url | `https://intranetrrhh-labXX.msappproxy.net/` |
| Pre Authentication | Microsoft Entra ID |
| Connector Group | `CG-LAB` |

Deja las demás opciones como en el Paso 3.1, selecciona **Add** y copia la External Url en `mis-datos.txt`.

**Paso 4.2.** Asigna `DYN-Compras` y `GRP-RRHH`.

**Paso 4.3.** Desde LAB-CLIENT (InPrivate) entra a la External Url con `ana.lopez`.

Resultado esperado: Entra autentica a Ana, pero después el navegador **pide usuario y contraseña de Windows** o muestra un error **401**. La intranet exige autenticación integrada de Windows (Kerberos/NTLM) y application proxy no la transmite desde el navegador: hace falta configurar **Kerberos Constrained Delegation** (Práctica 6). Cierra la ventana.

| Aplicación | Resultado sin SSO | Motivo |
|---|---|---|
| ERP heredado | Página visible | El ERP no autentica; confía en lo que llega |
| Intranet RR. HH. | Pide credenciales de Windows o 401 | IIS exige Windows Authentication |

---

## Tarea 5. Exigir MFA con acceso condicional

**Paso 5.1.** Abre **Entra ID › Conditional Access › Policies › New policy**:

| Sección | Valor | Explicación |
|---|---|---|
| Name | `LAB - MFA aplicaciones publicadas` | |
| Users › Include | All users | |
| Users › Exclude | Tu cuenta `participante@...` | Buena práctica: excluir una cuenta de emergencia para no bloquear la administración |
| Target resources › Include | Select resources › `ERP heredado` y `Intranet RR. HH.` | La política solo aplica a las aplicaciones publicadas |
| Grant | Grant access › **Require multifactor authentication** | |
| Enable policy | **On** | En producción se recomienda iniciar en **Report-only** |

Selecciona **Create**.

**Paso 5.2.** Desde LAB-CLIENT (InPrivate) entra al ERP con `pedro.garcia`. Resultado esperado: después de la contraseña, Entra pide la aprobación en **Microsoft Authenticator**; al aprobar, aparece la página del ERP.

**Paso 5.3.** En **Entra ID › Monitoring & health › Sign-in logs** abre el inicio de sesión de Pedro en **ERP heredado**:

| Pestaña | Valor esperado |
|---|---|
| Basic info | Status: Success; Application: ERP heredado |
| Authentication Details | Password + Mobile app notification (o el método que registraste) |
| Conditional Access | `LAB - MFA aplicaciones publicadas`: **Success** |

Abre también el intento de `marta.ruiz` (Tarea 3): Status **Failure**, código **50105**.

> **Reto opcional.** Cambia temporalmente **Pre Authentication** del ERP a **Passthrough** y entra a la External Url desde una ventana InPrivate: la página aparece **sin iniciar sesión**. ¿Qué riesgo representa para una aplicación que confía en encabezados? Regresa el valor a **Microsoft Entra ID** al terminar.

---

## Resultado esperado

| Prueba | Resultado |
|---|---|
| Conector LAB-SRV01 | Active, grupo CG-LAB; servicios en Running |
| Acceso directo desde LAB-CLIENT | No resuelve ni responde |
| ERP con `ana.lopez` / `pedro.garcia` | MFA → página de encabezados (sin `X-User`) |
| ERP con `marta.ruiz` | AADSTS50105 después de autenticarse |
| Intranet con `ana.lopez` | Autenticación en Entra correcta; luego pide credenciales de Windows o 401 (se resuelve en la Práctica 6) |
| Sign-in logs | Política `LAB - MFA aplicaciones publicadas` en Success |

**Lista de verificación**

- [ ] Verifiqué el conector en el portal y sus servicios en LAB-SRV01.
- [ ] Comprobé que las aplicaciones no son accesibles directamente desde fuera.
- [ ] Publiqué el ERP y la intranet con preautenticación de Entra.
- [ ] Probé un usuario asignado y uno no asignado.
- [ ] Creé la política de acceso condicional y la vi aplicada en los sign-in logs.

## Archivos completos

**`C:\Curso\recursos\datos\mis-datos.txt`** (sección de application proxy)

```text
Application proxy (Prácticas 5 y 6)
  URL externa de la intranet .............. https://intranetrrhh-lab01.msappproxy.net/
  URL externa del ERP ..................... https://erp-lab01.msappproxy.net/
```

**Configuración final en Entra**

| Elemento | Configuración |
|---|---|
| ERP heredado | Internal `http://erp.contoso.local/`; External `https://erp-labXX.msappproxy.net/`; Pre Authentication Microsoft Entra ID; CG-LAB; asignados GRP-Logistica y DYN-Compras |
| Intranet RR. HH. | Internal `http://hr.contoso.local/`; External `https://intranetrrhh-labXX.msappproxy.net/`; Pre Authentication Microsoft Entra ID; CG-LAB; asignados DYN-Compras y GRP-RRHH |
| Acceso condicional | `LAB - MFA aplicaciones publicadas`: todos los usuarios excepto la cuenta del participante; ambas aplicaciones; Require MFA; On |

## Problemas comunes

| Síntoma | Causa | Solución |
|---|---|---|
| El conector aparece **Inactive** | Servicio detenido o salida 443 bloqueada | En LAB-SRV01: `Start-Service WAPCsvc`; si persiste, avisa a soporte |
| "Bad Gateway" o error de conector al abrir la External Url | El conector no resuelve `erp.contoso.local` o el sitio está detenido | En LAB-SRV01 prueba `Invoke-WebRequest http://erp.contoso.local` y revisa IIS |
| "This corporate app can't be accessed" | La aplicación no tiene connector group o el grupo no tiene conectores activos | Revisa **Connector Group** en Application proxy |
| No pide MFA | La política está en Report-only, el usuario está excluido o se reutilizó la sesión | Revisa la política y usa una ventana InPrivate nueva |
| Te bloqueaste en el portal | Política aplicada a todas las aplicaciones sin exclusión | Entra con la cuenta excluida y corrige **Target resources** |
| La External Url no carga después de crearla | La publicación tarda unos minutos | Espera y reintenta |
