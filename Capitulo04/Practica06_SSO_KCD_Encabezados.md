# Práctica 6. Configuración de SSO para una aplicación heredada

**Módulo 4 · Acceso seguro a aplicaciones privadas con Microsoft Entra application proxy** · Duración aproximada: **60 minutos**

## Objetivos

Al terminar la práctica podrás:

- Registrar el **SPN** de una aplicación web y configurar **Kerberos Constrained Delegation basada en recursos (RBCD)** para el conector.
- Configurar SSO con **Integrated Windows Authentication** y elegir la **Delegated Login Identity**.
- Configurar SSO por **encabezados HTTP** con atributos de Microsoft Entra.
- Seguir el flujo Entra → conector → AD DS → aplicación en los registros y explicar los riesgos del SSO por encabezados.

## Antes de empezar

| Requisito | Cómo comprobarlo |
|---|---|
| Práctica 5 terminada | ERP heredado e Intranet RR. HH. publicados; política de MFA activa |
| RDP a LAB-SRV01 con `CONTOSO\labadmin` | Desde LAB-CLIENT: `mstsc /v:<ip-publica-lab-srv01>` |

> **Cómo usar esta guía.** Los comandos de Active Directory se ejecutan en **LAB-SRV01** (PowerShell como administrador); las pruebas de acceso, en **LAB-CLIENT** con ventanas InPrivate nuevas.

**Archivos que se modifican en esta práctica**

| Archivo | Qué haces |
|---|---|
| `C:\Curso\kcd-intranet.ps1` (LAB-SRV01) | Lo creas con los comandos de SPN y delegación, para documentar el cambio (archivo nuevo) |

En Entra cambias el SSO de **Intranet RR. HH.** (Windows Integrated Authentication) y de **ERP heredado** (Header-based).

---

## Contexto

| Aplicación | Cómo autentica | Qué hará el conector |
|---|---|---|
| Intranet RR. HH. | IIS con Windows Authentication (Negotiate), sitio ejecutado por `CONTOSO\svc-hr-iis` | Pedir a AD un ticket Kerberos **a nombre del usuario** para `HTTP/hr.contoso.local` y presentarlo a IIS |
| ERP heredado | Lee `X-User`, `X-Email` y `X-Dept` | Agregar esos encabezados con los datos del usuario autenticado en Entra |

```text
Usuario ─► Entra (MFA) ─► conector LAB-SRV01$ ─S4U2Self/S4U2Proxy─► KDC ─► ticket para HTTP/hr.contoso.local ─► IIS
```

---

## Tarea 1. Registrar el SPN y la delegación (LAB-SRV01)

**Paso 1.1.** En LAB-SRV01 crea `C:\Curso\kcd-intranet.ps1` (crea la carpeta si no existe) con este contenido y ejecútalo en PowerShell como administrador:

```powershell
# Práctica 6. SPN y delegación Kerberos (RBCD) para la Intranet RR. HH.
Import-Module ActiveDirectory

# 1. SPN del sitio en la cuenta que ejecuta el grupo de aplicaciones
setspn -S HTTP/hr.contoso.local CONTOSO\svc-hr-iis
setspn -S HTTP/hr CONTOSO\svc-hr-iis

# 2. Comprobar que el SPN no está duplicado
setspn -Q HTTP/hr.contoso.local

# 3. RBCD: la cuenta del sitio acepta delegación desde la cuenta de equipo del conector
$conector = Get-ADComputer -Identity "LAB-SRV01"
Set-ADUser -Identity "svc-hr-iis" -PrincipalsAllowedToDelegateToAccount $conector

# 4. Verificar
Get-ADUser -Identity "svc-hr-iis" -Properties servicePrincipalName, PrincipalsAllowedToDelegateToAccount |
    Format-List Name, servicePrincipalName, PrincipalsAllowedToDelegateToAccount

# 5. Aplicar sin esperar: renovar los tickets del conector
klist purge -li 0x3e4
Restart-Service WAPCsvc
```

Salida esperada (resumen):

```text
Registering ServicePrincipalNames for CN=svc-hr-iis,CN=Users,DC=contoso,DC=local
        HTTP/hr.contoso.local
Updated object
...
CN=svc-hr-iis,CN=Users,DC=contoso,DC=local
        HTTP/hr
        HTTP/hr.contoso.local

Existing SPN found!

Name                                 : svc-hr-iis
servicePrincipalName                 : {HTTP/hr, HTTP/hr.contoso.local}
PrincipalsAllowedToDelegateToAccount : {CN=LAB-SRV01,OU=Domain Controllers,DC=contoso,DC=local}
```

| Comando | Explicación |
|---|---|
| `setspn -S` | Registra el SPN **verificando antes** que no exista en otra cuenta (`-A` no verifica) |
| `HTTP/hr.contoso.local` en `svc-hr-iis` | El sitio corre con esa cuenta y `useAppPoolCredentials = true`: IIS descifra los tickets con la clave de `svc-hr-iis` |
| `PrincipalsAllowedToDelegateToAccount` | **RBCD**: la delegación se configura en el recurso (la cuenta del sitio), indicando qué cuentas pueden pedir tickets en nombre de usuarios |
| `klist purge -li 0x3e4` | Borra los tickets en caché de la sesión **NETWORK SERVICE**, con la que corre el conector |
| `Restart-Service WAPCsvc` | Reinicia el conector para que use los tickets nuevos |

> **Por qué RBCD.** En el laboratorio el conector está en el controlador de dominio; RBCD evita cambiar la configuración de delegación de la cuenta del DC. Con conectores en servidores miembro también se puede usar la KCD clásica (pestaña **Delegation** de la cuenta del conector, "Use any authentication protocol").

---

## Tarea 2. SSO con Integrated Windows Authentication

**Paso 2.1.** En Entra abre **Enterprise apps › Intranet RR. HH. › Single sign-on** y elige **Windows Integrated Authentication**:

| Campo | Valor | Explicación |
|---|---|---|
| Internal Application SPN | `HTTP/hr.contoso.local` | El SPN para el que el conector pedirá el ticket; debe coincidir con el registrado en AD |
| Delegated Login Identity | **User principal name** | El conector pide el ticket para el UPN del usuario de Entra; en el laboratorio coincide con el UPN de AD (`ana.lopez@labXX.onmicrosoft.com`) |

Selecciona **Save**.

**Paso 2.2.** Desde LAB-CLIENT (InPrivate) entra a la External Url de la intranet con `ana.lopez` y aprueba la MFA.

Resultado esperado (ya no pide credenciales de Windows):

```text
Intranet RR. HH.
Usuario: CONTOSO\alopez
Metodo: Negotiate
```

**Paso 2.3.** Repite con `carla.diaz` (GRP-RRHH): `Usuario: CONTOSO\cdiaz`.

**Paso 2.4.** Prueba con `prueba.nube` (está en DYN-Compras, asignado a la intranet). Resultado esperado: una página de error de application proxy que indica que no fue posible obtener el ticket Kerberos. `prueba.nube` **no existe en Active Directory**: KCD solo funciona para usuarios con cuenta en AD DS.

**Paso 2.5.** Cambia **Delegated Login Identity** a **On-premises SAM account name**, guarda y prueba otra vez con `ana.lopez` (ventana nueva). Funciona igual: el conector pide ahora el ticket para `alopez`.

| Opción de Delegated Login Identity | Identidad que usa el conector | Cuándo usarla |
|---|---|---|
| User principal name | `ana.lopez@labXX.onmicrosoft.com` | UPN igual en Entra y en AD |
| On-premises user principal name | UPN sincronizado desde AD | UPN de Entra distinto del local |
| On-premises SAM account name | `alopez` | Aplicaciones que esperan el nombre clásico; un solo dominio |
| Username part of user principal name | `ana.lopez` | Aplicaciones no Windows con nombres cortos |

Regresa la opción a **User principal name** y guarda.

---

## Tarea 3. SSO por encabezados para el ERP

**Paso 3.1.** En **Enterprise apps › ERP heredado › Single sign-on** elige **Header-based** y agrega tres encabezados (**Add new header**):

| Name | Source | Source attribute | Explicación |
|---|---|---|---|
| `X-User` | Attribute | `user.onpremisessamaccountname` | Nombre de usuario de dominio (`alopez`), como lo espera el ERP |
| `X-Email` | Attribute | `user.mail` | Correo |
| `X-Dept` | Attribute | `user.department` | Departamento |

Selecciona **Save**.

**Paso 3.2.** Desde LAB-CLIENT (InPrivate) entra a la External Url del ERP con `pedro.garcia`.

Resultado esperado: además de los encabezados de la Práctica 5, la tabla muestra:

```text
X-User    pgarcia
X-Email   pedro.garcia@lab01.onmicrosoft.com
X-Dept    Logística
```

**Paso 3.3.** Repite con `ana.lopez`: `X-User = alopez`, `X-Dept = Compras`.

| Concepto | Explicación |
|---|---|
| Origen de los valores | Los mismos atributos y transformaciones disponibles para claims SAML |
| Alcance | Todas las rutas bajo la Internal Url reciben los mismos encabezados |
| Usuarios solo de nube | Funcionan, pero `X-User` queda vacío si el atributo de AD no existe (prueba con `prueba.nube` si quieres verlo) |

---

## Tarea 4. Riesgo de los encabezados

**Paso 4.1.** En LAB-SRV01 simula a alguien que llega **directamente** al servidor, sin pasar por el proxy:

```powershell
$r = Invoke-WebRequest http://erp.contoso.local -Headers @{ "X-User" = "administrador"; "X-Dept" = "Finanzas" } -UseBasicParsing
$r.Content -split "<tr>" | Select-String "X-"
```

Resultado esperado: el ERP muestra `X-User administrador`. La aplicación **no puede distinguir** un encabezado legítimo de uno falsificado.

| Control | Cómo mitiga el riesgo |
|---|---|
| Aislar la aplicación | Que solo acepte conexiones desde los servidores del conector (firewall de host o de red) |
| Filtrar encabezados entrantes | Un componente delante de la app descarta `X-User` que no venga del proxy |
| Preautenticación siempre en Entra ID | Con Passthrough cualquiera llega al ERP sin autenticarse |
| Preferir KCD o SAML cuando la app lo soporte | La identidad viaja firmada o cifrada, no como texto |

---

## Tarea 5. Seguir el flujo en los registros

**Paso 5.1. Entra.** En **Sign-in logs** filtra **Application** = Intranet RR. HH. y abre el inicio de sesión de Ana: Status Success, MFA satisfecha por la política de la Práctica 5.

**Paso 5.2. Controlador de dominio.** En LAB-SRV01 busca los tickets de servicio emitidos para la intranet:

```powershell
Get-WinEvent -FilterHashtable @{ LogName = "Security"; Id = 4769 } -MaxEvents 200 |
    Where-Object { $_.Message -match "svc-hr-iis" } |
    Select-Object -First 3 TimeCreated, @{ n = "Detalle"; e = { ($_.Message -split "`n" | Select-String "Account Name|Service Name|Transited Services") -join " | " } } |
    Format-List
```

Resultado esperado (resumen): un evento **4769** con **Account Name** `alopez@CONTOSO.LOCAL` (o el UPN), **Service Name** `svc-hr-iis` y **Transited Services** con `LAB-SRV01$`: el conector obtuvo el ticket en nombre de Ana (S4U2Proxy).

**Paso 5.3. Conector.** En **Event Viewer › Applications and Services Logs** busca el registro **Admin** del conector. Si hubo errores de KCD (por ejemplo, en el Paso 2.4 con `prueba.nube`), aparecen ahí con su descripción.

Completa esta tabla con lo que observaste:

| Salto | Evidencia | Dónde la viste |
|---|---|---|
| Usuario → Entra | Inicio de sesión con MFA | Sign-in logs |
| Entra → conector | Solicitud entregada a CG-LAB | Página de la intranet cargada; registro Admin del conector |
| Conector → KDC | Evento 4769 con Transited Services | Registro Security de LAB-SRV01 |
| Conector → IIS | `Usuario: CONTOSO\alopez`, `Metodo: Negotiate` | Página de la intranet |

> **Reto opcional.** Elimina temporalmente la delegación (`Set-ADUser svc-hr-iis -PrincipalsAllowedToDelegateToAccount $null`), ejecuta `klist purge -li 0x3e4` y `Restart-Service WAPCsvc`, y prueba la intranet. Identifica el error en el registro del conector y restaura la delegación con el script.

---

## Resultado esperado

| Prueba | Resultado |
|---|---|
| Intranet con `ana.lopez` / `carla.diaz` | Sin solicitud de credenciales: `CONTOSO\alopez` / `CONTOSO\cdiaz`, método Negotiate |
| Intranet con `prueba.nube` | Error de KCD: el usuario no existe en AD DS |
| ERP con `pedro.garcia` | `X-User pgarcia`, `X-Email`, `X-Dept Logística` |
| Acceso directo con encabezado falso | El ERP acepta `X-User administrador`: riesgo demostrado |
| Evento 4769 | Ticket para `svc-hr-iis` con Transited Services `LAB-SRV01$` |

**Lista de verificación**

- [ ] Registré el SPN sin duplicados y configuré RBCD.
- [ ] Configuré Windows Integrated Authentication con el SPN y la identidad delegada.
- [ ] Comprobé por qué un usuario solo de nube no puede usar KCD.
- [ ] Configuré tres encabezados en el ERP y validé sus valores.
- [ ] Demostré el riesgo de falsificar encabezados y sus controles.
- [ ] Seguí el flujo en sign-in logs, en el evento 4769 y en el registro del conector.

## Archivos completos

**`C:\Curso\kcd-intranet.ps1`** (LAB-SRV01)

```powershell
# Práctica 6. SPN y delegación Kerberos (RBCD) para la Intranet RR. HH.
Import-Module ActiveDirectory

# 1. SPN del sitio en la cuenta que ejecuta el grupo de aplicaciones
setspn -S HTTP/hr.contoso.local CONTOSO\svc-hr-iis
setspn -S HTTP/hr CONTOSO\svc-hr-iis

# 2. Comprobar que el SPN no está duplicado
setspn -Q HTTP/hr.contoso.local

# 3. RBCD: la cuenta del sitio acepta delegación desde la cuenta de equipo del conector
$conector = Get-ADComputer -Identity "LAB-SRV01"
Set-ADUser -Identity "svc-hr-iis" -PrincipalsAllowedToDelegateToAccount $conector

# 4. Verificar
Get-ADUser -Identity "svc-hr-iis" -Properties servicePrincipalName, PrincipalsAllowedToDelegateToAccount |
    Format-List Name, servicePrincipalName, PrincipalsAllowedToDelegateToAccount

# 5. Aplicar sin esperar: renovar los tickets del conector
klist purge -li 0x3e4
Restart-Service WAPCsvc
```

**Configuración final en Entra**

| Aplicación | Single sign-on |
|---|---|
| Intranet RR. HH. | Windows Integrated Authentication · SPN `HTTP/hr.contoso.local` · Delegated Login Identity: User principal name |
| ERP heredado | Header-based · `X-User` = `user.onpremisessamaccountname` · `X-Email` = `user.mail` · `X-Dept` = `user.department` |

## Problemas comunes

| Síntoma | Causa | Solución |
|---|---|---|
| La intranet sigue pidiendo credenciales | El SSO de la aplicación no se guardó o el conector usa tickets viejos | Revisa Single sign-on; ejecuta `klist purge -li 0x3e4` y reinicia `WAPCsvc` |
| Error de application proxy sobre KCD | Delegación ausente, SPN distinto o usuario sin cuenta en AD | Verifica con `Get-ADUser svc-hr-iis -Properties PrincipalsAllowedToDelegateToAccount` y el SPN en Entra |
| `setspn -S` indica "Duplicate SPN found" | El SPN ya está en otra cuenta | Elimínalo de la otra cuenta con `setspn -D` antes de registrarlo |
| La página muestra `Metodo: NTLM` | IIS no pudo usar Kerberos | Revisa el SPN en `svc-hr-iis` y que `useAppPoolCredentials` esté habilitado |
| El ERP no muestra `X-User` | El encabezado no se guardó o el atributo está vacío | Revisa la configuración Header-based y el atributo del usuario |
| `X-User` vacío para un usuario | El usuario es solo de nube (no tiene `onpremisessamaccountname`) | Esperado; usa otro atributo o un usuario sincronizado |
| El evento 4769 no aparece | La auditoría de Kerberos no está habilitada o hay muchos eventos | Aumenta `-MaxEvents` o revisa la directiva de auditoría del DC |
