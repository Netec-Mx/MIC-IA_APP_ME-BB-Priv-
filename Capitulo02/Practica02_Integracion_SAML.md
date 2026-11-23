# Práctica 2. Integración de una aplicación personalizada mediante SAML 2.0

**Módulo 2 · Federación y SSO mediante SAML 2.0** · Duración aproximada: **75 minutos**

## Objetivos

Al terminar la práctica podrás:

- Integrar una aplicación **fuera de la galería** con SSO SAML usando la metadata del service provider (SP).
- Configurar el **NameID**, claims personalizados, una **transformación** y un claim **condicional por grupo**.
- Definir **roles de aplicación** y asignarlos a grupos.
- Probar los flujos **SP-initiated** e **IdP-initiated** y leer la assertion con la aplicación de prueba, SAML-tracer y los sign-in logs.
- Diagnosticar un error de identificador (`AADSTS700016`).

## Antes de empezar

| Requisito | Cómo comprobarlo |
|---|---|
| Práctica 1 terminada | `verificar-ambiente.ps1` indica "Ambiente listo." y MFA registrada para ana, luis, marta y pedro |
| Tenant ID anotado | Está en `C:\Curso\recursos\datos\mis-datos.txt` |
| Entorno de Python del curso | En PowerShell 7: `C:\Curso\.venv\Scripts\python --version` muestra 3.12 |

> **Cómo usar esta guía.** Cada paso tiene la acción, una tabla que explica las opciones y el resultado esperado. Si ya dominas el tema, sigue las acciones y compara resultados; si es tu primera vez, lee las tablas. `XX` es tu número de participante (los ejemplos usan `lab01`).

**Archivos que se modifican en esta práctica**

| Archivo (en `C:\Curso\recursos`) | Qué haces |
|---|---|
| `saml-sp\config.json` | Configuras el tenant y el certificado de Entra en la aplicación de prueba |
| `saml-sp\certs\entra-actual.cer` | Guardas el certificado de firma descargado de Entra (archivo nuevo) |
| `datos\mis-datos.txt` | Anotas los identificadores de la aplicación |

Al final están los archivos completos. En Entra creas la enterprise app **Portal de Proveedores (Lab)** y sus roles; su configuración final se resume en la sección **Configuración final en Entra**.

---

## Contexto

Contoso compró un portal de proveedores que solo soporta SAML. El fabricante entregó estos requisitos:

| Requisito del fabricante | Cómo se resuelve en Entra |
|---|---|
| Entity ID `https://saml-test.contoso.com/sp`; respuestas en `https://localhost:5001/saml/acs` | Basic SAML Configuration (cargando la metadata) |
| Identificar al usuario por su **correo** | NameID = `user.mail`, formato Email address |
| Atributo `role` con **Comprador** o **Aprobador** | Roles de aplicación + claim `user.assignedroles` |
| Atributo `numeroEmpleado` **sin** el prefijo `EMP-` | Claim con transformación `Extract()` |
| Atributo `perfil` = `ALMACEN` para logística y `CONSULTA` para el resto | Claim con condición por grupo |
| Assertions firmadas con SHA-256 | Configuración predeterminada de Entra |

En el laboratorio, el "portal" es la **aplicación SAML de prueba** (`recursos\saml-sp`): un SP en Python que muestra todo lo que recibe y valida la firma, la audiencia, la vigencia y el destino de la respuesta.

---

## Tarea 1. Preparar la aplicación SAML de prueba

**Paso 1.1.** En LAB-CLIENT abre **PowerShell 7** y activa el entorno de Python del curso:

```powershell
cd C:\Curso\recursos\saml-sp
C:\Curso\.venv\Scripts\Activate.ps1
python generar_certificado_https.py
```

Salida esperada (la huella cambia):

```text
Certificado creado en C:\Curso\recursos\saml-sp\certs
Huella: 6660B2DF47990FBD145CCD9ADBEFF925B2F3F5FD
```

| Elemento | Explicación |
|---|---|
| `Activate.ps1` | Usa el Python del entorno virtual `C:\Curso\.venv`, donde están Flask, lxml, cryptography y msal. El indicador `(.venv)` aparece al inicio de la línea |
| `generar_certificado_https.py` | Crea un certificado autofirmado para `https://localhost:5001`. Entra exige HTTPS en la URL de respuesta |

**Paso 1.2.** Confía en el certificado HTTPS para que Edge no muestre advertencias:

```powershell
Import-Certificate -FilePath .\certs\localhost.cer -CertStoreLocation Cert:\CurrentUser\Root
```

Acepta la advertencia de seguridad de Windows (**Sí**). El certificado queda como raíz de confianza solo para tu usuario.

**Paso 1.3.** Abre `config.json` en VS Code (`code config.json`) y reemplaza `<tenant-id>` por tu Tenant ID en dos lugares:

```json
  "idp_login_url": "https://login.microsoftonline.com/2b6c4f1e-7a2d-4c1b-9e35-0d8a3f6c1e41/saml2",
  "idp_entity_id": "https://sts.windows.net/2b6c4f1e-7a2d-4c1b-9e35-0d8a3f6c1e41/",
```

| Parámetro de `config.json` | Significado | Efecto si es incorrecto |
|---|---|---|
| `sp_entity_id` | Identificador de la aplicación (Issuer de sus solicitudes y Audience esperada) | Entra no encuentra la aplicación: `AADSTS700016` |
| `acs_url` | URL donde la aplicación recibe la respuesta (ACS) | Entra rechaza la solicitud: `AADSTS50011` |
| `idp_login_url` | Endpoint SAML de Entra al que la aplicación envía la solicitud | La solicitud llega a otro tenant o a una URL inexistente |
| `idp_entity_id` | Issuer que la aplicación espera en la respuesta | La validación "Issuer = Entra ID esperado" falla |
| `nameid_formato` | Formato de NameID que la aplicación solicita | Si no coincide con lo que entrega Entra, algunas aplicaciones rechazan la respuesta |
| `certificados_idp` | Certificados de Entra en los que confía la aplicación | Si está vacío o es otro certificado, la firma se reporta inválida |
| `tolerancia_reloj_segundos` | Margen para diferencias de reloj al validar la vigencia | Sin margen, un desfase de segundos invalida la respuesta |

**Paso 1.4.** Inicia la aplicación:

```powershell
python app.py
```

Salida esperada:

```text
 * Running on https://127.0.0.1:5001
Press CTRL+C to quit
```

Deja esta ventana abierta. En Edge abre `https://localhost:5001`: verás la configuración y una tabla de certificados vacía. Abre `https://localhost:5001/metadata`: se descarga `metadata-sp.xml` en **Descargas**.

---

## Tarea 2. Crear la aplicación fuera de la galería

**Paso 2.1.** En el Microsoft Entra admin center abre **Entra ID › Enterprise apps › New application**. Busca "Portal de proveedores" en la galería para confirmar que no existe. Selecciona **Create your own application**:

| Campo | Valor | Explicación |
|---|---|---|
| What's the name of your app? | `Portal de Proveedores (Lab)` | Nombre visible en el portal y en My Apps |
| What are you looking to do with your application? | **Integrate any other application you don't find in the gallery (Non-gallery)** | Crea el application object y el service principal sin plantilla |

Selecciona **Create**. En unos segundos se abre la página **Overview** de la aplicación.

**Paso 2.2.** En **Properties** revisa y deja:

| Propiedad | Valor | Efecto |
|---|---|---|
| Enabled for users to sign-in? | Yes | Con No, nadie obtiene token para la aplicación |
| Assignment required? | **Yes** | Solo los usuarios o grupos asignados reciben una assertion; el resto obtiene `AADSTS50105` |
| Visible to users? | Yes | Muestra el icono en My Apps a los usuarios asignados |

Copia **Object ID** y **Application ID** en `mis-datos.txt` y selecciona **Save** si cambiaste algo.

**Paso 2.3.** Abre **Single sign-on › SAML**. En **Basic SAML Configuration** selecciona **Upload metadata file**, elige `Descargas\metadata-sp.xml` y **Add**. Revisa los valores cargados y selecciona **Save**:

| Campo | Valor esperado | Explicación |
|---|---|---|
| Identifier (Entity ID) | `https://saml-test.contoso.com/sp` (marcado como Default) | Debe coincidir con el Issuer de la solicitud y con la Audience que la aplicación valida |
| Reply URL (Assertion Consumer Service URL) | `https://localhost:5001/saml/acs` | URL donde Entra publica la respuesta; debe coincidir exactamente con la que pide la aplicación |
| Sign on URL | (vacío por ahora) | Vacío: My Apps usa IdP-initiated. Lo llenarás en la Tarea 6 |
| Relay State | (vacío) | Página a la que la aplicación redirige después de iniciar sesión |
| Logout Url | (vacío) | Endpoint de cierre de sesión del SP; la aplicación de prueba no lo implementa |

Cuando aparezca **Test single sign-on with Portal de Proveedores (Lab)?** selecciona **No, I'll test later**.

**Paso 2.4.** En la sección **SAML Certificates** observa el **Token signing certificate**:

| Dato | Qué observar |
|---|---|
| Status | Active |
| Thumbprint | Huella SHA-1 del certificado; la verás en la aplicación de prueba |
| Expiration | Tres años a partir de hoy |
| Notification Email | Tu cuenta; la Práctica 3 agrega más destinatarios |

Selecciona **Certificate (Base64) › Download** y guarda el archivo como `C:\Curso\recursos\saml-sp\certs\entra-actual.cer`.

**Paso 2.5.** En la sección **Set up Portal de Proveedores (Lab)** compara:

| Valor de Entra | Debe ser igual a… |
|---|---|
| Login URL | `idp_login_url` de `config.json` |
| Microsoft Entra Identifier | `idp_entity_id` de `config.json` |

**Paso 2.6.** En `config.json` registra el certificado y guarda:

```json
  "certificados_idp": ["certs/entra-actual.cer"],
```

En la ventana de PowerShell detén la aplicación (**Ctrl+C**) e iníciala de nuevo con `python app.py`. En `https://localhost:5001` la tabla de certificados muestra la huella y la fecha de vencimiento: deben coincidir con el portal.

---

## Tarea 3. Definir roles de aplicación y asignar grupos

**Paso 3.1.** Abre **Entra ID › App registrations › All applications › Portal de Proveedores (Lab) › App roles › Create app role** y crea dos roles:

| Campo | Rol 1 | Rol 2 |
|---|---|---|
| Display name | `Comprador` | `Aprobador` |
| Allowed member types | Users/Groups | Users/Groups |
| Value | `Comprador` | `Aprobador` |
| Description | Puede crear órdenes de compra | Aprueba órdenes de compra |
| Do you want to enable this app role? | Sí | Sí |

| Concepto | Explicación |
|---|---|
| Value | Es el texto que viaja en el claim `role`; la aplicación lo compara para autorizar |
| Allowed member types = Users/Groups | Permite asignar el rol a usuarios y grupos (no a aplicaciones) |
| Por qué roles y no grupos | El rol tiene significado para la aplicación, no depende del nombre del grupo y no sufre el límite de 150 grupos en SAML |

**Paso 3.2.** Vuelve a **Enterprise apps › Portal de Proveedores (Lab) › Users and groups › Add user/group** y crea tres asignaciones:

| Grupo | Rol | Quiénes quedan con acceso |
|---|---|---|
| `DYN-Compras` | Comprador | ana, luis y prueba.nube |
| `GRP-Compras-Jefes` | Aprobador | luis |
| `GRP-Logistica` | Comprador | pedro |

Resultado esperado: tres filas en **Users and groups**. `luis.mendez` tiene dos roles (Comprador por DYN-Compras y Aprobador por GRP-Compras-Jefes); el claim `role` llevará ambos valores.

---

## Tarea 4. Primera prueba con los claims predeterminados

**Paso 4.1.** Prueba primero con tu cuenta de administración: en **Single sign-on** selecciona **Test › Test sign in**. Resultado esperado: error **AADSTS50105** ("The signed in user is not assigned to a role for the application"), porque tu cuenta no está asignada. El panel de prueba muestra la causa y la solución.

**Paso 4.2.** Abre una **ventana InPrivate** de Edge, ve a `https://localhost:5001` y selecciona **Iniciar sesión (SP-initiated)**. Inicia sesión con `ana.lopez@labXX.onmicrosoft.com`.

Resultado esperado en la aplicación de prueba:

```text
Flujo: SP-initiated (respuesta a una solicitud de esta aplicación)

Validación                              Resultado   Detalle
Estado de la respuesta                  OK          Success
Destination = ACS                       OK          https://localhost:5001/saml/acs
Issuer = Entra ID esperado              OK          https://sts.windows.net/2b6c.../
InResponseTo = ID de la solicitud       OK          _7c0e4b...
Firma válida (respuesta o assertion)    OK          Respuesta: sin firma · Assertion: válida
Vigencia (NotBefore / NotOnOrAfter)     OK          2026-11-17T17:02:10Z → 2026-11-17T18:07:10Z
Audience = Entity ID de la app          OK          https://saml-test.contoso.com/sp
Recipient = ACS                         OK          https://localhost:5001/saml/acs

NameID: ana.lopez@lab01.onmicrosoft.com (emailAddress)
```

Y en **Claims recibidos**, entre otros: `.../claims/givenname = Ana`, `.../claims/surname = López`, `.../claims/emailaddress`, `.../claims/name`, `.../identity/claims/tenantid`, `.../identity/claims/objectidentifier`, `.../identity/claims/displayname` y `.../identity/claims/authnmethodsreferences`.

| Observación | Explicación |
|---|---|
| Respuesta "sin firma", assertion "válida" | La opción predeterminada de Entra es **Sign SAML assertion** |
| NameID en formato `emailAddress` aunque el origen es el UPN | La aplicación pidió ese formato en su solicitud y el NameID de Entra está en **Default** |
| `authnmethodsreferences` | Indica cómo se autenticó el usuario (contraseña, MFA) |
| Los nombres de claim son URIs largas | Así los emite Entra por omisión; el fabricante pidió nombres cortos (`role`, `numeroEmpleado`, `perfil`) |

---

## Tarea 5. Personalizar el NameID y los claims

En **Single sign-on › Attributes & Claims › Edit**:

**Paso 5.1.** Selecciona **Unique User Identifier (Name ID)** y configura:

| Campo | Valor | Efecto |
|---|---|---|
| Name identifier format | **Email address** | El NameID se emite con formato `emailAddress` aunque la aplicación no lo pida |
| Source | Attribute | El valor sale de un atributo del usuario |
| Source attribute | `user.mail` | El correo; para los usuarios sincronizados viene del atributo `mail` de AD |

**Paso 5.2.** **Add new claim**: `role`

| Campo | Valor | Explicación |
|---|---|---|
| Name | `role` | Nombre exacto que pidió el fabricante |
| Namespace | (vacío) | Sin namespace, el atributo se llama solo `role` |
| Source | Attribute | |
| Source attribute | `user.assignedroles` | Emite el **Value** de cada rol asignado al usuario en esta aplicación |

**Paso 5.3.** **Add new claim**: `numeroEmpleado`

| Campo | Valor | Explicación |
|---|---|---|
| Name | `numeroEmpleado` | |
| Source | **Transformation** | El valor se calcula |
| Transformation | `Extract() - After matching` | Devuelve el texto que sigue al valor indicado |
| Parameter 1 (Input) | Attribute: `user.employeeid` | `EMP-00412` para Ana |
| Value | `EMP-` | Texto que se busca; se devuelve lo que está después |

Resultado del cálculo para Ana: `00412`. (Alternativa: `RegexReplace()` con un patrón, si tu tenant la muestra.)

**Paso 5.4.** **Add new claim**: `perfil` con un valor condicional

| Campo | Valor | Explicación |
|---|---|---|
| Name | `perfil` | |
| Source | Attribute | |
| Source attribute | `"CONSULTA"` (escrito entre comillas) | Un valor **constante** para todos los usuarios |
| Claim conditions › User type | `Members` | La condición aplica a usuarios internos |
| Claim conditions › Scoped Groups | `GRP-Logistica` | Solo a los miembros de este grupo |
| Claim conditions › Source / Value | Attribute / `"ALMACEN"` | Valor que reemplaza a la constante cuando se cumple la condición |

Guarda cada claim (**Save**). Las condiciones se evalúan en orden y gana la **última** que se cumple.

**Paso 5.5.** Prueba de nuevo en una ventana InPrivate con tres usuarios y compara:

| Usuario | NameID | role | numeroEmpleado | perfil |
|---|---|---|---|---|
| `ana.lopez` | `ana.lopez@lab01.onmicrosoft.com` | Comprador | 00412 | CONSULTA |
| `luis.mendez` | `luis.mendez@lab01.onmicrosoft.com` | Comprador, Aprobador | 00418 | CONSULTA |
| `pedro.garcia` | `pedro.garcia@lab01.onmicrosoft.com` | Comprador | 00377 | ALMACEN |
| `marta.ruiz` | — | — | — | — |

Con `marta.ruiz` el resultado esperado es **AADSTS50105**: Finanzas no está asignado a la aplicación.

> **Importante.** Entre una prueba y otra cierra la ventana InPrivate. Si reutilizas la ventana, Entra reutiliza la sesión del usuario anterior.

---

## Tarea 6. Flujos SP-initiated e IdP-initiated y herramientas de diagnóstico

**Paso 6.1. IdP-initiated.** En una ventana InPrivate entra a `https://myapps.microsoft.com` con `ana.lopez` y selecciona el icono **Portal de Proveedores (Lab)**. Resultado esperado: la aplicación muestra **Flujo: IdP-initiated** y no aparece la validación de `InResponseTo` (no hubo solicitud).

**Paso 6.2.** En **Basic SAML Configuration** escribe **Sign on URL** = `https://localhost:5001/login` y guarda. Repite el Paso 6.1: ahora My Apps redirige a la aplicación, que genera la solicitud, y el flujo es **SP-initiated**.

| Configuración de Sign on URL | Comportamiento desde My Apps |
|---|---|
| Vacía | Entra envía la respuesta directamente a la Reply URL predeterminada (IdP-initiated) |
| Con valor | My Apps abre esa URL y la aplicación inicia el flujo (SP-initiated) |

**Paso 6.3. SAML-tracer.** En Edge abre la extensión **SAML-tracer** (icono en la barra) y deja su ventana abierta. En una ventana InPrivate (habilita la extensión en InPrivate desde `edge://extensions` › Detalles › Permitir en InPrivate) inicia sesión con `ana.lopez`.

| Línea marcada como SAML | Qué contiene |
|---|---|
| `GET https://login.microsoftonline.com/.../saml2?SAMLRequest=...` | El `AuthnRequest` decodificado: `ID`, `Issuer`, `AssertionConsumerServiceURL` |
| `POST https://localhost:5001/saml/acs` | La `SAMLResponse`: busca `InResponseTo` (igual al `ID` anterior), `NameID`, los `Attribute` y `<Signature>` |

**Paso 6.4. Sign-in logs.** En el portal abre **Entra ID › Monitoring & health › Sign-in logs**, filtra **Application** = Portal de Proveedores (Lab) y abre un registro de ana:

| Pestaña | Qué observar |
|---|---|
| Basic info | Application, Status (Success), Correlation ID |
| Authentication Details | Métodos usados (contraseña, notificación de Authenticator si hubo MFA) |
| Conditional Access | Políticas evaluadas (aún ninguna) |
| Additional Details | Protocolo de inicio de sesión |

Los registros de marta muestran **Failure** con el código **50105**.

---

## Tarea 7. Diagnosticar un error de identificador

**Paso 7.1.** En `config.json` cambia temporalmente `sp_entity_id` a `https://saml-test.contoso.com/sp2`, guarda y reinicia la aplicación. Inicia sesión desde `https://localhost:5001`.

Resultado esperado: Entra muestra **AADSTS700016: Application with identifier 'https://saml-test.contoso.com/sp2' was not found in the directory**.

| Pregunta de diagnóstico | Respuesta |
|---|---|
| ¿La página de error es de Microsoft o de la aplicación? | De Microsoft: el problema está en la solicitud, antes de autenticar |
| ¿Qué valor compara Entra? | El `Issuer` del AuthnRequest contra los **Identifier** registrados en las aplicaciones |
| ¿Dónde se ve el valor enviado? | En el mensaje de error, en SAML-tracer y en `saml-sp\ultima_solicitud.xml` |

**Paso 7.2.** Restablece `sp_entity_id` a `https://saml-test.contoso.com/sp`, guarda, reinicia y confirma que el inicio de sesión vuelve a funcionar.

> **Reto opcional.** Cambia en `config.json` el valor de `acs_url` a `https://localhost:5001/saml/acs2` (sin cambiar Entra). ¿Qué código de error aparece y por qué? (Respuesta: `AADSTS50011`, la URL de respuesta solicitada no está registrada.) Restablece el valor al terminar.

---

## Resultado esperado

| Comprobación | Resultado |
|---|---|
| Validaciones de la aplicación de prueba | Todas en OK para ana, luis y pedro |
| NameID | Correo del usuario, formato `emailAddress` |
| Claims personalizados | `role`, `numeroEmpleado` y `perfil` con los valores de la tabla del Paso 5.5 |
| Usuario no asignado (marta) | `AADSTS50105` |
| Flujos | IdP-initiated sin Sign on URL; SP-initiated con Sign on URL |
| Identificador incorrecto | `AADSTS700016` |

**Lista de verificación**

- [ ] Creé la aplicación fuera de la galería con la metadata del SP.
- [ ] La aplicación de prueba valida la firma con el certificado descargado de Entra.
- [ ] Configuré NameID, `role`, `numeroEmpleado` (transformación) y `perfil` (condición por grupo).
- [ ] Asigné grupos con roles y comprobé el comportamiento con un usuario no asignado.
- [ ] Leí la solicitud y la respuesta en SAML-tracer y el registro en los sign-in logs.
- [ ] Provoqué y corregí `AADSTS700016`.

## Archivos completos

**`C:\Curso\recursos\saml-sp\config.json`** (también en `soluciones\saml-sp-config-practica2.json`; el Tenant ID es un ejemplo)

```json
{
  "puerto": 5001,
  "sp_entity_id": "https://saml-test.contoso.com/sp",
  "acs_url": "https://localhost:5001/saml/acs",
  "idp_login_url": "https://login.microsoftonline.com/2b6c4f1e-7a2d-4c1b-9e35-0d8a3f6c1e41/saml2",
  "idp_entity_id": "https://sts.windows.net/2b6c4f1e-7a2d-4c1b-9e35-0d8a3f6c1e41/",
  "nameid_formato": "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress",
  "certificados_idp": ["certs/entra-actual.cer"],
  "relay_state": "/",
  "tolerancia_reloj_segundos": 120
}
```

**`C:\Curso\recursos\saml-sp\certs\entra-actual.cer`**: certificado descargado de Entra (formato Base64, empieza con `-----BEGIN CERTIFICATE-----`).

**Configuración final en Entra** (Portal de Proveedores (Lab))

| Sección | Configuración |
|---|---|
| Properties | Assignment required = Yes; Visible to users = Yes |
| Basic SAML Configuration | Identifier `https://saml-test.contoso.com/sp`; Reply URL `https://localhost:5001/saml/acs`; Sign on URL `https://localhost:5001/login` |
| Name ID | Email address · `user.mail` |
| Claims adicionales | `role` = `user.assignedroles`; `numeroEmpleado` = `Extract() After "EMP-"` sobre `user.employeeid`; `perfil` = `"CONSULTA"`, o `"ALMACEN"` si es miembro de GRP-Logistica |
| App roles | Comprador, Aprobador |
| Users and groups | DYN-Compras → Comprador; GRP-Compras-Jefes → Aprobador; GRP-Logistica → Comprador |

Fragmento del manifiesto de la aplicación (App registrations › Manifest) con los roles (los `id` son GUID generados por el portal):

```json
"appRoles": [
  {
    "allowedMemberTypes": [ "User" ],
    "description": "Aprueba órdenes de compra",
    "displayName": "Aprobador",
    "id": "a3b4c5d6-7e8f-4a1b-9c2d-3e4f5a6b7c8d",
    "isEnabled": true,
    "value": "Aprobador"
  },
  {
    "allowedMemberTypes": [ "User" ],
    "description": "Puede crear órdenes de compra",
    "displayName": "Comprador",
    "id": "6f1c2a9e-1b8e-4a7e-9a52-1f2d3c4b5a61",
    "isEnabled": true,
    "value": "Comprador"
  }
]
```

## Problemas comunes

| Síntoma | Causa | Solución |
|---|---|---|
| Edge muestra "La conexión no es privada" en `localhost:5001` | No se importó el certificado HTTPS | Repite el Paso 1.2 y reinicia Edge |
| `ModuleNotFoundError: No module named 'flask'` | No se activó el entorno `.venv` | Ejecuta `C:\Curso\.venv\Scripts\Activate.ps1` |
| `AADSTS700016` | `sp_entity_id` distinto del Identifier de Entra | Iguala ambos valores (incluida la barra final) |
| `AADSTS50011` | `acs_url` no está en las Reply URL | Agrega la URL exacta en Basic SAML Configuration |
| `AADSTS50105` | El usuario no está en un grupo asignado | Asigna el grupo; recuerda que los grupos anidados no cuentan |
| "Firma válida: FALLA" | `config.json` no tiene el certificado activo de Entra | Descarga de nuevo **Certificate (Base64)** y revisa `certificados_idp` |
| "InResponseTo: FALLA" | La sesión de la aplicación se perdió (se reinició `app.py` a mitad del flujo) | Vuelve a iniciar sesión desde `https://localhost:5001` |
| `numeroEmpleado` no aparece | El usuario no tiene `employeeId` o el valor no contiene `EMP-` | Revisa el atributo en el perfil del usuario |
| `role` aparece vacío | El grupo se asignó sin rol (Default Access) | Edita la asignación y elige el rol |
| Se inicia sesión con el usuario anterior | Ventana InPrivate reutilizada | Cierra todas las ventanas InPrivate entre pruebas |
