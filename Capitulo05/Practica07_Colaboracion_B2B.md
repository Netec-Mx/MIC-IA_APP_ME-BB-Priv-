# Práctica 7. Implementación de colaboración B2B

**Módulo 5 · Microsoft Entra External ID y federación de identidades externas** · Duración aproximada: **45 minutos**

## Objetivos

Al terminar la práctica podrás:

- Configurar quién puede invitar, qué ve un invitado y con qué dominios se colabora.
- Configurar **cross-tenant access** para confiar en la MFA de una organización socia.
- Invitar usuarios externos en lote con Microsoft Graph PowerShell.
- Dar acceso a invitados a una aplicación SAML y distinguir su identidad en los claims.
- Comprobar el canje (redemption) con tres tipos de identidad: otro tenant de Entra, cuenta Microsoft y código por correo.

## Antes de empezar

| Requisito | Cómo comprobarlo |
|---|---|
| Práctica 2 terminada | `Portal de Proveedores (Lab)` funciona con la aplicación de prueba en `https://localhost:5001` |
| Cuentas externas | Usuario `socioXX@fabrikamlab.onmicrosoft.com` (con MFA registrada en su tenant), buzón Outlook.com y cuenta de Gmail, con sus contraseñas |
| Aplicación de prueba en ejecución | `python app.py` en `C:\Curso\recursos\saml-sp` con `.venv` activo |

> **Cómo usar esta guía.** Cada paso tiene la acción, la explicación de las opciones y el resultado esperado. Las pruebas con usuarios externos se hacen en ventanas InPrivate nuevas.

**Archivos que se modifican en esta práctica**

| Archivo (en `C:\Curso\recursos`) | Qué haces |
|---|---|
| [`datos\invitados.csv`](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/datos/invitados.csv) | Escribes los correos de tus cuentas externas |
| [`datos\mis-datos.txt`](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/datos/mis-datos.txt) | Registras las cuentas externas |

---

## Contexto

Tres proveedores necesitan entrar al portal de proveedores de Contoso:

| Proveedor | Identidad | Cómo se autenticará |
|---|---|---|
| Fabrikam | Cuenta de su propio tenant de Microsoft Entra | En su tenant, con su MFA (Contoso confía en ella) |
| Proveedor Andes | Buzón de Outlook.com | Con su cuenta Microsoft (MSA) |
| Proveedor Sur | Cuenta de Gmail | Con un **código de un solo uso** enviado por correo |

El portal debe saber que son externos: el claim `perfil` llevará `PROVEEDOR`.

---

## Tarea 1. Configurar la colaboración externa

**Paso 1.1.** Abre **Entra ID › External Identities › External collaboration settings**:

| Sección | Valor | Efecto |
|---|---|---|
| Guest user access | **Guest user access is restricted to properties and memberships of their own directory objects** | Un invitado no puede listar usuarios ni grupos de Contoso |
| Guest invite settings | **Member users and users assigned to specific admin roles can invite guest users including guests with member permissions** | Los invitados no pueden invitar a otros |
| Enable guest self-service sign up via user flows | No | Solo se entra por invitación |
| Collaboration restrictions | **Allow invitations only to the specified domains** · `fabrikamlab.onmicrosoft.com`, `outlook.com`, `hotmail.com`, `gmail.com` | Cualquier invitación a otro dominio se rechaza |

Selecciona **Save**.

**Paso 1.2.** Abre **External Identities › All identity providers** y confirma:

| Proveedor | Estado | Explicación |
|---|---|---|
| Microsoft Entra ID | Configurado | Usuarios de otros tenants de Entra |
| Microsoft Account | Configurado | Cuentas personales de Microsoft |
| Email one-time passcode | **Enabled** | Respaldo para quien no tiene otra cuenta compatible |

---

## Tarea 2. Confiar en la MFA del tenant socio

**Paso 2.1.** Abre **External Identities › Cross-tenant access settings › Organizational settings › Add organization**, escribe `fabrikamlab.onmicrosoft.com` y selecciona **Add**.

**Paso 2.2.** En la fila de Fabrikam abre **Inbound access › Trust settings › Customize settings** y marca **Trust multifactor authentication from Microsoft Entra tenants**. Selecciona **Save**.

| Opción de confianza | Efecto |
|---|---|
| Trust multifactor authentication | Si el usuario ya hizo MFA en Fabrikam, el acceso condicional de Contoso la acepta |
| Trust compliant devices / hybrid joined devices | Igual, para las condiciones de dispositivo |

**Paso 2.3.** Crea una política para comprobarlo: **Conditional Access › New policy**:

| Sección | Valor |
|---|---|
| Name | `LAB - MFA socios en portal` |
| Users › Include | Guest or external users › **B2B collaboration guest users** · External Microsoft Entra organizations: **Select** › `fabrikamlab.onmicrosoft.com` |
| Target resources | `Portal de Proveedores (Lab)` |
| Grant | Require multifactor authentication |
| Enable policy | On |

---

## Tarea 3. Invitar a los usuarios externos

**Paso 3.1.** Edita [`datos\invitados.csv`](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/datos/invitados.csv) con tus cuentas (conserva el encabezado):

```text
correo,nombre,empresa
socio01@fabrikamlab.onmicrosoft.com,Socio Fabrikam 01,Fabrikam
externo.lab01@outlook.com,Proveedor Andes 01,Proveedor Andes
cuenta.lab01@gmail.com,Proveedor Sur 01,Proveedor Sur
```

**Paso 3.2.** En PowerShell 7 ejecuta:

```powershell
cd C:\Curso\recursos\scripts
./invitar-externos.ps1 -Csv ..\datos\invitados.csv
```

Salida esperada:

```text
Correo                                ObjectId                             Estado          EnlaceCanje
------                                --------                             ------          -----------
socio01@fabrikamlab.onmicrosoft.com   8b1d2c3e-...                         PendingAcceptance https://login.microsoftonline.com/redeem?...
externo.lab01@outlook.com             1f2e3d4c-...                         PendingAcceptance https://login.microsoftonline.com/redeem?...
cuenta.lab01@gmail.com                9a8b7c6d-...                         PendingAcceptance https://login.microsoftonline.com/redeem?...
```

| Elemento del script | Explicación |
|---|---|
| `New-MgInvitation` | Crea el usuario **Guest** y, con `SendInvitationMessage`, envía el correo de invitación |
| `InviteRedirectUrl` | A dónde llega el invitado después de canjear: My Apps de Contoso (`?tenantid=`) |
| `Update-MgUser -CompanyName` | Registra la empresa; sirve para reglas de grupos dinámicos y reportes |
| `New-MgGroupMember` | Agrega al invitado a `GRP-Proveedores` |
| Estado `PendingAcceptance` | El invitado aún no canjea la invitación |

**Paso 3.3.** En **Entra ID › Users** filtra **User type = Guest**. Revisa los tres invitados: **User principal name** con el formato `cuenta.lab01_gmail.com#EXT#@labXX.onmicrosoft.com` e **Invitation state = Pending acceptance**.

---

## Tarea 4. Dar acceso al portal

**Paso 4.1.** En **Enterprise apps › Portal de Proveedores (Lab) › Users and groups** asigna `GRP-Proveedores` con el rol **Comprador**.

**Paso 4.2.** En **Single sign-on › Attributes & Claims** edita el claim `perfil` y agrega una condición más (al final de la lista):

| Campo | Valor |
|---|---|
| User type | **External guests** |
| Scoped Groups | (ninguno) |
| Source / Value | Attribute / `"PROVEEDOR"` |

Guarda.

| Decisión | Explicación |
|---|---|
| NameID = `user.mail` (desde la Práctica 2) | Para un invitado, `mail` es su correo real; el UPN tendría el formato `#EXT#`, que el portal no reconocería |
| Condición por tipo de usuario | El portal distingue a proveedores de compradores internos sin grupos adicionales |

---

## Tarea 5. Probar el canje y el acceso

**Paso 5.1. Usuario de Fabrikam.** En una ventana InPrivate abre `https://localhost:5001`, selecciona **Iniciar sesión** y escribe `socio01@fabrikamlab.onmicrosoft.com`. Entra redirige al tenant de Fabrikam: inicia sesión con su contraseña y su MFA. La primera vez aparece **Review permissions** de Contoso: selecciona **Accept**.

Resultado esperado en la aplicación de prueba:

```text
NameID: socio01@fabrikamlab.onmicrosoft.com (emailAddress)
role = Comprador
perfil = PROVEEDOR
http://schemas.microsoft.com/identity/claims/identityprovider = https://sts.windows.net/<id-tenant-fabrikam>/
```

No se pidió una segunda MFA en Contoso: la política `LAB - MFA socios en portal` quedó satisfecha con la MFA de Fabrikam.

**Paso 5.2. Cuenta Microsoft.** En otra ventana InPrivate repite con `externo.lab01@outlook.com` (contraseña de la cuenta Microsoft). Resultado esperado: `identityprovider = live.com` y `perfil = PROVEEDOR`.

**Paso 5.3. Código por correo.** Repite con `cuenta.lab01@gmail.com`. Como no hay federación con Google configurada, Entra envía un **código de verificación** al correo: ábrelo en Gmail (en otra pestaña) y escríbelo. Resultado esperado: `identityprovider = mail`.

**Paso 5.4.** En **Entra ID › Users** filtra los invitados: los tres aparecen con **Invitation state = Accepted**. Abre uno y revisa **Identities** (el emisor de su identidad).

**Paso 5.5.** En **Sign-in logs** filtra **User type = Guest** (pestaña **User sign-ins (interactive)**). Abre el inicio de sesión del socio de Fabrikam:

| Campo | Valor esperado |
|---|---|
| Cross tenant access type | B2B collaboration |
| Home tenant ID | El tenant de Fabrikam |
| Conditional Access | `LAB - MFA socios en portal`: Success (MFA satisfecha por el tenant de origen) |

| Tipo de identidad | Emisor en Entra (`identityprovider`) | Dónde se autentica |
|---|---|---|
| Otro tenant de Entra | `https://sts.windows.net/<tenant>/` | En su organización, con sus políticas |
| Cuenta Microsoft | `live.com` | En la cuenta personal de Microsoft |
| Código por correo | `mail` | Código enviado al buzón, válido por un tiempo limitado |

> **Reto opcional (federación con Google).** En `https://console.cloud.google.com` (proyecto `entra-labXX`) configura la pantalla de consentimiento OAuth (tipo **External**, con tu cuenta como usuario de prueba) y crea un **OAuth client ID** de tipo **Web application** con estos **Authorized redirect URIs**: `https://login.microsoftonline.com`, `https://login.microsoftonline.com/te/<tenant-id>/oauth2/authresp` y `https://login.microsoftonline.com/te/labXX.onmicrosoft.com/oauth2/authresp`. En Entra, **All identity providers › Google**, escribe el Client ID y el Client secret. Invita una segunda cuenta de Gmail y comprueba que su `identityprovider` es `google.com`. (Los invitados que ya canjearon con código conservan ese método.)

---

## Resultado esperado

| Comprobación | Resultado |
|---|---|
| Colaboración externa | Restringida a cuatro dominios; invitados con acceso restringido |
| Cross-tenant access | Fabrikam con confianza en MFA |
| Invitados | Tres usuarios Guest en GRP-Proveedores, con empresa registrada, estado Accepted |
| Portal de proveedores | NameID = correo real; `role = Comprador`; `perfil = PROVEEDOR` |
| Identidades | Entra (Fabrikam), `live.com` y `mail` |
| Sign-in logs | B2B collaboration; MFA de Fabrikam aceptada por la política |

**Lista de verificación**

- [ ] Configuré la colaboración externa y la lista de dominios permitidos.
- [ ] Configuré cross-tenant access con Fabrikam y la confianza en MFA.
- [ ] Invité a tres usuarios con [`invitar-externos.ps1`](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/scripts/invitar-externos.ps1).
- [ ] Asigné GRP-Proveedores al portal y agregué la condición `PROVEEDOR`.
- [ ] Probé el canje con los tres tipos de identidad y lo comprobé en los sign-in logs.

## Archivos completos

**[`C:\Curso\recursos\datos\invitados.csv`](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/datos/invitados.csv)** (con tus correos)

```text
correo,nombre,empresa
socio01@fabrikamlab.onmicrosoft.com,Socio Fabrikam 01,Fabrikam
externo.lab01@outlook.com,Proveedor Andes 01,Proveedor Andes
cuenta.lab01@gmail.com,Proveedor Sur 01,Proveedor Sur
```

**[`C:\Curso\recursos\scripts\invitar-externos.ps1`](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/scripts/invitar-externos.ps1)** (se usa sin cambios)

```powershell
param(
    [Parameter(Mandatory)][string]$Csv,
    [string]$Grupo = "GRP-Proveedores",
    [switch]$SinCorreo
)

Connect-MgGraph -Scopes "User.Invite.All", "User.ReadWrite.All", "GroupMember.ReadWrite.All" -NoWelcome
$tenantId = (Get-MgContext).TenantId
$g = Get-MgGroup -Filter "displayName eq '$Grupo'"
if (-not $g) { throw "No existe el grupo $Grupo" }

foreach ($fila in Import-Csv $Csv) {
    $params = @{
        InvitedUserEmailAddress = $fila.correo
        InvitedUserDisplayName  = "$($fila.nombre) ($($fila.empresa))"
        InviteRedirectUrl       = "https://myapps.microsoft.com/?tenantid=$tenantId"
        SendInvitationMessage   = -not $SinCorreo
        InvitedUserMessageInfo  = @{ CustomizedMessageBody = "Bienvenido al portal de proveedores de Contoso." }
    }
    $inv = New-MgInvitation -BodyParameter $params
    Update-MgUser -UserId $inv.InvitedUser.Id -CompanyName $fila.empresa
    $miembros = (Get-MgGroupMember -GroupId $g.Id -All).Id
    if ($inv.InvitedUser.Id -notin $miembros) {
        New-MgGroupMember -GroupId $g.Id -DirectoryObjectId $inv.InvitedUser.Id
    }
    [pscustomobject]@{
        Correo = $fila.correo; ObjectId = $inv.InvitedUser.Id
        Estado = $inv.Status; EnlaceCanje = $inv.InviteRedeemUrl
    }
}
```

**Configuración final en Entra**

| Elemento | Configuración |
|---|---|
| External collaboration settings | Acceso de invitados restringido; solo miembros y roles invitan; dominios permitidos: fabrikamlab.onmicrosoft.com, outlook.com, hotmail.com, gmail.com |
| Cross-tenant access | Fabrikam: Inbound › Trust multifactor authentication |
| Acceso condicional | `LAB - MFA socios en portal`: invitados B2B de Fabrikam, Portal de Proveedores (Lab), Require MFA |
| Portal de Proveedores (Lab) | GRP-Proveedores → Comprador; `perfil` con condición External guests → `"PROVEEDOR"` |

## Problemas comunes

| Síntoma | Causa | Solución |
|---|---|---|
| `New-MgInvitation`: "the domain is not allowed" | El dominio no está en la lista de Collaboration restrictions | Agrégalo en External collaboration settings |
| El invitado ve **AADSTS50020** | Inició sesión en My Apps sin indicar el tenant de Contoso | Usa la aplicación de prueba (`/login` usa la URL del tenant) o `https://myapps.microsoft.com/?tenantid=<tenant-id>` |
| El invitado ve **AADSTS50105** | `GRP-Proveedores` no está asignado o el invitado no es miembro | Revisa la asignación y la membresía |
| Se pide MFA dos veces al socio | Falta la confianza en MFA o el usuario no hizo MFA en Fabrikam | Revisa Trust settings; el usuario debe tener MFA en su tenant |
| El código por correo no llega | Filtro de correo no deseado | Revisa la carpeta de spam; el código vence en minutos |
| El usuario de Gmail se autentica con Google | Configuraste la federación con Google antes de canjear | Esperado si hiciste el reto; el emisor será `google.com` |
| `perfil` sigue en CONSULTA para un invitado | La condición External guests no se guardó o hay otra condición después que también se cumple | Revisa el orden: gana la última condición que se cumple |
