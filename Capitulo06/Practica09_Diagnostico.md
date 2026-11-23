# Práctica 9. Diagnóstico de una integración con errores

**Módulo 6 · Diagnóstico y operación de integraciones** · Duración aproximada: **45 minutos**

## Objetivos

Al terminar la práctica podrás:

- Obtener una vista general de la salud de las integraciones con [`reporte-salud.ps1`](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/scripts/reporte-salud.ps1).
- Aplicar un método ordenado: síntoma → ubicación → evidencia → hipótesis → corrección → validación.
- Usar sign-in logs, audit logs, provisioning logs, la aplicación de prueba y Provision on demand para encontrar la causa raíz.
- Corregir cinco fallas de SAML, claims, certificados, aprovisionamiento y acceso, y documentarlas.

## Antes de empezar

| Requisito | Cómo comprobarlo |
|---|---|
| Prácticas 2, 3, 4 y 7 terminadas | El portal de prueba, el aprovisionamiento y los invitados funcionan |
| Fallas aplicadas con el script de la práctica | El instructor las aplica a todo el grupo y te avisa, o te pide ejecutar `C:\Curso\recursos\scripts\instructor\fallas-practica9.ps1` **sin abrir el archivo** (inicia sesión con tu cuenta y acepta los permisos) |
| Aplicación de prueba en ejecución | `python app.py` en `C:\Curso\recursos\saml-sp` |

> **Cómo usar esta guía.** No hay pasos con la respuesta: cada caso describe lo que **reporta el usuario**. Usa el método de la Tarea 2 y anota todo en la bitácora. Al final hay **pistas** por si te atoras; consúltalas solo después de 8 minutos en un caso.

**Archivos que se modifican en esta práctica**

| Archivo (en `C:\Curso\recursos`) | Qué haces |
|---|---|
| [`datos\bitacora-diagnostico.csv`](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/datos/bitacora-diagnostico.csv) | Registras síntoma, evidencia, causa, corrección y validación de cada caso |
| `salidas\*.csv` | Los genera [`reporte-salud.ps1`](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/scripts/reporte-salud.ps1) (archivos nuevos) |

---

## Contexto

Es lunes y la mesa de ayuda de Contoso recibió cinco reportes sobre el **Portal de Proveedores (Lab)**. Durante el fin de semana alguien hizo cambios "de mantenimiento". Tu tarea es restablecer el servicio y documentar cada caso.

| Caso | Reporte recibido |
|---|---|
| 1 | "Cuando entro al portal desde su página (botón Iniciar sesión) Microsoft me muestra un error con un código AADSTS." — Ana López |
| 2 | "Desde el viernes el portal no reconoce bien a los usuarios: o llegan con un identificador que no es su correo, o los compradores ya no tienen sus permisos." — Fabricante del portal |
| 3 | "Nadie puede entrar al portal; dice que la firma no es válida." — Mesa de ayuda (llega después de corregir el caso 1) |
| 4 | "Mi cuenta del portal ya no se actualiza y la de Luis aparece inactiva." — Compras |
| 5 | "Ayer entraba al portal y hoy me dice que no tengo acceso." — Proveedor Sur (`cuenta.labXX@gmail.com`) |

---

## Tarea 1. Vista general

**Paso 1.1.** En PowerShell 7 ejecuta el reporte de salud:

```powershell
cd C:\Curso\recursos\scripts
./reporte-salud.ps1 -Horas 4
```

| Sección del reporte | Qué te dice |
|---|---|
| 1. Errores de inicio de sesión | Códigos AADSTS por aplicación en las últimas horas |
| 2. Cambios en aplicaciones | **Quién cambió qué** en los últimos días (audit logs) |
| 3. Aprovisionamiento | Estado del job, cuarentena y resultado del último ciclo |
| 4. Certificados | Certificados SAML que vencen pronto |

Los archivos CSV quedan en `C:\Curso\recursos\salidas`. Abre `cambios-aplicaciones.csv`: es la lista de sospechosos.

**Paso 1.2.** Abre [`datos\bitacora-diagnostico.csv`](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/datos/bitacora-diagnostico.csv) en VS Code. Lo completarás caso por caso.

---

## Tarea 2. Método de diagnóstico

Para cada caso sigue estos pasos y anótalos en la bitácora:

| Paso | Pregunta | Herramientas |
|---|---|---|
| 1. Síntoma exacto | ¿Qué usuario, qué aplicación, qué hora y qué mensaje? ¿Uno o todos? | Reproduce en una ventana InPrivate |
| 2. Ubicar el error | ¿La página de error es de Microsoft o de la aplicación? | Si es de Microsoft: solicitud, asignación o política. Si es de la aplicación: lo que contiene la respuesta |
| 3. Evidencia | ¿Qué dicen los registros? | Sign-in logs (código y causa), audit logs (cambios), provisioning logs, aplicación de prueba, SAML-tracer |
| 4. Hipótesis | ¿Qué cambio explica **todo** el síntoma? | Compara con la configuración final de las prácticas anteriores |
| 5. Corrección | Un solo cambio a la vez | Portal o Graph PowerShell |
| 6. Validación | ¿Desapareció el síntoma con el mismo usuario? | Repite la prueba original |

---

## Tarea 3. Resolver los casos

Resuelve los casos en orden (el 3 solo se ve después de corregir el 1).

**Caso 1.** Reproduce con `ana.lopez` desde `https://localhost:5001` › **Iniciar sesión**.

**Caso 2.** Inicia sesión con `ana.lopez` y revisa en la aplicación de prueba el NameID y el claim `role` contra los requisitos del fabricante (Práctica 2).

**Caso 3.** Después de corregir el caso 1, inicia sesión con `ana.lopez` y revisa la validación de la firma y la huella.

**Caso 4.** Usa **Provision on demand** con `ana.lopez` y revisa cada paso; luego revisa el estado de `luis.mendez` en `https://scim-labXX.azurewebsites.net/cuentas?token=<token>`.

**Caso 5.** Reproduce con `cuenta.labXX@gmail.com` (código por correo) y busca su intento en los sign-in logs (filtro **User type = Guest**).

Después de cada corrección, valida con el mismo usuario y completa la fila de la bitácora.

> **Reto opcional.** Ejecuta de nuevo [`./reporte-salud.ps1 -Horas 4`](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/scripts/reporte-salud.ps1) y compara con el primer reporte: la sección 1 debe mostrar los errores ya resueltos (anteriores a tus correcciones) y no deben aparecer nuevos.

---

## Resultado esperado

| Caso | Validación |
|---|---|
| 1 | Inicio SP-initiated de `ana.lopez` sin error |
| 2 | NameID = correo real para empleados e invitados |
| 3 | Firma válida en la aplicación de prueba |
| 4 | Provision on demand de `ana.lopez` sin "out of scope"; cuentas de Compras activas |
| 5 | El invitado de Gmail entra con `perfil = PROVEEDOR` |

**Lista de verificación**

- [ ] Generé el reporte de salud y usé los audit logs para ubicar cambios.
- [ ] Apliqué el método de diagnóstico en los cinco casos.
- [ ] Corregí cada falla con un solo cambio y validé con el mismo usuario.
- [ ] Completé la bitácora.

## Pistas (consúltalas solo si te atoras)

| Caso | Pista |
|---|---|
| 1 | El código del error te dice qué valor compara Entra. Compara letra por letra (mayúsculas, barra final, número) la URL de la solicitud con las Reply URL registradas |
| 2 | Compara con la Práctica 2: ¿qué atributo y formato tiene hoy el **Unique User Identifier**? ¿El valor de `role` coincide con el **Value** de los App roles que espera el portal? |
| 3 | La aplicación muestra la huella del certificado que firmó. ¿Está en [`config.json`](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/saml-sp/config.json)? ¿Cuál está activo en **SAML Certificates**? |
| 4 | Lee el paso **Determine if user is in scope** y compáralo con el valor real del departamento |
| 5 | ¿El invitado sigue siendo miembro del grupo asignado? Revisa los audit logs del grupo |

## Archivos completos

**[`C:\Curso\recursos\datos\bitacora-diagnostico.csv`](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/datos/bitacora-diagnostico.csv)** (consúltalo al terminar; también en `soluciones\bitacora-diagnostico-solucion.csv`)

```text
Caso,Sintoma_observado,Evidencia_y_registro,Causa_raiz,Correccion_aplicada,Validacion
1,Al iniciar desde el portal aparece AADSTS50011,Mensaje de error y sign-in log con codigo 50011; la URL solicitada es https://localhost:5001/saml/acs; audit log: Update application (Reply URLs),La Reply URL registrada se altero (barra final; /saml/acs2 o mayusculas /SAML/ACS segun el equipo),Reply URL corregida a https://localhost:5001/saml/acs en Basic SAML Configuration,Inicio SP-initiated de ana.lopez exitoso
2,El portal no reconoce bien a los usuarios,Aplicacion de prueba: NameID = UPN con formato persistent (variante A) o role = Compradores (variante B); audit log: Update service principal o Update application,Variante A: Name ID cambiado a user.userprincipalname. Variante B: Value del app role Comprador cambiado a Compradores,Variante A: Name ID user.mail con formato Email address. Variante B: Value del rol restablecido a Comprador,NameID = correo y role = Comprador para ana.lopez
3,Ningun usuario puede entrar; la aplicacion reporta firma invalida,Aplicacion de prueba: Firma FALLA con huella desconocida; SAML Certificates: certificado CN=Mantenimiento activo; audit log del cambio,Se activo un certificado nuevo sin entregarlo a la aplicacion,Se reactivo el certificado anterior (alternativa: descargar el nuevo y agregarlo a config.json),Firma valida con certs/entra-nuevo.cer
4,Las cuentas de Compras aparecen inactivas o no se actualizan en el portal,Provision on demand de ana: fuera de alcance; scoping filter department EQUALS Compra,Error de captura en el scoping filter,Clausula corregida a Compras,Provision on demand de ana: Update u Other con usuario activo
5,Un proveedor recibe AADSTS50105,Sign-in log del invitado con codigo 50105; GRP-Proveedores sin el invitado; audit log: Remove member from group,El invitado fue retirado del grupo asignado,Invitado agregado de nuevo a GRP-Proveedores,Inicio de sesion del invitado exitoso con perfil PROVEEDOR
```

**[`C:\Curso\recursos\scripts\reporte-salud.ps1`](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/scripts/reporte-salud.ps1)**: se usa sin cambios (ver la carpeta `scripts`).

## Problemas comunes

| Síntoma | Causa | Solución |
|---|---|---|
| [`reporte-salud.ps1`](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/scripts/reporte-salud.ps1) pide permisos nuevos | Usa `AuditLog.Read.All` además de los permisos anteriores | Acepta el consentimiento con tu cuenta de administración |
| El reporte no muestra errores | Los inicios de sesión fallidos tardan unos minutos en aparecer en los registros | Reproduce el error, espera 3 a 5 minutos y vuelve a ejecutar |
| Corregí el caso 1 y ahora falla la firma | Es el caso 3: había dos fallas en la misma ruta | Continúa con el caso 3 |
| El caso 4 no cambia tras corregir el filtro | El ciclo incremental aún no corre | Usa Provision on demand o **Restart provisioning** |
| El invitado sigue con 50105 tras agregarlo al grupo | Se reutilizó la sesión | Usa una ventana InPrivate nueva |
