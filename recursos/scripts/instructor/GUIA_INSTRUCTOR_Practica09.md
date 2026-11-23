# Guía del instructor · Práctica 9. Diagnóstico de una integración con errores

Uso exclusivo del instructor. Las cinco fallas se aplican **con un script**, sin pasos manuales, en dos modalidades:

| Modalidad | Cuándo usarla | Preparación | Tiempo con 30 participantes |
|---|---|---|---|
| **A. Instructor, todos los tenants** (recomendada) | Grupos grandes; los participantes no ven el script | Soporte registra la aplicación `Netec-Instructor-P9` en cada tenant (etapa 13 de la SUG) | Una ejecución de 3 a 5 minutos |
| **B. Cada participante** | Si no se hizo la etapa 13 | Ninguna | 1 minuto, en paralelo |

## Fallas que aplica `fallas-practica9.ps1`

| Falla | Qué cambia (API) | Síntoma | Corrección esperada |
|---|---|---|---|
| F1 | Reply URL de la app; una de tres variantes al azar: barra final, `/saml/acs2` o `/SAML/ACS` (Graph v1.0) | `AADSTS50011` al iniciar desde la aplicación | Reply URL `https://localhost:5001/saml/acs` |
| F2 | NameID = `user.userprincipalname`, formato Persistent (Custom Claims Policy, Graph **beta**). Si la API beta no responde: el valor del rol `Comprador` cambia a `Compradores` (Graph v1.0) | NameID incorrecto (`#EXT#` en invitados) **o** `role = Compradores` | NameID `user.mail` / Email address, **o** valor del rol `Comprador` |
| F3 | Certificado de firma nuevo `CN=Mantenimiento` y activo (Graph v1.0) | Firma inválida en la aplicación de prueba | Reactivar el certificado anterior |
| F4 | Scoping filter `department EQUALS Compra` en el esquema de sincronización (Graph v1.0) | Usuarios de Compras fuera de alcance | Cláusula `Compras` |
| F5 | Invitado de Gmail retirado de `GRP-Proveedores` (Graph v1.0) | `AADSTS50105` para el invitado | Agregarlo al grupo |

Cada ejecución guarda el estado original en un archivo JSON para restaurarlo con `restaurar-practica9.ps1`.

## Modalidad A. Instructor, todos los tenants

**Una sola vez por curso (antes de la preparación del ambiente)**, en tu equipo:

```powershell
$c = New-SelfSignedCertificate -Subject "CN=Netec-Instructor-P9" -CertStoreLocation Cert:\CurrentUser\My `
       -KeyExportPolicy Exportable -KeySpec Signature -KeyLength 2048 -NotAfter (Get-Date).AddMonths(6)
Export-Certificate -Cert $c -FilePath .\Netec-Instructor-P9.cer
$c.Thumbprint
```

Entrega a soporte **solo** `Netec-Instructor-P9.cer` (la clave privada se queda en tu equipo). Soporte ejecuta `registrar-app-instructor.ps1` en cada tenant (etapa 13 de la SUG) y te devuelve `tenants.csv`:

```text
"Participante","TenantId","ClientId","CertificateThumbprint","CorreoInvitado"
"01","2b6c4f1e-...","9d8e7f6a-...","A1B2C3...","cuenta.lab01@gmail.com"
"02","7c1d0e2f-...","4a5b6c7d-...","A1B2C3...","cuenta.lab02@gmail.com"
```

Completa la columna `CorreoInvitado` con la cuenta de Gmail que cada participante invitó en la Práctica 7.

**Al iniciar la Práctica 9** (por ejemplo, durante el receso previo):

```powershell
cd C:\Curso\recursos\scripts\instructor
./fallas-practica9.ps1 -Tenants .\tenants.csv
```

Salida esperada (un renglón por participante):

```text
Participante F1 F2          F3 F4 F5
------------ -- --          -- -- --
01           OK OK (NameID) OK OK OK
02           OK OK (NameID) OK OK OK
03           OK OK (NameID) OK ERROR: La aplicación no tiene aprovisionamiento configurado (Práctica 4) OK
```

Un `ERROR` en una falla no detiene las demás: indica que ese participante no terminó la práctica correspondiente; el caso queda fuera de su ejercicio. El resumen también se guarda en `estados\resumen-fallas.csv`.

**Al terminar** (o para los equipos que no completaron):

```powershell
./restaurar-practica9.ps1 -Tenants .\tenants.csv
```

## Modalidad B. Cada participante

Indica a los participantes que, **sin abrir el archivo**, ejecuten en PowerShell 7 de LAB-CLIENT:

```powershell
cd C:\Curso\recursos\scripts\instructor
./fallas-practica9.ps1
```

Inician sesión con su cuenta de participante y aceptan los permisos. El script solo muestra "Ambiente de la Práctica 9 preparado". El estado queda en `%LOCALAPPDATA%\MIC_P9\estado.json`; para revertir: `./restaurar-practica9.ps1`.

Las variantes al azar de F1 hacen que los equipos no tengan exactamente la misma falla, lo que reduce que se compartan respuestas.

## Requisitos y consideraciones

- F2 usa la API **beta** de Custom Claims Policy. Si Microsoft la cambia, el script aplica automáticamente la variante del rol; la bitácora de solución describe ambas.
- F4 requiere que la Práctica 4 haya creado el job de aprovisionamiento. Para que el caso 4 se note en `/cuentas`, los participantes usan Provision on demand (no hace falta esperar el ciclo).
- F5 requiere el invitado de Gmail de la Práctica 7.
- Los cambios quedan en los **audit logs** como hechos por `Netec-Instructor-P9` (modalidad A) o por la cuenta del participante (modalidad B): es parte de la evidencia que deben encontrar.

## Puntos de discusión al cierre

- Los **audit logs** identificaron en todos los casos quién hizo el cambio y cuándo: sin control de cambios, son la primera fuente de evidencia.
- Los casos 1 y 3 se encadenan: corregir un síntoma puede revelar otro. Validar siempre con el mismo usuario.
- El caso 4 muestra por qué existe el umbral de **eliminaciones accidentales**: un error de captura en un filtro puede desactivar cuentas en masa.
- El caso 5 recuerda que el acceso de invitados depende de la membresía en grupos asignados.
- La propia automatización de esta práctica es un ejemplo de operación a escala con Microsoft Graph y una aplicación con certificado (Módulo 6).
