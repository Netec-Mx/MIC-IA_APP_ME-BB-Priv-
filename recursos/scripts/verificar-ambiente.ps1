<#
.SYNOPSIS
  Práctica 1. Verifica licencias, roles, usuarios, grupos y métodos de MFA del tenant de trabajo.
.DESCRIPTION
  Solo lee información (no cambia nada). Requiere PowerShell 7 y el módulo Microsoft.Graph.
.EXAMPLE
  ./verificar-ambiente.ps1
  ./verificar-ambiente.ps1 -Dominio lab01.onmicrosoft.com
#>
param(
    [string]$Dominio
)

$scopes = "User.Read.All", "Group.Read.All", "Organization.Read.All",
          "RoleManagement.Read.Directory", "UserAuthenticationMethod.Read.All"
Connect-MgGraph -Scopes $scopes -NoWelcome
$ctx = Get-MgContext
if (-not $Dominio) {
    $Dominio = ((Get-MgOrganization).VerifiedDomains | Where-Object IsDefault).Name
}
Write-Host "`nTenant: $Dominio   Cuenta: $($ctx.Account)`n" -ForegroundColor Cyan
$resultado = [System.Collections.Generic.List[object]]::new()
function Agregar($area, $elemento, $ok, $detalle) {
    $resultado.Add([pscustomobject]@{
        Area = $area; Elemento = $elemento
        Estado = $(if ($ok) { "OK" } else { "REVISAR" }); Detalle = $detalle })
}

# 1. Licencias
$skus = Get-MgSubscribedSku
$p2 = $skus | Where-Object { $_.SkuPartNumber -in "AAD_PREMIUM_P2", "SPE_E5", "EMSPREMIUM" }
foreach ($s in $skus) {
    Agregar "Licencias" $s.SkuPartNumber ($s.PrepaidUnits.Enabled -gt 0) `
        "Asignadas $($s.ConsumedUnits) de $($s.PrepaidUnits.Enabled)"
}
if (-not $p2) { Agregar "Licencias" "Entra ID P2" $false "No se encontró P2 ni un plan que lo incluya" }

# 2. Rol de la cuenta del participante
$yo = Get-MgUser -UserId $ctx.Account
$roles = Get-MgRoleManagementDirectoryRoleAssignment -Filter "principalId eq '$($yo.Id)'" -ExpandProperty roleDefinition
$nombres = ($roles | ForEach-Object { $_.RoleDefinition.DisplayName }) -join ", "
Agregar "Roles" $ctx.Account ($nombres -match "Global Administrator|Application Administrator") $nombres

# 3. Usuarios de prueba
$cuentas = "ana.lopez", "luis.mendez", "marta.ruiz", "pedro.garcia", "carla.diaz", "prueba.nube"
foreach ($c in $cuentas) {
    $upn = "$c@$Dominio"
    $u = Get-MgUser -UserId $upn -Property id,displayName,department,jobTitle,employeeId,onPremisesSyncEnabled,usageLocation,accountEnabled -ErrorAction SilentlyContinue
    if (-not $u) { Agregar "Usuarios" $upn $false "No existe"; continue }
    $lic = (Get-MgUserLicenseDetail -UserId $u.Id).SkuPartNumber -join ","
    $origen = if ($u.OnPremisesSyncEnabled) { "sincronizado" } else { "nube" }
    $datosOk = $u.Department -and $lic -and ($c -eq "prueba.nube" -or $u.EmployeeId)
    Agregar "Usuarios" $upn $datosOk "$origen | $($u.Department) | $($u.JobTitle) | $($u.EmployeeId) | licencia: $lic"
    $metodos = Get-MgUserAuthenticationMethod -UserId $u.Id |
        Where-Object { $_.AdditionalProperties.'@odata.type' -ne "#microsoft.graph.passwordAuthenticationMethod" }
    Agregar "MFA" $upn ($metodos.Count -gt 0) "$($metodos.Count) método(s) además de la contraseña"
}

# 4. Grupos
$grupos = "Todos-Empleados", "DYN-Compras", "GRP-RRHH", "GRP-Compras-Jefes", "GRP-Logistica", "GRP-Proveedores"
foreach ($g in $grupos) {
    $obj = Get-MgGroup -Filter "displayName eq '$g'" -Property id,displayName,groupTypes,membershipRule
    if (-not $obj) { Agregar "Grupos" $g $false "No existe"; continue }
    $n = (Get-MgGroupMember -GroupId $obj.Id -All).Count
    $tipo = if ($obj.GroupTypes -contains "DynamicMembership") { "dinámico: $($obj.MembershipRule)" } else { "asignado" }
    Agregar "Grupos" $g ($n -gt 0 -or $g -eq "GRP-Proveedores") "$n miembro(s) | $tipo"
}

$resultado | Format-Table -AutoSize -Wrap
$pend = ($resultado | Where-Object Estado -eq "REVISAR").Count
if ($pend -eq 0) { Write-Host "Ambiente listo." -ForegroundColor Green }
else { Write-Host "$pend elemento(s) por revisar." -ForegroundColor Yellow }
