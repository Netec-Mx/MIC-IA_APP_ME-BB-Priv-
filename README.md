<a href="https://netec.com">
  <img src="https://static.wixstatic.com/media/96edd2_934dddb3230b4b16b1d1c56c51143738~mv2.png" alt="Logo de Netec" width="300"/>
</a>

# Integración avanzada de aplicaciones e identidades con Microsoft Entra

## Plataforma de laboratorios

Te damos la bienvenida a la **plataforma de laboratorios** del curso **Integración avanzada de aplicaciones e identidades con Microsoft Entra**. Aquí podrás explorar diferentes tecnologías a través de prácticas guiadas. ¡Desarrolla tus habilidades y lleva tus conocimientos al siguiente nivel!

## Lista de laboratorios

Cada uno de estos laboratorios está diseñado para ofrecerte una experiencia práctica. Haz clic en los enlaces para comenzar.

### Módulo 1. Arquitectura de integración de aplicaciones con Microsoft Entra

#### [Práctica 1. Preparación del ambiente y análisis de escenarios de integración](Capitulo01/Practica01_Preparacion_Analisis.md)

  - **Descripción**: Verificación del tenant, licencias, roles y usuarios de prueba que usarán las prácticas 2 a 9; análisis de aplicaciones SaaS, propietarias y on-premises para elegir el mecanismo de autenticación, SSO y aprovisionamiento.

  - ⏱️ **Duración estimada**: 45 min.

  - 📂 **Recursos**:
    - [recursos/scripts/verificar-ambiente.ps1](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/scripts/verificar-ambiente.ps1)
    - [recursos/datos/mis-datos.txt](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/datos/mis-datos.txt)
    - [recursos/datos/escenarios-contoso.md](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/datos/escenarios-contoso.md)
    - [recursos/datos/matriz-integracion.csv](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/datos/matriz-integracion.csv)
    - [recursos/soluciones/matriz-integracion-solucion.csv](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/soluciones/matriz-integracion-solucion.csv)

### Módulo 2. Federación y SSO mediante SAML 2.0

#### [Práctica 2. Integración de una aplicación personalizada mediante SAML 2.0](Capitulo02/Practica02_Integracion_SAML.md)

  - **Descripción**: Aplicación fuera de la galería, SSO SAML, NameID y claims según requisitos, asignación de usuarios y validación de las assertions.

  - ⏱️ **Duración estimada**: 75 min.

  - 📂 **Recursos**:
    - [recursos/requirements.txt](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/requirements.txt)
    - [recursos/saml-sp/app.py](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/saml-sp/app.py)
    - [recursos/saml-sp/config.json](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/saml-sp/config.json)
    - [recursos/saml-sp/generar_certificado_https.py](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/saml-sp/generar_certificado_https.py)
    - [recursos/saml-sp/certs/LEEME.txt](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/saml-sp/certs/LEEME.txt)
    - [recursos/datos/mis-datos.txt](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/datos/mis-datos.txt)

#### [Práctica 3. Gestión y rotación de certificados SAML](Capitulo02/Practica03_Rotacion_Certificados.md)

  - **Descripción**: Revisión del certificado de firma, preparación de la renovación y estrategia de transición sin interrupción del SSO.

  - ⏱️ **Duración estimada**: 30 min.

  - 📂 **Recursos**:
    - [recursos/saml-sp/app.py](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/saml-sp/app.py)
    - [recursos/saml-sp/config.json](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/saml-sp/config.json)
    - [recursos/scripts/inventario-certificados.ps1](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/scripts/inventario-certificados.ps1)

### Módulo 3. Aprovisionamiento automático mediante SCIM 2.0

#### [Práctica 4. Aprovisionamiento automático mediante SCIM 2.0](Capitulo03/Practica04_Aprovisionamiento_SCIM.md)

  - **Descripción**: Aprovisionamiento hacia una aplicación compatible con SCIM, mappings y scoping filters, usuarios de prueba y análisis de los registros.

  - ⏱️ **Duración estimada**: 100 min.

  - 📂 **Recursos**:
    - [recursos/datos/mis-datos.txt](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/datos/mis-datos.txt)
    - [recursos/scripts/carga-rrhh.ps1](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/scripts/carga-rrhh.ps1)
    - [recursos/datos/lote-rrhh.json](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/datos/lote-rrhh.json)

### Módulo 4. Acceso seguro a aplicaciones privadas con Microsoft Entra application proxy

#### [Práctica 5. Publicación segura de una aplicación privada](Capitulo04/Practica05_Publicacion_App_Proxy.md)

  - **Descripción**: Publicación con application proxy, asignación de usuarios, preautenticación con Entra y validación del acceso desde una red externa.

  - ⏱️ **Duración estimada**: 70 min.

  - 📂 **Recursos**:
    - [recursos/datos/mis-datos.txt](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/datos/mis-datos.txt)

#### [Práctica 6. Configuración de SSO para una aplicación heredada](Capitulo04/Practica06_SSO_KCD_Encabezados.md)

  - **Descripción**: SSO con KCD y con encabezados; análisis del flujo entre Microsoft Entra, el conector y las aplicaciones privadas.

  - ⏱️ **Duración estimada**: 60 min.

  - 📂 **Recursos**: esta práctica no utiliza archivos de la carpeta recursos.

### Módulo 5. Microsoft Entra External ID y federación de identidades externas

#### [Práctica 7. Implementación de colaboración B2B](Capitulo05/Practica07_Colaboracion_B2B.md)

  - **Descripción**: Incorporación de usuarios externos, acceso a una aplicación empresarial y prueba de la autenticación con una identidad externa.

  - ⏱️ **Duración estimada**: 45 min.

  - 📂 **Recursos**:
    - [recursos/scripts/invitar-externos.ps1](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/scripts/invitar-externos.ps1)
    - [recursos/datos/invitados.csv](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/datos/invitados.csv)
    - [recursos/saml-sp/app.py](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/saml-sp/app.py)
    - [recursos/datos/mis-datos.txt](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/datos/mis-datos.txt)

#### [Práctica 8. Federación de clientes con Microsoft Entra External ID](Capitulo05/Practica08_External_ID_Clientes.md)

  - **Descripción**: Escenario de autenticación para usuarios externos, user flow de registro e inicio de sesión, proveedor de identidad externo y validación end-to-end.

  - ⏱️ **Duración estimada**: 90 min.

  - 📂 **Recursos**:
    - [recursos/oidc-app/app.py](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/oidc-app/app.py)
    - [recursos/oidc-app/config.json](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/oidc-app/config.json)
    - [recursos/datos/logo-contoso-banner.png](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/datos/logo-contoso-banner.png)
    - [recursos/datos/mis-datos.txt](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/datos/mis-datos.txt)

### Módulo 6. Diagnóstico y operación de integraciones

#### [Práctica 9. Diagnóstico de una integración con errores](Capitulo06/Practica09_Diagnostico.md)

  - **Descripción**: Fallos preconfigurados de SAML, claims, aprovisionamiento o acceso; uso de registros y herramientas de diagnóstico para identificar el origen y la corrección.

  - ⏱️ **Duración estimada**: 45 min.

  - 📂 **Recursos**:
    - [recursos/scripts/reporte-salud.ps1](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/scripts/reporte-salud.ps1)
    - [recursos/datos/bitacora-diagnostico.csv](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/datos/bitacora-diagnostico.csv)
    - [recursos/saml-sp/app.py](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/saml-sp/app.py)
    - [recursos/saml-sp/config.json](https://github.com/Netec-Mx/MIC-IA_APP_ME-BB-Priv-/blob/main/recursos/saml-sp/config.json)

---

## 📬 **Contacto y más información**

Si tienes alguna pregunta o necesitas más detalles, no dudes en [contactarnos](mailto:soporte@netec.com). También puedes encontrar más recursos en nuestra [página](https://netec.com).

---

¡Gracias por visitar nuestra plataforma! No olvides revisar todos los laboratorios y comenzar tu viaje de aprendizaje hoy mismo.
