# Práctica 6. SPN y delegación Kerberos (RBCD) para la Intranet RR. HH.
Import-Module ActiveDirectory

# 1. SPN del sitio en la cuenta que ejecuta el grupo de aplicaciones
setspn -S HTTP/hr.contoso.local CONTOSO\svc-hr-iis
setspn -S HTTP/hr CONTOSO\svc-hr-iis

# 2. Comprobar que el SPN no está duplicado
setspn -Q HTTP/hr.contoso.local

# 3. RBCD: la cuenta del sitio acepta delegación desde la cuenta de equipo del conector
$conector = Get-ADComputer -Identity "LAB-SRV01"
Set-ADUser -Identity "svc-hr-iis" -PrincipalsAllowedToDelegateToAccount $conector

# 4. Verificar
Get-ADUser -Identity "svc-hr-iis" -Properties servicePrincipalName, PrincipalsAllowedToDelegateToAccount |
    Format-List Name, servicePrincipalName, PrincipalsAllowedToDelegateToAccount

# 5. Aplicar sin esperar: renovar los tickets del conector
klist purge -li 0x3e4
Restart-Service WAPCsvc
