Tipo de desarrollo: Estándar

Nombre del curso:

**Integración avanzada de aplicaciones e identidades con Microsoft Entra**  
**\[MIC\_IA\_APP\_ME\_BB\]**

# GUÍA DE INSTALACIÓN

## 1. Guía de Laboratorios en GitHub: https://github.com/Netec-Mx/MIC_IA_APP_ME_BB

## 2. Hardware (requerimientos de equipo por participante)

- Resumen de lo que se prepara para cada participante:
    - a. Dos máquinas virtuales en Microsoft Azure: LAB-CLIENT (estación de trabajo) y LAB-SRV01 (servidor con dominio, aplicaciones privadas y conector).
    - b. Un tenant de Microsoft Entra propio (tenant de trabajo) con siete licencias de Microsoft Entra ID P2 y una suscripción de Azure asociada a ese tenant.
    - c. Un Azure App Service (plan B1) para el endpoint SCIM de prueba.
    - d. Un external tenant de Microsoft Entra External ID.
    - e. Cuentas externas de prueba: Google, un buzón de correo externo y un usuario en el tenant socio (Fabrikam).
    - f. Toda la configuración es individual: ningún recurso se comparte entre participantes, salvo el tenant socio.

- LAB-CLIENT (estación de trabajo; simula a un usuario remoto, fuera de la red corporativa):
    - a. Tamaño: Standard D4s v5 (4 vCPU, 16 GiB de RAM).
    - b. Disco del sistema: SSD Premium de 128 GiB.
    - c. Red virtual propia (vnet-cliente, 10.20.0.0/16), sin peering con la red del servidor.
    - d. IP pública con RDP (3389) permitido solo desde las direcciones de Netec o del aula.
    - e. No se une al dominio.

- LAB-SRV01 (servidor de la red corporativa simulada):
    - a. Tamaño: Standard D4s v5 (4 vCPU, 16 GiB de RAM).
    - b. Disco del sistema: SSD estándar de 128 GiB.
    - c. Red virtual vnet-servidores (10.10.0.0/16, subred 10.10.1.0/24) con IP privada estática 10.10.1.4.
    - d. Funciones: controlador de dominio contoso.local, DNS, IIS (intranet y aplicación por encabezados), Microsoft Entra private network connector y agente de Microsoft Entra Cloud Sync.
    - e. IP pública solo para administración: RDP permitido únicamente desde la IP pública de LAB-CLIENT (y, si se requiere, desde la IP de soporte). Ningún puerto HTTP/HTTPS abierto hacia Internet.
    - f. En producción el conector se instala en servidores miembro dedicados; en el laboratorio comparte servidor con el dominio para reducir costo y pasos.

- Recursos de plataforma por participante:
    - a. Azure App Service con plan Linux B1 (Python 3.12) para el endpoint SCIM, publicado en https://scim-labXX.azurewebsites.net (XX = número de participante).
    - b. Arquitectura x64 y generación de VM V2 en ambas máquinas virtuales.

## 3. Software

- Sistema operativo de LAB-SRV01:
    - a. Sistema operativo: Windows Server 2022 Datacenter: Azure Edition
    - b. Publicador: MicrosoftWindowsServer
    - c. Oferta: WindowsServer
    - d. SKU: 2022-datacenter-azure-edition
    - e. Generación de VM: V2
    - f. Arquitectura: x64

- Sistema operativo de LAB-CLIENT:
    - a. Sistema operativo: Windows 11 Enterprise 24H2
    - b. Publicador: MicrosoftWindowsDesktop
    - c. Oferta: windows-11
    - d. SKU: win11-24h2-ent
    - e. Generación de VM: V2
    - f. Arquitectura: x64
    - g. Alternativa si no se cuentan con derechos de licencia de Windows Enterprise (sección 4): Windows Server 2022 Datacenter con Experiencia de escritorio.

- Software en LAB-CLIENT:
    - a. Microsoft Edge (incluido) y Mozilla Firefox, última versión estable.
    - b. Extensión SAML-tracer (Firefox y Edge) y extensión My Apps Secure Sign-in Extension (Edge).
    - c. PowerShell 7 (versión LTS vigente) y módulo Microsoft.Graph de PowerShell 2.x.
    - d. Visual Studio Code con las extensiones PowerShell, Python y REST Client.
    - e. Python 3.12 con un entorno virtual en C:\\Curso\\.venv y las bibliotecas de recursos\\requirements.txt (flask, lxml, cryptography, msal y requests), para la aplicación SAML de prueba, la tienda OIDC y las pruebas del endpoint SCIM.
    - f. Azure CLI 2.x y Git.
    - g. Carpeta de trabajo C:\\Curso\\recursos copiada del repositorio del curso.

- Roles y software en LAB-SRV01:
    - a. AD DS y DNS: bosque y dominio contoso.local (NetBIOS CONTOSO), con el sufijo UPN del tenant de trabajo.
    - b. IIS con Windows Authentication, ASP.NET 4.8 y consola de administración; sitios Intranet RRHH (http://hr.contoso.local) y ERP (http://erp.contoso.local).
    - c. Microsoft Entra private network connector (última versión) registrado en el tenant de trabajo, con HTTP/2 deshabilitado.
    - d. Agente de aprovisionamiento de Microsoft Entra Cloud Sync, sincronizando la OU Contoso-Usuarios.
    - e. Microsoft Edge (incluido) para usar el Microsoft Entra admin center durante la preparación.

- Recursos del curso (repositorio, carpeta recursos):
    - a. saml-sp: aplicación SAML de prueba (Python y Flask) que valida y muestra la assertion recibida.
    - b. scim-endpoint: endpoint SCIM 2.0 de prueba (Python 3.12 y Flask) con token configurable y registro de solicitudes.
    - c. oidc-app: tienda en línea OIDC de ejemplo (Python, Flask y MSAL) para el external tenant.
    - d. scripts: verificar-ambiente.ps1, inventario-certificados.ps1, invitar-externos.ps1, reporte-salud.ps1 y carga-rrhh.ps1 (los usan los participantes); carpeta instructor con las fallas de la Práctica 9.
    - e. datos: escenarios, matriz de integración, invitados.csv, lote-rrhh.json, bitácora de diagnóstico, logotipo y mis-datos.txt.
    - f. El repositorio lo publica Desarrollo de Contenidos; las etapas 9 y 10 de la sección 6 lo requieren.

- Conectividad requerida:
    - a. LAB-CLIENT: salida HTTPS a Internet, en particular a login.microsoftonline.com, entra.microsoft.com, portal.azure.com, myapps.microsoft.com, graph.microsoft.com, \*.ciamlogin.com, \*.msappproxy.net, accounts.google.com y console.cloud.google.com, además de github.com, www.powershellgallery.com y pypi.org.
    - b. LAB-SRV01: salida TCP 443 y 80 hacia las URLs que indica la documentación de Microsoft para el private network connector y para Cloud Sync (entre ellas \*.msappproxy.net, \*.servicebus.windows.net, login.microsoftonline.com y los servidores de CRL y OCSP), sin inspección ni terminación TLS.
    - c. Endpoint SCIM en App Service: accesible por HTTPS desde Internet (sin restricciones de IP).
    - d. Ningún puerto de entrada desde Internet hacia LAB-SRV01, salvo RDP desde LAB-CLIENT.

## 4. Licencias y suscripciones (por participante)

- Microsoft Entra ID (tenant de trabajo):
    - a. Siete licencias de Microsoft Entra ID P2 (incluye P1): cuenta del participante, cinco usuarios sincronizados y un usuario solo de nube.
    - b. P1 es el mínimo indispensable (acceso condicional, asignación de grupos a aplicaciones, grupos dinámicos y application proxy); P2 agrega Privileged Identity Management y revisiones de acceso.
    - c. Equivalentes válidos: Microsoft 365 E5 o Enterprise Mobility + Security E5.
    - d. Si se usa la prueba gratuita de Microsoft Entra ID P2 (30 días), activarla cerca del inicio del curso.

- Suscripción de Azure:
    - a. Una suscripción asociada al tenant de trabajo del participante (o el modelo equivalente del proveedor de laboratorios), con el participante como Owner o Contributor del grupo de recursos rg-entra-labXX.
    - b. Hospeda las dos máquinas virtuales, las redes, el App Service y la facturación de External ID.
    - c. Configurar el apagado automático de las máquinas virtuales para controlar el costo.

- Microsoft Entra External ID:
    - a. Facturación por usuarios activos al mes (MAU); los primeros 50,000 MAU del nivel básico no tienen costo, por lo que el laboratorio no genera cargos.
    - b. El tenant de trabajo se vincula a la suscripción de Azure para la facturación de los invitados B2B.
    - c. El external tenant se crea con la misma suscripción. Alternativa: prueba gratuita de 30 días sin suscripción de Azure (una por cuenta).
    - d. No se requieren complementos premium (SMS, ID Governance para externos).

- Sistemas operativos:
    - a. Windows Server 2022: licencia incluida en el costo por uso de la máquina virtual.
    - b. Windows 11 Enterprise en Azure: requiere derechos de Windows Enterprise E3/E5 (o Microsoft 365 E3/E5) por usuario; sin ellos, usar la alternativa con Windows Server para LAB-CLIENT.

- Cuentas y servicios externos (sin costo):
    - a. Cuenta de Google y proyecto en Google Cloud Console (Prácticas 7 y 8).
    - b. Buzón de correo externo (p. ej., Outlook.com) para la invitación con código de un solo uso.
    - c. Usuario en el tenant socio Fabrikam (uno por participante, en un tenant compartido que prepara Netec).
    - d. No se requieren PingAccess, F5 BIG-IP ni otros productos de terceros.

## 5. Cuentas que se crean por participante

- En LAB-SRV01 (dominio contoso.local):
    - a. labadmin: administrador local y, después de crear el dominio, CONTOSO\\labadmin (administrador del dominio).
    - b. Usuarios de prueba en la OU Contoso-Usuarios: alopez (Ana López, Compras), lmendez (Luis Méndez, Compras), mruiz (Marta Ruiz, Finanzas), pgarcia (Pedro García, Logística) y cdiaz (Carla Díaz, Recursos Humanos), con UPN nombre.apellido@labXX.onmicrosoft.com.
    - c. svc-hr-iis: cuenta de servicio del sitio Intranet RRHH (fuera de la OU sincronizada).

- En el tenant de trabajo (labXX.onmicrosoft.com):
    - a. participante@labXX.onmicrosoft.com: cuenta del participante, con rol Global Administrator de su tenant de laboratorio (en clase se analiza el mínimo privilegio).
    - b. Los cinco usuarios sincronizados desde contoso.local y el usuario solo de nube prueba.nube.
    - c. Grupos: Todos-Empleados (dinámico), DYN-Compras (dinámico), GRP-RRHH, GRP-Compras-Jefes, GRP-Logistica y GRP-Proveedores.
    - d. En el libro del curso los ejemplos usan el dominio contoso.com; en el laboratorio corresponden a labXX.onmicrosoft.com.

- Otras cuentas:
    - a. External tenant contosoclientesXX, administrado por la cuenta del participante.
    - b. Cuenta de Google y buzón externo de prueba.
    - c. socioXX@fabrikamlab.onmicrosoft.com en el tenant socio, con MFA registrada.

## 6. Preparación del ambiente paso a paso (repetir para cada participante)

- Etapa 0. Datos de planeación del participante:
    - a. Asignar el número de participante XX (01, 02…) y registrar: grupo de recursos rg-entra-labXX, región de Azure, dominio del tenant labXX.onmicrosoft.com y contraseñas (administrador de VM, DSRM, usuarios de prueba, svc-hr-iis y token SCIM).
    - b. En todos los comandos, reemplazar 01 por el número del participante y los valores entre \< \> por los datos reales.
    - c. Requisitos de quien prepara: Global Administrator del tenant de trabajo, Owner de la suscripción de Azure y una terminal con Azure CLI (Azure Cloud Shell sirve).

- Etapa 1. Infraestructura en Azure (Azure Cloud Shell, PowerShell):
    - a. Definir variables, grupo de recursos y redes:

      ```powershell
      $XX  = "01"
      $RG  = "rg-entra-lab$XX"
      $LOC = "eastus2"
      $ADM = "labadmin"
      $PASS = "<contraseña-administrador-vm>"
      az account set --subscription "<id-suscripcion>"
      az group create -n $RG -l $LOC
      az network vnet create -g $RG -n vnet-servidores --address-prefixes 10.10.0.0/16 `
        --subnet-name snet-servidores --subnet-prefixes 10.10.1.0/24
      az network vnet create -g $RG -n vnet-cliente --address-prefixes 10.20.0.0/16 `
        --subnet-name snet-cliente --subnet-prefixes 10.20.1.0/24
      ```

    - b. Crear la estación de trabajo LAB-CLIENT:

      ```powershell
      az vm create -g $RG -n LAB-CLIENT `
        --image MicrosoftWindowsDesktop:windows-11:win11-24h2-ent:latest `
        --size Standard_D4s_v5 --vnet-name vnet-cliente --subnet snet-cliente `
        --public-ip-sku Standard --nsg-rule RDP --license-type Windows_Client `
        --os-disk-size-gb 128 --storage-sku Premium_LRS `
        --admin-username $ADM --admin-password $PASS
      ```

    - c. Crear el servidor LAB-SRV01 con IP privada fija y sin reglas de entrada:

      ```powershell
      az vm create -g $RG -n LAB-SRV01 `
        --image MicrosoftWindowsServer:WindowsServer:2022-datacenter-azure-edition:latest `
        --size Standard_D4s_v5 --vnet-name vnet-servidores --subnet snet-servidores `
        --private-ip-address 10.10.1.4 --public-ip-sku Standard --nsg-rule NONE `
        --os-disk-size-gb 128 --storage-sku StandardSSD_LRS `
        --admin-username $ADM --admin-password $PASS
      ```

    - d. Restringir RDP: LAB-SRV01 solo acepta RDP desde LAB-CLIENT; LAB-CLIENT solo desde las IP de Netec o del aula (verificar el nombre de la regla con az network nsg rule list):

      ```powershell
      $ipCliente = az vm show -d -g $RG -n LAB-CLIENT --query publicIps -o tsv
      az network nsg rule create -g $RG --nsg-name LAB-SRV01NSG -n RDP-desde-cliente `
        --priority 100 --protocol Tcp --destination-port-ranges 3389 `
        --source-address-prefixes $ipCliente "<ip-soporte>" --access Allow
      az network nsg rule list -g $RG --nsg-name LAB-CLIENTNSG -o table
      az network nsg rule update -g $RG --nsg-name LAB-CLIENTNSG -n rdp `
        --source-address-prefixes "<ip-o-rango-netec>"
      ```

    - e. Programar el apagado automático (hora UTC):

      ```powershell
      az vm auto-shutdown -g $RG -n LAB-CLIENT --time 0400
      az vm auto-shutdown -g $RG -n LAB-SRV01  --time 0400
      ```

- Etapa 2. Controlador de dominio en LAB-SRV01:
    - a. Conectarse por RDP a LAB-SRV01 (desde LAB-CLIENT o desde la IP de soporte) con labadmin y abrir PowerShell como administrador:

      ```powershell
      Set-TimeZone -Id "Central Standard Time (Mexico)"
      Install-WindowsFeature AD-Domain-Services, DNS -IncludeManagementTools
      Install-ADDSForest -DomainName "contoso.local" -DomainNetbiosName "CONTOSO" -InstallDns `
        -SafeModeAdministratorPassword (Read-Host "Contraseña DSRM" -AsSecureString) -Force
      ```

    - b. El servidor se reinicia. En Cloud Shell, configurar el DNS de la red y reiniciar la VM:

      ```powershell
      az network vnet update -g $RG -n vnet-servidores --dns-servers 10.10.1.4
      az vm restart -g $RG -n LAB-SRV01
      ```

    - c. Iniciar sesión como CONTOSO\\labadmin y agregar el reenviador DNS de Azure:

      ```powershell
      Add-DnsServerForwarder -IPAddress 168.63.129.16
      ```

- Etapa 3. Usuarios, cuenta de servicio y registros DNS (LAB-SRV01, PowerShell como administrador):
    - a. Agregar el sufijo UPN del tenant, la OU y los usuarios de prueba:

      ```powershell
      $sfx = "lab01.onmicrosoft.com"
      Get-ADForest | Set-ADForest -UPNSuffixes @{Add = $sfx}
      New-ADOrganizationalUnit -Name "Contoso-Usuarios" -Path "DC=contoso,DC=local"
      $ou = "OU=Contoso-Usuarios,DC=contoso,DC=local"
      $pw = Read-Host "Contraseña de los usuarios de prueba" -AsSecureString
      $usuarios = @(
        @("alopez","Ana","López","ana.lopez","Compras","Compradora Sr.","EMP-00412"),
        @("lmendez","Luis","Méndez","luis.mendez","Compras","Gerente de Compras","EMP-00418"),
        @("mruiz","Marta","Ruiz","marta.ruiz","Finanzas","Analista de Finanzas","EMP-00233"),
        @("pgarcia","Pedro","García","pedro.garcia","Logística","Jefe de Almacén","EMP-00377"),
        @("cdiaz","Carla","Díaz","carla.diaz","Recursos Humanos","Generalista de RR. HH.","EMP-00105")
      )
      foreach ($u in $usuarios) {
        New-ADUser -Name "$($u[1]) $($u[2])" -GivenName $u[1] -Surname $u[2] -SamAccountName $u[0] `
          -UserPrincipalName "$($u[3])@$sfx" -EmailAddress "$($u[3])@$sfx" -Department $u[4] `
          -Title $u[5] -EmployeeID $u[6] -Path $ou -AccountPassword $pw -Enabled $true `
          -PasswordNeverExpires $true
      }
      ```

    - b. Crear la cuenta de servicio de la intranet (fuera de la OU sincronizada) y los registros DNS:

      ```powershell
      New-ADUser -Name "svc-hr-iis" -SamAccountName "svc-hr-iis" `
        -UserPrincipalName "svc-hr-iis@contoso.local" -Path "CN=Users,DC=contoso,DC=local" `
        -AccountPassword (Read-Host "Contraseña de svc-hr-iis" -AsSecureString) `
        -Enabled $true -PasswordNeverExpires $true
      Add-DnsServerResourceRecordA -ZoneName "contoso.local" -Name "hr"  -IPv4Address 10.10.1.4
      Add-DnsServerResourceRecordA -ZoneName "contoso.local" -Name "erp" -IPv4Address 10.10.1.4
      ```

    - c. No registrar el SPN ni configurar la delegación Kerberos: forman parte de la Práctica 6.

- Etapa 4. Aplicaciones privadas en IIS (LAB-SRV01, PowerShell como administrador):
    - a. Instalar IIS y crear las páginas de las dos aplicaciones:

      ```powershell
      Install-WindowsFeature Web-Server, Web-Windows-Auth, Web-Asp-Net45, Web-Mgmt-Console
      New-Item C:\inetpub\hr, C:\inetpub\erp -ItemType Directory -Force | Out-Null
      @'
      <%@ Page Language="C#" %>
      <html><body><h1>Intranet RR. HH.</h1>
      <p>Usuario: <%= User.Identity.Name %></p>
      <p>Metodo: <%= Request.ServerVariables["AUTH_TYPE"] %></p>
      </body></html>
      '@ | Set-Content C:\inetpub\hr\default.aspx -Encoding UTF8
      @'
      <%@ Page Language="C#" %>
      <html><body><h1>ERP heredado - encabezados recibidos</h1><table border="1">
      <% foreach (string k in Request.Headers.AllKeys) { %>
      <tr><td><%= k %></td><td><%= Server.HtmlEncode(Request.Headers[k]) %></td></tr>
      <% } %></table></body></html>
      '@ | Set-Content C:\inetpub\erp\default.aspx -Encoding UTF8
      ```

    - b. Crear el grupo de aplicaciones con la cuenta de servicio, los sitios y la autenticación de Windows:

      ```powershell
      Import-Module WebAdministration
      $svcPass = Read-Host "Contraseña de svc-hr-iis"
      New-WebAppPool -Name "hr-pool" | Out-Null
      Set-ItemProperty IIS:\AppPools\hr-pool -Name processModel `
        -Value @{userName = "CONTOSO\svc-hr-iis"; password = $svcPass; identityType = 3}
      icacls C:\inetpub\hr /grant "CONTOSO\svc-hr-iis:(OI)(CI)RX"
      New-Website -Name "Intranet RRHH" -PhysicalPath C:\inetpub\hr -HostHeader "hr.contoso.local" `
        -Port 80 -ApplicationPool "hr-pool"
      New-Website -Name "ERP" -PhysicalPath C:\inetpub\erp -HostHeader "erp.contoso.local" -Port 80
      $ah = "MACHINE/WEBROOT/APPHOST"
      $f  = "system.webServer/security/authentication"
      $p  = @{ PSPath = $ah; Location = "Intranet RRHH" }
      Set-WebConfigurationProperty @p -Filter "$f/anonymousAuthentication" -Name enabled -Value $false
      Set-WebConfigurationProperty @p -Filter "$f/windowsAuthentication" -Name enabled -Value $true
      Set-WebConfigurationProperty @p -Filter "$f/windowsAuthentication" `
        -Name useAppPoolCredentials -Value $true
      ```

    - c. Permitir la autenticación de Windows local hacia los nombres hr y erp (evita el error 401 por la comprobación de bucle invertido) y probar:

      ```powershell
      New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Lsa\MSV1_0" `
        -Name "BackConnectionHostNames" -PropertyType MultiString `
        -Value "hr.contoso.local", "erp.contoso.local" -Force
      (Invoke-WebRequest http://hr.contoso.local -UseDefaultCredentials -UseBasicParsing).Content
      #  Debe mostrar: Usuario: CONTOSO\labadmin
      (Invoke-WebRequest http://erp.contoso.local -UseBasicParsing).StatusCode    # 200
      ```

- Etapa 5. Tenant de trabajo (Microsoft Entra admin center, https://entra.microsoft.com):
    - a. Crear o asignar el tenant labXX.onmicrosoft.com y asociarle la suscripción de Azure del participante.
    - b. Adquirir o activar las siete licencias de Microsoft Entra ID P2 (Billing › Licenses).
    - c. Deshabilitar los valores predeterminados de seguridad: Entra ID › Overview › Properties › Manage security defaults › Disabled (el curso usa acceso condicional).
    - d. Vincular el tenant a la suscripción para External ID: External Identities › Overview › Linked subscriptions › seleccionar el tenant › Link subscription.
    - e. Crear la cuenta del participante con Microsoft Graph PowerShell (desde Cloud Shell o desde LAB-CLIENT después de la etapa 9):

      ```powershell
      Connect-MgGraph -Scopes "User.ReadWrite.All","RoleManagement.ReadWrite.Directory"
      $dom  = "lab01.onmicrosoft.com"
      $part = New-MgUser -DisplayName "Participante 01" -UserPrincipalName "participante@$dom" `
        -MailNickname "participante" -AccountEnabled -UsageLocation "MX" `
        -PasswordProfile @{ Password = "<contraseña-inicial>"; ForceChangePasswordNextSignIn = $true }
      $ga = Get-MgRoleManagementDirectoryRoleDefinition -Filter "displayName eq 'Global Administrator'"
      New-MgRoleManagementDirectoryRoleAssignment -PrincipalId $part.Id `
        -RoleDefinitionId $ga.Id -DirectoryScopeId "/"
      ```

    - f. En la suscripción de Azure, asignar al participante el rol Contributor sobre su grupo de recursos:

      ```powershell
      az role assignment create --assignee "participante@lab01.onmicrosoft.com" `
        --role Contributor --scope "/subscriptions/<id-suscripcion>/resourceGroups/rg-entra-lab01"
      ```

- Etapa 6. Sincronización con Microsoft Entra Cloud Sync (en LAB-SRV01):
    - a. En Edge de LAB-SRV01, iniciar sesión en el Microsoft Entra admin center con un Global Administrator del tenant: Entra ID › Entra Connect › Cloud sync › Agents › Download on-premises agent.
    - b. Ejecutar el instalador del agente de aprovisionamiento; en el asistente, iniciar sesión con la cuenta de Entra, elegir crear la gMSA y proporcionar CONTOSO\\labadmin como administrador del dominio.
    - c. En Cloud sync › New configuration › AD to Microsoft Entra ID sync, elegir contoso.local y crear la configuración.
    - d. Scoping filters: Selected organizational units › OU=Contoso-Usuarios,DC=contoso,DC=local.
    - e. Habilitar Password hash sync.
    - f. Attribute mapping: confirmar que department, title (jobTitle), mail y employeeID (employeeId) se sincronizan; si employeeId no aparece, agregar el mapeo directo employeeID → employeeId.
    - g. Usar Provision on demand con alopez para probar; después Review and enable. En unos minutos los cinco usuarios aparecen en Entra con UPN nombre.apellido@labXX.onmicrosoft.com.

- Etapa 7. Usuarios, licencias y grupos en Entra (Graph PowerShell):
    - a. Crear el usuario solo de nube, asignar ubicación de uso y licencias:

      ```powershell
      Connect-MgGraph -Scopes "User.ReadWrite.All","Group.ReadWrite.All",
                              "Organization.Read.All","Directory.ReadWrite.All"
      $dom = "lab01.onmicrosoft.com"
      New-MgUser -DisplayName "Prueba Nube" -UserPrincipalName "prueba.nube@$dom" `
        -MailNickname "prueba.nube" -AccountEnabled -UsageLocation "MX" -Department "Compras" `
        -PasswordProfile @{ Password = "<contraseña-usuarios>"; ForceChangePasswordNextSignIn = $false }
      $sku = (Get-MgSubscribedSku | Where-Object SkuPartNumber -eq "AAD_PREMIUM_P2").SkuId
      #  Con Microsoft 365 E5 usar "SPE_E5"; con EMS E5, "EMSPREMIUM".
      $cuentas = "ana.lopez","luis.mendez","marta.ruiz","pedro.garcia","carla.diaz",
                 "prueba.nube","participante"
      foreach ($c in $cuentas) {
        $u = Get-MgUser -UserId "$c@$dom"
        Update-MgUser -UserId $u.Id -UsageLocation "MX"
        Set-MgUserLicense -UserId $u.Id -AddLicenses @(@{SkuId = $sku}) -RemoveLicenses @()
      }
      ```

    - b. Crear los grupos de seguridad, los grupos dinámicos y las membresías:

      ```powershell
      $g = @{}
      foreach ($n in "GRP-RRHH","GRP-Compras-Jefes","GRP-Logistica","GRP-Proveedores") {
        $g[$n] = New-MgGroup -DisplayName $n -MailEnabled:$false `
                  -MailNickname $n.ToLower() -SecurityEnabled
      }
      New-MgGroup -DisplayName "DYN-Compras" -MailEnabled:$false -MailNickname "dyn-compras" `
        -SecurityEnabled `
        -GroupTypes "DynamicMembership" -MembershipRule 'user.department -eq "Compras"' `
        -MembershipRuleProcessingState "On"
      New-MgGroup -DisplayName "Todos-Empleados" -MailEnabled:$false -MailNickname "todos-empleados" `
        -SecurityEnabled `
        -GroupTypes "DynamicMembership" -MembershipRule 'user.userType -eq "Member"' `
        -MembershipRuleProcessingState "On"
      $m = @{ "GRP-RRHH" = "carla.diaz"; "GRP-Compras-Jefes" = "luis.mendez";
              "GRP-Logistica" = "pedro.garcia" }
      foreach ($k in $m.Keys) {
        $u = Get-MgUser -UserId "$($m[$k])@$dom"
        New-MgGroupMember -GroupId $g[$k].Id -DirectoryObjectId $u.Id
      }
      ```

    - c. GRP-Proveedores queda vacío: los invitados se agregan en la Práctica 7. La MFA de los usuarios de prueba la registra el participante en la Práctica 1 (Microsoft Authenticator habilitado en Authentication methods).

- Etapa 8. Private network connector (LAB-SRV01):
    - a. Deshabilitar HTTP/2 (requerido por application proxy en Windows Server 2019 y posteriores) y reiniciar:

      ```powershell
      New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\Http\Parameters" `
        -Name "EnableDefaultHTTP2" -PropertyType DWord -Value 0 -Force
      Restart-Computer
      ```

    - b. En el Microsoft Entra admin center (Edge de LAB-SRV01): Global Secure Access › Connect › Connectors (o Entra ID › Enterprise applications › Application proxy) › Download connector service; aceptar los términos y ejecutar el instalador.
    - c. Al terminar, iniciar sesión con un Global Administrator o Application Administrator del tenant para registrar el conector.
    - d. Crear el connector group CG-LAB y mover LAB-SRV01 a ese grupo; el conector debe aparecer como Active.
    - e. Verificar que los servicios del conector y del actualizador estén en ejecución:

      ```powershell
      Get-Service WAPCsvc, WAPCUpdaterSvc
      ```

    - f. No publicar aplicaciones: la publicación es parte de las Prácticas 5 y 6.

- Etapa 9. Software de LAB-CLIENT (RDP con labadmin, PowerShell como administrador):
    - a. Instalar el software con winget:

      ```powershell
      $ids = "Mozilla.Firefox","Microsoft.PowerShell","Microsoft.VisualStudioCode",
             "Python.Python.3.12","Microsoft.AzureCLI","Git.Git"
      foreach ($id in $ids) {
        winget install --id $id -e --silent --accept-package-agreements --accept-source-agreements
      }
      ```

    - b. Abrir una nueva ventana de PowerShell 7 (pwsh) como administrador e instalar el módulo de Graph, las extensiones de VS Code y el repositorio:

      ```powershell
      Install-Module Microsoft.Graph -Scope AllUsers -Force      # tarda varios minutos
      code --install-extension ms-vscode.powershell
      code --install-extension ms-python.python
      code --install-extension humao.rest-client
      git clone https://github.com/Netec-Mx/MIC_IA_APP_ME_BB C:\Curso\repo
      Copy-Item C:\Curso\repo\recursos C:\Curso\recursos -Recurse
      py -3.12 -m venv C:\Curso\.venv
      C:\Curso\.venv\Scripts\python -m pip install --upgrade pip
      C:\Curso\.venv\Scripts\python -m pip install -r C:\Curso\recursos\requirements.txt
      ```

    - c. Extensiones de navegador: SAML-tracer en Firefox (addons.mozilla.org) y en Edge (Chrome Web Store, permitiendo extensiones de otras tiendas); My Apps Secure Sign-in Extension en Edge (Edge Add-ons).
    - d. Repetir la instalación de las extensiones de VS Code y la configuración de navegadores en el perfil del usuario con el que trabajará el participante, si es distinto de labadmin.

- Etapa 10. Endpoint SCIM en Azure App Service (desde LAB-CLIENT o la terminal de soporte):
    - a. Desplegar el endpoint desde la carpeta del repositorio y configurar el token del participante:

      ```powershell
      az login
      cd C:\Curso\recursos\scim-endpoint
      az webapp up --name scim-lab01 --resource-group rg-entra-lab01 `
        --runtime "PYTHON:3.12" --sku B1 --location eastus2
      az webapp config set -g rg-entra-lab01 -n scim-lab01 `
        --startup-file "gunicorn --bind=0.0.0.0 --timeout 600 app:app"
      az webapp config appsettings set -g rg-entra-lab01 -n scim-lab01 `
        --settings SCIM_TOKEN="<token-scim-del-participante>"
      ```

    - b. Probar el endpoint (debe responder 200 con una lista vacía):

      ```powershell
      Invoke-RestMethod "https://scim-lab01.azurewebsites.net/scim/v2/Users" `
        -Headers @{ Authorization = "Bearer <token-scim-del-participante>" }
      ```

- Etapa 11. External tenant (Microsoft Entra admin center, con la cuenta del participante):
    - a. Entra ID › Overview › Manage tenants › Create › External › Continue › Use Azure Subscription.
    - b. Nombre: Contoso Clientes XX; dominio: contosoclientesXX; ubicación: la más cercana; suscripción y grupo de recursos del participante.
    - c. Review + create. La creación puede tardar hasta 30 minutos.
    - d. Si lo crea otra cuenta, invitar a participante@labXX.onmicrosoft.com al external tenant y asignarle el rol Global Administrator.
    - e. Alternativa sin suscripción: prueba gratuita de 30 días del external tenant.

- Etapa 12. Cuentas externas:
    - a. Google: cuenta de laboratorio por participante (o la cuenta personal del participante) y un proyecto vacío entra-labXX en https://console.cloud.google.com; el cliente OAuth se crea en las prácticas.
    - b. Correo externo: buzón de prueba (p. ej., externo.labXX@outlook.com) para el código de un solo uso.
    - c. Tenant socio (una sola vez por grupo): tenant fabrikamlab.onmicrosoft.com con un usuario socioXX por participante y MFA registrada.

- Etapa 13. Aplicación del instructor para la Práctica 9 (recomendada con más de 10 participantes):
    - a. Permite que el instructor aplique y revierta las fallas de la Práctica 9 en todos los tenants con una sola ejecución, sin pasos manuales.
    - b. El instructor entrega a soporte el certificado público Netec-Instructor-P9.cer (la clave privada se queda en su equipo).
    - c. En LAB-CLIENT de cada participante, con un Global Administrator de su tenant, ejecutar:

      ```powershell
      cd C:\Curso\recursos\scripts\instructor
      ./registrar-app-instructor.ps1 -Participante 01 -Certificado <ruta>\Netec-Instructor-P9.cer `
        -Salida <carpeta-compartida>\tenants.csv
      ```

    - d. El script registra la aplicación Netec-Instructor-P9 con el certificado, le otorga los permisos de aplicación Application.ReadWrite.All, Policy.ReadWrite.ApplicationConfiguration, Synchronization.ReadWrite.All, GroupMember.ReadWrite.All y User.Read.All (con consentimiento de administrador) y agrega una fila a tenants.csv.
    - e. Entregar tenants.csv al instructor; él agrega la columna CorreoInvitado después de la Práctica 7.
    - f. Al terminar el curso, eliminar la aplicación Netec-Instructor-P9 de cada tenant (o eliminar los tenants de laboratorio).

## 7. Verificación y entrega

- Verificación del ambiente (antes de iniciar el curso):
    - a. En LAB-SRV01, Invoke-WebRequest http://hr.contoso.local -UseDefaultCredentials muestra "Usuario: CONTOSO\\labadmin".
    - b. Desde LAB-CLIENT, http://hr.contoso.local no resuelve ni responde (la estación está fuera de la red corporativa).
    - c. Desde LAB-CLIENT, la conexión RDP a LAB-SRV01 funciona.
    - d. Cloud Sync muestra la configuración en estado Healthy y los cinco usuarios aparecen en Entra con department, jobTitle y employeeId.
    - e. Billing › Licenses muestra siete licencias P2 asignadas; los grupos DYN-Compras y Todos-Empleados tienen miembros.
    - f. El conector LAB-SRV01 aparece como Active en el grupo CG-LAB.
    - g. En LAB-CLIENT, C:\\Curso\\.venv\\Scripts\\python -c "import flask, lxml, cryptography, msal" termina sin errores, y Connect-MgGraph con la cuenta del participante funciona.
    - h. El endpoint SCIM responde 401 sin token y 200 con el token.
    - i. El external tenant está disponible y el participante puede cambiar a él.
    - j. Si se hizo la etapa 13: tenants.csv tiene una fila por participante y la aplicación Netec-Instructor-P9 aparece en App registrations con los permisos concedidos.

- Datos a entregar a cada participante:
    - a. IP pública de LAB-CLIENT y usuario labadmin con su contraseña; IP pública de LAB-SRV01 (para RDP desde LAB-CLIENT) y la cuenta CONTOSO\\labadmin.
    - b. Tenant de trabajo, cuenta participante@labXX.onmicrosoft.com y su contraseña inicial.
    - c. Contraseña común de los usuarios de prueba y de svc-hr-iis.
    - d. URL y token del endpoint SCIM.
    - e. Nombre del external tenant, cuenta de Google, buzón externo y usuario del tenant socio.

- Uso del ambiente por práctica:
    - a. Práctica 1: tenant de trabajo, licencias, roles, usuarios, grupos y registro de MFA.
    - b. Prácticas 2 y 3: aplicación SAML de prueba en LAB-CLIENT y Graph PowerShell.
    - c. Práctica 4: endpoint SCIM en App Service y grupo DYN-Compras.
    - d. Prácticas 5 y 6: LAB-SRV01 (IIS, conector y AD DS), acceso condicional y acceso desde LAB-CLIENT.
    - e. Práctica 7: tenant socio, cuenta de Google y buzón externo.
    - f. Práctica 8: external tenant, proyecto de Google Cloud y aplicación OIDC de ejemplo.
    - g. Práctica 9: el ambiente completo, con fallas preparadas por el instructor.

- ¿Es necesario que todo el software esté instalado antes de iniciar el curso? ¿O se hará a lo largo de éste?
    - a. El software y la infraestructura deben estar listos antes de iniciar el curso (etapas 0 a 13). Durante las prácticas solo se configuran los servicios de Microsoft Entra: aplicaciones, aprovisionamiento, publicación con application proxy, delegación Kerberos y External ID.
