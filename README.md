# Integración avanzada de aplicaciones e identidades con Microsoft Entra · Guía de laboratorios (MIC_IA_APP_ME_BB)

Prácticas del curso sobre el caso **Contoso**, una empresa que integra con Microsoft Entra sus aplicaciones SaaS, sus aplicaciones del centro de datos, a sus proveedores y a sus clientes en línea. Cada módulo de la presentación tiene su carpeta con la guía de cada práctica en Markdown (`.md`) y en Word (`.docx`). Las aplicaciones de prueba, los scripts y los datos están en la carpeta `recursos`.

| Módulo | Práctica | Guía | Duración |
|---|---|---|---|
| 1. Arquitectura de integración de aplicaciones | 1. Preparación del ambiente y análisis de escenarios de integración | `Modulo01/Practica01_Preparacion_Analisis` | 45 min |
| 2. Federación y SSO mediante SAML 2.0 | 2. Integración de una aplicación personalizada mediante SAML 2.0 | `Modulo02/Practica02_Integracion_SAML` | 75 min |
| 2. Federación y SSO mediante SAML 2.0 | 3. Gestión y rotación de certificados SAML | `Modulo02/Practica03_Rotacion_Certificados` | 30 min |
| 3. Aprovisionamiento automático mediante SCIM 2.0 | 4. Aprovisionamiento automático mediante SCIM 2.0 | `Modulo03/Practica04_Aprovisionamiento_SCIM` | 100 min |
| 4. Application proxy | 5. Publicación segura de una aplicación privada | `Modulo04/Practica05_Publicacion_App_Proxy` | 70 min |
| 4. Application proxy | 6. Configuración de SSO para una aplicación heredada | `Modulo04/Practica06_SSO_KCD_Encabezados` | 60 min |
| 5. External ID | 7. Implementación de colaboración B2B | `Modulo05/Practica07_Colaboracion_B2B` | 45 min |
| 5. External ID | 8. Federación de clientes con Microsoft Entra External ID | `Modulo05/Practica08_External_ID_Clientes` | 90 min |
| 6. Diagnóstico y operación | 9. Diagnóstico de una integración con errores | `Modulo06/Practica09_Diagnostico` | 45 min |

## Cómo empezar

1. Tu ambiente lo prepara soporte con la guía de instalación del curso (SUG): estación **LAB-CLIENT**, servidor **LAB-SRV01**, tenant de trabajo con licencias, endpoint SCIM y external tenant.
2. La carpeta `recursos` está en `C:\Curso\recursos` de LAB-CLIENT, con el entorno de Python en `C:\Curso\.venv`.
3. Haz las prácticas en orden: la 3 usa la aplicación de la 2; la 4 y la 7 agregan aprovisionamiento e invitados a esa misma aplicación; la 6 continúa la 5, y la 9 diagnostica lo construido en las anteriores.
4. Anota los datos de tu ambiente en `recursos/datos/mis-datos.txt` desde la Práctica 1.

## Estructura

```text
MIC_IA_APP_ME_BB/
├── Modulo01/ … Modulo06/        guía de cada práctica (.md y .docx)
└── recursos/                    carpeta de trabajo (C:\Curso\recursos en LAB-CLIENT)
    ├── requirements.txt         bibliotecas de Python de las aplicaciones de prueba
    ├── saml-sp/                 aplicación SAML de prueba (service provider): valida firma, audiencia y vigencia
    │   ├── app.py, config.json, generar_certificado_https.py
    │   └── certs/               certificado HTTPS de localhost y certificados de firma de Entra
    ├── scim-endpoint/           endpoint SCIM 2.0 de prueba (Azure App Service): /scim/v2, /registro, /cuentas
    ├── oidc-app/                tienda en línea (OIDC con MSAL) para el external tenant
    ├── scripts/                 verificar-ambiente, inventario-certificados, invitar-externos,
    │   │                        reporte-salud y carga-rrhh (Graph PowerShell)
    │   └── instructor/          fallas y guía de la Práctica 9 (uso del instructor)
    ├── datos/                   escenarios de Contoso, matriz de integración, invitados, lote de RR. HH.,
    │                            bitácora de diagnóstico, logotipo y mis-datos.txt
    └── soluciones/              archivos completos esperados (matriz, config.json, bitácora)
```

## Nota sobre los resultados esperados

Los identificadores (Tenant ID, huellas, object ID) y las fechas de los resultados esperados son ejemplos: en tu tenant serán distintos. Los nombres de menús del Microsoft Entra admin center se escriben en inglés y pueden variar ligeramente con las actualizaciones del portal.
