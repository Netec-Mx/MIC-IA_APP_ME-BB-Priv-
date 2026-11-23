# Escenarios de integración de Contoso (Práctica 1)

Contoso es una empresa de distribución con 1 200 empleados, un centro de datos propio y una red de proveedores y clientes en línea. El área de identidad debe decidir cómo integrar con Microsoft Entra estas seis aplicaciones.

## 1. ServiceNow

- Mesa de servicio de TI contratada como SaaS. Aparece en la galería de Microsoft Entra.
- Todos los empleados la usan; los agentes de soporte tienen un rol distinto.
- Hoy cada alta la hace a mano el equipo de soporte; hay cuentas activas de personas que ya no trabajan en la empresa.

## 2. Portal de proveedores

- Aplicación web Java comprada a un tercero, hospedada por el fabricante. No está en la galería.
- El fabricante entrega un archivo de metadata SAML y pide que el usuario llegue identificado **por su correo**, con un atributo `role` (Comprador o Aprobador) y el número de empleado.
- Lo usan compradores de Contoso y también personal de los proveedores (otras empresas).
- El fabricante ofrece un endpoint SCIM 2.0 para crear y desactivar cuentas.

## 3. Intranet de Recursos Humanos

- Sitio ASP.NET en IIS dentro del centro de datos (`http://hr.contoso.local`), con autenticación integrada de Windows.
- Los empleados deben consultar recibos y vacaciones desde casa, sin VPN y con MFA.
- No se puede modificar el código de la aplicación.

## 4. ERP heredado

- Aplicación de finanzas y logística en el centro de datos. No implementa autenticación: confía en un encabezado HTTP con el nombre de usuario de dominio (`X-User`).
- Hoy un producto de control de acceso antiguo inyecta ese encabezado; se quiere retirar.

## 5. Aplicación móvil de ventas

- Desarrollo propio (iOS y Android) que consulta una API de pedidos también propia.
- El equipo de desarrollo puede usar cualquier biblioteca.

## 6. Tienda en línea

- Sitio web nuevo para clientes (consumidores). Se espera llegar a 30 000 clientes registrados el primer año.
- Los clientes deben poder registrarse solos con su correo o con Google, con la marca de Contoso.
- Mercadotecnia necesita saber el país del cliente y si acepta recibir promociones.
