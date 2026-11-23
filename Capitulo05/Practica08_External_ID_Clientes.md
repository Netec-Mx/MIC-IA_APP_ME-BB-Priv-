# Práctica 8. Federación de clientes con Microsoft Entra External ID

**Módulo 5 · Microsoft Entra External ID y federación de identidades externas** · Duración aproximada: **90 minutos**

## Objetivos

Al terminar la práctica podrás:

- Trabajar en un **external tenant** y aplicar la marca de la empresa a las páginas de inicio de sesión.
- Configurar **Google** como proveedor de identidad para clientes.
- Crear un **atributo personalizado** y un **user flow** de registro e inicio de sesión.
- Registrar una aplicación web OIDC, asociarla al user flow y agregar atributos al token.
- Validar el escenario de extremo a extremo con una cuenta local y con Google.

## Antes de empezar

| Requisito | Cómo comprobarlo |
|---|---|
| External tenant `contosoclientesXX` | Lo creó soporte; tu cuenta de participante es administradora |
| Cuenta de Google y proyecto `entra-labXX` | Puedes entrar a `https://console.cloud.google.com` y ver el proyecto |
| Un buzón donde recibir códigos | Tu buzón de Outlook.com (u otro distinto del de Gmail) |
| Entorno de Python del curso | `C:\Curso\.venv\Scripts\Activate.ps1` funciona |

> **Cómo usar esta guía.** Cada paso tiene la acción, la explicación de las opciones y el resultado esperado. Revisa siempre, en la esquina superior derecha del portal, **en qué tenant estás**: casi toda la práctica ocurre en el external tenant.

**Archivos que se modifican en esta práctica**

| Archivo (en `C:\Curso\recursos`) | Qué haces |
|---|---|
| `oidc-app\config.json` | Configuras el external tenant, el client ID y el secreto de la tienda |
| `datos\mis-datos.txt` | Registras los datos del external tenant y de la aplicación |

---

## Contexto

Contoso lanza su **tienda en línea**. Los clientes deben registrarse solos, con correo y contraseña o con Google, en páginas con la marca de Contoso. Mercadotecnia necesita el **país** y si el cliente **acepta promociones**.

```text
Cliente ─► Tienda (OIDC, MSAL) ─► external tenant contosoclientesXX ─► user flow "Registro-Tienda"
                                                                     ├─ correo + contraseña
                                                                     └─ Google
```

| Pieza | Dónde se configura |
|---|---|
| Marca | Company branding |
| Proveedores de identidad | External Identities › All identity providers |
| Datos del cliente | Custom user attributes + atributos del user flow |
| Experiencia de registro | User flows |
| Aplicación | App registrations (OIDC) + Enterprise applications (claims) |

---

## Tarea 1. Entrar al external tenant

**Paso 1.1.** En el Microsoft Entra admin center selecciona el icono **Settings** (engrane) › **Directories + subscriptions** y, en la fila `Contoso Clientes XX`, selecciona **Switch**.

**Paso 1.2.** En **Overview** copia en `mis-datos.txt`:

| Dato | Ejemplo |
|---|---|
| Tenant ID | `7d3c9e2a-...` |
| Primary domain | `contosoclientes01.onmicrosoft.com` (el subdominio es `contosoclientes01`) |

| Diferencia con el tenant de trabajo | Explicación |
|---|---|
| Configuración "External" | El tenant está pensado para usuarios que se registran solos; no tiene los empleados de Contoso |
| URL de inicio de sesión | `https://contosoclientes01.ciamlogin.com/` en lugar de `login.microsoftonline.com` |
| Menú External Identities | Incluye User flows y Custom user attributes |

---

## Tarea 2. Aplicar la marca de Contoso

**Paso 2.1.** Abre **Company branding › Default sign-in experience › Edit**:

| Pestaña | Campo | Valor |
|---|---|---|
| Basics | Page background color | `#0F3D5C` |
| Layout | (dejar la plantilla predeterminada) | |
| Header | Banner logo | `C:\Curso\recursos\datos\logo-contoso-banner.png` |
| Sign-in form | Sign-in page text | `Bienvenido a la tienda en línea de Contoso` |

Selecciona **Review + save › Save**. Los cambios tardan unos minutos en verse.

---

## Tarea 3. Configurar Google como proveedor de identidad

**Paso 3.1.** En `https://console.cloud.google.com`, con el proyecto `entra-labXX` seleccionado:

1. **APIs & Services › OAuth consent screen** (Google Auth Platform): tipo **External**, nombre de la app `Contoso Tienda (Lab)`, tu correo de soporte; en **Audience › Test users** agrega tu cuenta de Gmail.
2. **Credentials › Create credentials › OAuth client ID** › **Web application**, nombre `Entra External ID`:

| Campo | Valor (reemplaza el subdominio y el Tenant ID del external tenant) |
|---|---|
| Authorized JavaScript origins | `https://contosoclientesXX.ciamlogin.com` |
| Authorized redirect URIs | `https://contosoclientesXX.ciamlogin.com/<tenant-id>/federation/oauth2` |
| | `https://contosoclientesXX.ciamlogin.com/contosoclientesXX.onmicrosoft.com/federation/oauth2` |

Selecciona **Create** y copia el **Client ID** y el **Client secret**.

| Concepto | Explicación |
|---|---|
| Redirect URIs | Google solo devuelve la respuesta a URLs registradas; son los endpoints de federación de tu external tenant |
| Modo de prueba de Google | Solo los "Test users" pueden iniciar sesión; para producción se publica la app en Google |

**Paso 3.2.** En el external tenant abre **External Identities › All identity providers › Google** (pestaña **Built-in**) y escribe el **Client ID** y el **Client secret**. Selecciona **Save**.

---

## Tarea 4. Crear el atributo personalizado

**Paso 4.1.** Abre **External Identities › Custom user attributes › Add**:

| Campo | Valor | Explicación |
|---|---|---|
| Name | `AceptaPromociones` | Nombre del atributo; en tokens y en Graph aparece como `extension_<id>_AceptaPromociones` |
| Data Type | **Boolean** | Se mostrará como casilla |
| Description | Acepta recibir promociones por correo | |

Selecciona **Create**.

---

## Tarea 5. Registrar la aplicación de la tienda

**Paso 5.1.** Abre **App registrations › New registration**:

| Campo | Valor | Explicación |
|---|---|---|
| Name | `Tienda en línea (Lab)` | |
| Supported account types | **Accounts in this organizational directory only** | Solo los clientes del external tenant |
| Redirect URI | **Web** · `http://localhost:5002/getAToken` | URL donde la aplicación recibe el código; `http://localhost` se admite para desarrollo |

Selecciona **Register** y copia el **Application (client) ID** en `mis-datos.txt`.

**Paso 5.2.** En **Certificates & secrets › Client secrets › New client secret** escribe la descripción `lab`, vigencia 90 días, **Add**, y copia el **Value** (solo se muestra una vez).

**Paso 5.3.** En **API permissions** confirma que existen los permisos delegados de Microsoft Graph `openid` y `offline_access` (agrégalos con **Add a permission › Microsoft Graph › Delegated permissions** si faltan) y selecciona **Grant admin consent for Contoso Clientes XX › Yes**.

| Concepto | Explicación |
|---|---|
| `openid` | Permite obtener el ID token (inicio de sesión OIDC) |
| `offline_access` | Permite obtener un refresh token |
| Consentimiento de administrador | Los clientes no pueden dar consentimiento a permisos; el administrador lo otorga para todos |

---

## Tarea 6. Crear el user flow

**Paso 6.1.** Abre **External Identities › User flows › New user flow**:

| Sección | Valor | Efecto |
|---|---|---|
| Name | `Registro-Tienda` | |
| Identity providers › Email accounts | **Email with password** | El cliente crea una contraseña; su correo se verifica con un código |
| Identity providers › Other identity providers | **Google** | Aparece el botón "Sign in with Google" |
| User attributes | Given Name, Surname, Country/Region, **AceptaPromociones** | Datos que se piden al registrarse (Show more attributes para ver todos) |

Selecciona **Create**.

**Paso 6.2.** Abre el user flow **Registro-Tienda › Applications › Add application**, elige `Tienda en línea (Lab)` y **Select**.

**Paso 6.3.** En **Page layouts** ajusta las etiquetas y marca **Required** = Yes en Given Name, Surname y Country/Region; en `AceptaPromociones` escribe la etiqueta `Acepto recibir promociones de Contoso` y déjalo **opcional**. Selecciona **Save**.

| Opción | Efecto |
|---|---|
| Atributos del user flow | Se piden solo al **registrarse**; en inicios de sesión posteriores ya no aparecen |
| Required | El cliente no puede continuar sin capturarlo |
| Una aplicación por user flow | Cada aplicación se asocia a un solo user flow |

---

## Tarea 7. Agregar los atributos al token

Por omisión el ID token no incluye el país ni los atributos personalizados.

**Paso 7.1.** Abre **Enterprise apps › Tienda en línea (Lab) › Single sign-on** (o **Attributes & Claims**, según la versión del portal) › **Edit** y agrega cuatro claims (**Add new claim**):

| Name | Source attribute |
|---|---|
| `given_name` | `user.givenname` |
| `family_name` | `user.surname` |
| `pais` | `user.country` |
| `acepta_promociones` | el atributo personalizado `AceptaPromociones` (aparece en la lista como extensión) |

**Paso 7.2.** Abre **App registrations › Tienda en línea (Lab) › Manifest** y cambia el valor `acceptMappedClaims` a `true` (en el formato actual del manifiesto está dentro de la sección `"api"`). Selecciona **Save**.

| Concepto | Explicación |
|---|---|
| Claims mapeados | Se configuran en la enterprise app (service principal) |
| `acceptMappedClaims` | Indica que la aplicación acepta claims personalizados en tokens firmados con la clave común del tenant; sin él, el inicio de sesión falla con `AADSTS50146` |

---

## Tarea 8. Ejecutar la tienda y registrar un cliente

**Paso 8.1.** En VS Code edita `C:\Curso\recursos\oidc-app\config.json`:

```json
{
  "puerto": 5002,
  "authority": "https://contosoclientes01.ciamlogin.com/contosoclientes01.onmicrosoft.com",
  "client_id": "5c9b1d2e-4f6a-4b8c-9d0e-a41f02b7c3d8",
  "client_secret": "<valor-del-secreto>",
  "redirect_uri": "http://localhost:5002/getAToken",
  "post_logout_redirect_uri": "http://localhost:5002/"
}
```

| Parámetro | Explicación | Efecto si es incorrecto |
|---|---|---|
| `authority` | Endpoint del external tenant (`ciamlogin.com`) | Con `login.microsoftonline.com` no se usa el user flow de clientes |
| `client_id` | Application (client) ID de la tienda | `AADSTS700016` |
| `client_secret` | Value del secreto | `AADSTS7000215` (secreto inválido) |
| `redirect_uri` | Igual a la Redirect URI registrada | `AADSTS50011` |

**Paso 8.2.** En PowerShell 7:

```powershell
cd C:\Curso\recursos\oidc-app
C:\Curso\.venv\Scripts\Activate.ps1
python app.py
```

Salida esperada: ` * Running on http://localhost:5002`.

**Paso 8.3.** En una ventana InPrivate abre `http://localhost:5002` y selecciona **Registrarse o iniciar sesión**. Verás la página con la marca de Contoso. Selecciona **No account? Create one**, escribe tu correo de Outlook.com, captura el **código de verificación** que llega al buzón, crea una contraseña y completa nombre, apellido, país y la casilla de promociones.

Resultado esperado en la tienda:

```text
Hola, Laura. Iniciaste sesión con una cuenta local del external tenant.

Claim                 Valor
iss                   https://<tenant-id>.ciamlogin.com/<tenant-id>/v2.0
aud                   5c9b1d2e-...
oid                   0e1f2a3b-...
tid                   7d3c9e2a-...
given_name            Laura
family_name           Cliente
pais                  Mexico
acepta_promociones    true
...
```

**Paso 8.4.** Selecciona **Cerrar sesión**. En otra ventana InPrivate repite el inicio de sesión con **Sign in with Google** y tu cuenta de Gmail. La primera vez se piden los atributos del registro.

Resultado esperado: el claim `idp` = `google.com` y los atributos capturados.

| Claim | Cuenta local | Google |
|---|---|---|
| `idp` | (no aparece) | `google.com` |
| `given_name`, `family_name` | Capturados en el registro | Capturados en el registro (o de Google si se mapean) |
| `pais`, `acepta_promociones` | Capturados en el registro | Capturados en el registro |

---

## Tarea 9. Revisar los clientes registrados

**Paso 9.1.** En el external tenant abre **Users**: aparecen los dos clientes. Abre cada uno y revisa **Identities**:

| Cliente | Sign-in type | Issuer |
|---|---|---|
| Cuenta de Outlook.com | emailAddress | `contosoclientesXX.onmicrosoft.com` |
| Cuenta de Gmail | federated | `google.com` |

**Paso 9.2.** Abre **Sign-in logs** del external tenant y busca los inicios de sesión en `Tienda en línea (Lab)`.

> **Reto opcional.** Crea un segundo user flow con **Email one-time passcode** (sin contraseña), asócialo a la tienda (una aplicación solo puede tener un user flow: primero quítala de Registro-Tienda) y compara la experiencia.

---

## Resultado esperado

| Comprobación | Resultado |
|---|---|
| Página de inicio de sesión | Fondo azul de Contoso, logotipo y texto de bienvenida |
| Registro con correo | Código de verificación → contraseña → atributos → tienda con claims |
| Registro con Google | Botón de Google → atributos → `idp = google.com` |
| Claims personalizados | `pais` y `acepta_promociones` en el ID token |
| Usuarios del external tenant | Dos clientes, uno local y uno federado |

**Lista de verificación**

- [ ] Trabajé en el external tenant y apliqué la marca.
- [ ] Configuré Google con las Redirect URIs del external tenant.
- [ ] Creé el atributo `AceptaPromociones` y el user flow `Registro-Tienda`.
- [ ] Registré la tienda, otorgué consentimiento y agregué los claims al token.
- [ ] Registré un cliente con correo y otro con Google, y revisé sus identidades.

## Archivos completos

**`C:\Curso\recursos\oidc-app\config.json`** (también en `soluciones\oidc-app-config-practica8.json`; los identificadores son ejemplos)

```json
{
  "puerto": 5002,
  "authority": "https://contosoclientes01.ciamlogin.com/contosoclientes01.onmicrosoft.com",
  "client_id": "5c9b1d2e-4f6a-4b8c-9d0e-a41f02b7c3d8",
  "client_secret": "<valor-del-secreto>",
  "redirect_uri": "http://localhost:5002/getAToken",
  "post_logout_redirect_uri": "http://localhost:5002/"
}
```

**`C:\Curso\recursos\datos\mis-datos.txt`** (sección de External ID)

```text
External ID (Práctica 8)
  Subdominio del external tenant .......... contosoclientes01
  ID del external tenant .................. 7d3c9e2a-5b4f-4e1d-8c6a-1f2e3d4c5b6a
  Client ID de la tienda .................. 5c9b1d2e-4f6a-4b8c-9d0e-a41f02b7c3d8
```

**Configuración final en el external tenant**

| Elemento | Configuración |
|---|---|
| Company branding | Fondo `#0F3D5C`, banner `logo-contoso-banner.png`, texto de bienvenida |
| Proveedores | Email with password, Google |
| Custom user attributes | `AceptaPromociones` (Boolean) |
| User flow `Registro-Tienda` | Email with password + Google; Given Name, Surname, Country/Region (obligatorios), AceptaPromociones (opcional); aplicación Tienda en línea (Lab) |
| App registration | Web `http://localhost:5002/getAToken`; secreto; `openid` y `offline_access` con consentimiento; `acceptMappedClaims = true` |
| Claims de la enterprise app | `given_name`, `family_name`, `pais`, `acepta_promociones` |

## Problemas comunes

| Síntoma | Causa | Solución |
|---|---|---|
| No aparece el botón de Google | Google no está en el user flow o falta su configuración | Revisa **All identity providers** y el user flow |
| Google: `redirect_uri_mismatch` | Las URIs en Google no coinciden con las del external tenant | Copia exactamente subdominio y Tenant ID |
| Google: "Access blocked: app has not completed verification" | La cuenta no está en Test users | Agrégala en **Audience › Test users** |
| `AADSTS50146` | Claims mapeados sin `acceptMappedClaims` | Cambia el manifiesto (Paso 7.2) |
| `AADSTS50011` | La Redirect URI no coincide | Revisa `http://localhost:5002/getAToken` en ambos lados |
| `AADSTS7000215` | Secreto incorrecto (se copió el **Secret ID** en lugar del **Value**) | Crea un secreto nuevo y copia el Value |
| La tienda dice "Flujo inválido" | Se reinició `app.py` o se abrió el enlace en otra ventana | Vuelve a iniciar sesión desde `http://localhost:5002` |
| No se piden los atributos al iniciar sesión | El usuario ya estaba registrado | Esperado: solo se piden en el registro |
| La marca no aparece | Propagación de la configuración | Espera unos minutos y usa una ventana InPrivate nueva |
