# Práctica 3. Gestión y rotación de certificados SAML

**Módulo 2 · Federación y SSO mediante SAML 2.0** · Duración aproximada: **30 minutos**

## Objetivos

Al terminar la práctica podrás:

- Revisar el certificado de firma de una aplicación SAML: estado, huella, vigencia y destinatarios de notificación.
- Comprobar qué ocurre cuando el certificado se cambia en Entra sin coordinarlo con la aplicación.
- Ejecutar una rotación **sin interrupción**: certificado nuevo inactivo → aplicación que confía en ambos → activación → validación → retiro del anterior.
- Cambiar las opciones de firma y consultar el inventario de certificados con Microsoft Graph PowerShell.

## Antes de empezar

| Requisito | Cómo comprobarlo |
|---|---|
| Práctica 2 terminada | `ana.lopez` inicia sesión en `https://localhost:5001` y todas las validaciones están en OK |
| Aplicación de prueba en ejecución | En PowerShell 7, con `.venv` activo: `cd C:\Curso\recursos\saml-sp` y `python app.py` |

> **Cómo usar esta guía.** Cada paso tiene la acción, la explicación de las opciones y el resultado esperado. Haz las pruebas de inicio de sesión siempre en una **ventana InPrivate nueva** con `ana.lopez`.

**Archivos que se modifican en esta práctica**

| Archivo (en `C:\Curso\recursos\saml-sp`) | Qué haces |
|---|---|
| `certs\entra-nuevo.cer` | Guardas el certificado nuevo descargado de Entra (archivo nuevo) |
| [`config.json`](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/saml-sp/config.json) | Agregas el certificado nuevo y después retiras el anterior |

---

## Contexto

El fabricante del portal de proveedores informa que su aplicación **acepta varios certificados de confianza a la vez** (como la aplicación de prueba, que lee la lista `certificados_idp`). Contoso quiere practicar la rotación antes de que llegue el aviso de vencimiento real.

| Fase | Dónde se hace | Estado del servicio |
|---|---|---|
| 1. Crear certificado nuevo (inactivo) | Entra | Sin cambios: firma el anterior |
| 2. Entregar el nuevo al SP | Aplicación | El SP confía en ambos |
| 3. Activar el nuevo | Entra | Firma el nuevo; el SP lo acepta |
| 4. Validar | Ambos | Inicio de sesión exitoso con la huella nueva |
| 5. Retirar el anterior | Ambos | Solo queda el nuevo |

---

## Tarea 1. Revisar el certificado activo

**Paso 1.1.** Abre **Enterprise apps › Portal de Proveedores (Lab) › Single sign-on**. En **SAML Certificates › Token signing certificate** selecciona **Edit**.

| Elemento | Qué observar |
|---|---|
| Lista de certificados | Uno solo, **Active**, con su huella (thumbprint) y fecha de vencimiento |
| Signing Option | `Sign SAML assertion` |
| Signing Algorithm | `SHA-256` |
| Notification Email Addresses | Tu cuenta |

**Paso 1.2.** En **Notification Email Addresses** agrega `carla.diaz@labXX.onmicrosoft.com` (simula el buzón del dueño de la aplicación) y selecciona **Save**.

| Concepto | Explicación |
|---|---|
| Notificaciones | Entra envía correo 60, 30 y 7 días antes del vencimiento a estas direcciones |
| Buena práctica | Incluir un buzón compartido del equipo de identidad y al dueño de la aplicación, no a una sola persona |

**Paso 1.3.** En PowerShell 7 (otra ventana; la aplicación sigue ejecutándose en la primera) consulta el inventario:

```powershell
cd C:\Curso\recursos\scripts
./inventario-certificados.ps1 -Dias 1200
```

Salida esperada (las fechas dependen del día de creación):

```text
Aplicacion                  Huella                                   Activo Vence      Dias
----------                  ------                                   ------ -----      ----
Portal de Proveedores (Lab) 9C2E31D0A6B5F4E8C7D2A1B0F9E8D7C6B5A47A41   True 2029-11-17 1095

Aplicaciones SAML: 1 · certificados con menos de 1200 días: 1
```

| Parámetro | Efecto |
|---|---|
| `-Dias 1200` | Muestra los certificados que vencen en menos de 1 200 días (todos en el laboratorio). En operación se usa 90 |
| Columna `Activo` | Compara la huella con `preferredTokenSigningKeyThumbprint` del service principal |

---

## Tarea 2. Crear el certificado nuevo y ver una rotación no coordinada

**Paso 2.1.** En la página de edición del certificado selecciona **New Certificate**. En la fila nueva elige una **Expiration Date** a dos años y selecciona **Save**.

| Elemento | Explicación |
|---|---|
| Fecha de vencimiento | Se puede elegir cualquier fecha entre hoy y tres años; después de guardar ya no se cambia |
| Estado después de guardar | **Inactive**: el certificado anterior sigue firmando |

**Paso 2.2.** En la fila del certificado nuevo selecciona **⋯ › Base64 certificate download** y guárdalo como `C:\Curso\recursos\saml-sp\certs\entra-nuevo.cer`.

**Paso 2.3.** Simula el error típico: en la fila del certificado nuevo selecciona **⋯ › Make certificate active** **sin** cambiar la aplicación. Espera un minuto e inicia sesión con `ana.lopez` en `https://localhost:5001`.

Resultado esperado: la aplicación muestra **Firma válida: FALLA** con el detalle "Ningún certificado de config.json valida la firma (¿se rotó el certificado?)" y la **huella del certificado nuevo**. En un portal real, todos los usuarios quedarían fuera al mismo tiempo.

**Paso 2.4.** Revierte: en la fila del certificado **anterior** selecciona **⋯ › Make certificate active**. Espera un minuto y confirma que `ana.lopez` vuelve a entrar con la firma válida.

---

## Tarea 3. Rotación coordinada sin interrupción

**Paso 3.1.** En [`config.json`](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/saml-sp/config.json) agrega el certificado nuevo a la lista de confianza y guarda:

```json
  "certificados_idp": ["certs/entra-actual.cer", "certs/entra-nuevo.cer"],
```

Reinicia la aplicación (**Ctrl+C** y `python app.py`). En `https://localhost:5001` la tabla de certificados muestra **dos** huellas.

**Paso 3.2.** Prueba con `ana.lopez`: la firma es válida y el detalle dice "verificada con certs/entra-actual.cer". La aplicación ya está lista para cualquiera de los dos.

**Paso 3.3.** En Entra, activa el certificado nuevo (**⋯ › Make certificate active**). Espera un minuto y prueba de nuevo.

Resultado esperado:

```text
Firma válida (respuesta o assertion)    OK    Respuesta: sin firma · Assertion: válida
Firma de la assertion   válida: Firma RSA-SHA-256 verificada con certs/entra-nuevo.cer
Huella del certificado  4F1A8B2C...C9D2
```

**Paso 3.4.** Retira el certificado anterior de la aplicación: deja solo el nuevo en [`config.json`](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/saml-sp/config.json), guarda, reinicia y prueba de nuevo (debe seguir funcionando).

```json
  "certificados_idp": ["certs/entra-nuevo.cer"],
```

**Paso 3.5.** En Entra, en la fila del certificado anterior (Inactive) selecciona **⋯ › Delete certificate** y confirma.

| Momento | Riesgo si se omite |
|---|---|
| Entregar el certificado al SP **antes** de activarlo | Interrupción total del SSO (Paso 2.3) |
| Validar con usuarios de prueba después de activar | Problemas que llegan a la mesa de ayuda en lugar de detectarse en la ventana de cambio |
| Conservar el anterior hasta validar | Sin él no hay plan de regreso rápido |
| Eliminar el anterior al final | Certificados inactivos acumulados que confunden futuras rotaciones |

---

## Tarea 4. Opciones de firma e inventario final

**Paso 4.1.** En **Edit** del certificado cambia **Signing Option** a **Sign SAML response and assertion** y guarda. Prueba con `ana.lopez`.

Resultado esperado en la aplicación: `Respuesta: válida · Assertion: válida`.

| Signing Option | Qué firma | Lo que muestra la aplicación |
|---|---|---|
| Sign SAML assertion (predeterminada) | Solo la assertion | Respuesta: sin firma · Assertion: válida |
| Sign SAML response | Solo el mensaje Response | Respuesta: válida · Assertion: sin firma |
| Sign SAML response and assertion | Ambos | Respuesta: válida · Assertion: válida |

**Paso 4.2.** Regresa la opción a **Sign SAML assertion** y guarda.

**Paso 4.3.** Ejecuta de nuevo [`./inventario-certificados.ps1 -Dias 1200`](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/scripts/inventario-certificados.ps1). Resultado esperado: una sola fila, con la huella nueva, `Activo = True` y alrededor de 730 días.

> **Reto opcional.** Con Microsoft Graph PowerShell crea un certificado inactivo sin usar el portal (`Add-MgServicePrincipalTokenSigningCertificate`, ver la presentación del Módulo 2) y compruébalo en la página **SAML Certificates**. Elimínalo al terminar.

---

## Resultado esperado

| Comprobación | Resultado |
|---|---|
| Rotación no coordinada (Paso 2.3) | Firma inválida, con la huella del certificado nuevo |
| Rotación coordinada (Tarea 3) | Sin fallas en ningún momento |
| Certificados en Entra al final | Uno solo, el nuevo, activo, con vencimiento a dos años |
| [`config.json`](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/saml-sp/config.json) al final | Solo `certs/entra-nuevo.cer` |
| Notificaciones | Dos destinatarios |

**Lista de verificación**

- [ ] Agregué un destinatario de notificaciones.
- [ ] Vi la falla de una rotación no coordinada y la revertí.
- [ ] Roté el certificado sin interrupción y retiré el anterior en ambos lados.
- [ ] Comparé las tres opciones de firma.
- [ ] Consulté el inventario con [`inventario-certificados.ps1`](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/scripts/inventario-certificados.ps1).

## Archivos completos

**[`C:\Curso\recursos\saml-sp\config.json`](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/saml-sp/config.json)** (también en `soluciones\saml-sp-config-practica3.json`)

```json
{
  "puerto": 5001,
  "sp_entity_id": "https://saml-test.contoso.com/sp",
  "acs_url": "https://localhost:5001/saml/acs",
  "idp_login_url": "https://login.microsoftonline.com/2b6c4f1e-7a2d-4c1b-9e35-0d8a3f6c1e41/saml2",
  "idp_entity_id": "https://sts.windows.net/2b6c4f1e-7a2d-4c1b-9e35-0d8a3f6c1e41/",
  "nameid_formato": "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress",
  "certificados_idp": ["certs/entra-nuevo.cer"],
  "relay_state": "/",
  "tolerancia_reloj_segundos": 120
}
```

**[`C:\Curso\recursos\scripts\inventario-certificados.ps1`](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/scripts/inventario-certificados.ps1)** (se usa sin cambios)

```powershell
param(
    [int]$Dias = 90
)

Connect-MgGraph -Scopes "Application.Read.All" -NoWelcome

$apps = Get-MgServicePrincipal -All -Property id,displayName,preferredSingleSignOnMode,keyCredentials,preferredTokenSigningKeyThumbprint |
    Where-Object PreferredSingleSignOnMode -eq "saml"

$filas = foreach ($sp in $apps) {
    foreach ($k in ($sp.KeyCredentials | Where-Object Usage -eq "Verify")) {
        $huella = ($k.CustomKeyIdentifier | ForEach-Object { $_.ToString("X2") }) -join ""
        [pscustomobject]@{
            Aplicacion = $sp.DisplayName
            Huella     = $huella
            Activo     = ($huella -eq $sp.PreferredTokenSigningKeyThumbprint)
            Vence      = $k.EndDateTime.ToString("yyyy-MM-dd")
            Dias       = [int]($k.EndDateTime - (Get-Date)).TotalDays
        }
    }
}

$filas | Where-Object Dias -lt $Dias | Sort-Object Dias | Format-Table -AutoSize
Write-Host "Aplicaciones SAML: $($apps.Count) · certificados con menos de $Dias días: $(($filas | Where-Object Dias -lt $Dias).Count)"
```

## Problemas comunes

| Síntoma | Causa | Solución |
|---|---|---|
| La firma sigue validando con el certificado anterior tras activar el nuevo | El cambio tarda unos minutos en propagarse | Espera uno o dos minutos y usa una ventana InPrivate nueva |
| La tabla de certificados muestra "no existe" | El nombre del archivo no coincide con [`config.json`](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/saml-sp/config.json) | Revisa el nombre y la carpeta `certs` |
| Error al leer el certificado | Se descargó el formato **Federation Metadata XML** | Descarga **Certificate (Base64)** o **Base64 certificate download** |
| No aparece **Make certificate active** | El certificado ya está activo | Usa el menú ⋯ de la otra fila |
| [`inventario-certificados.ps1`](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/scripts/inventario-certificados.ps1) no muestra filas | `-Dias` es menor que los días restantes | Ejecuta con `-Dias 1200` |
