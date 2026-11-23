<#
.SYNOPSIS
  Preparación (soporte). Registra en el tenant de un participante la aplicación "Netec-Instructor-P9",
  con el certificado público del instructor y los permisos de aplicación que necesitan
  fallas-practica9.ps1 y restaurar-practica9.ps1. Devuelve la fila para tenants.csv.
.DESCRIPTION
  Se ejecuta una vez por tenant, con un Global Administrator del tenant del participante.
  El instructor genera el certificado una sola vez (ver GUIA_INSTRUCTOR_Practica09.md) y entrega
  a soporte solo el archivo público .cer.
.EXAMPLE
  ./registrar-app-instructor.ps1 -Participante 01 -Certificado .\Netec-Instructor-P9.cer -CorreoInvitado cuenta.lab01@gmail.com
#>
param(
    [Parameter(Mandatory)][string]$Participante,
    [Parameter(Mandatory)][string]$Certificado,
    [string]$CorreoInvitado = "",
    [string]$Salida = "$PSScriptRoot/tenants.csv"
)

$ErrorActionPreference = "Stop"
Connect-MgGraph -Scopes "Application.ReadWrite.All", "AppRoleAssignment.ReadWrite.All" -NoWelcome
$tenantId = (Get-MgContext).TenantId

$x509 = [System.Security.Cryptography.X509Certificates.X509Certificate2]::new((Resolve-Path $Certificado).Path)
$graph = Get-MgServicePrincipal -Filter "appId eq '00000003-0000-0000-c000-000000000000'"
$permisos = "Application.ReadWrite.All", "Policy.ReadWrite.ApplicationConfiguration",
            "Synchronization.ReadWrite.All", "GroupMember.ReadWrite.All", "User.Read.All"
$roles = foreach ($p in $permisos) { $graph.AppRoles | Where-Object Value -eq $p }

$app = Get-MgApplication -Filter "displayName eq 'Netec-Instructor-P9'"
if (-not $app) {
    $app = New-MgApplication -DisplayName "Netec-Instructor-P9" -SignInAudience "AzureADMyOrg" `
        -KeyCredentials @(@{ Type = "AsymmetricX509Cert"; Usage = "Verify"; Key = $x509.RawData
                             DisplayName = $x509.Subject; EndDateTime = $x509.NotAfter }) `
        -RequiredResourceAccess @(@{ ResourceAppId = $graph.AppId
            ResourceAccess = @($roles | ForEach-Object { @{ Id = $_.Id; Type = "Role" } }) })
}
$sp = Get-MgServicePrincipal -Filter "appId eq '$($app.AppId)'"
if (-not $sp) { $sp = New-MgServicePrincipal -AppId $app.AppId }

# Consentimiento de administrador: asignar cada permiso de aplicación al service principal
$asignados = (Get-MgServicePrincipalAppRoleAssignment -ServicePrincipalId $sp.Id).AppRoleId
foreach ($r in $roles) {
    if ($r.Id -notin $asignados) {
        New-MgServicePrincipalAppRoleAssignment -ServicePrincipalId $sp.Id -PrincipalId $sp.Id `
            -ResourceId $graph.Id -AppRoleId $r.Id | Out-Null
    }
}

$fila = [pscustomobject]@{
    Participante = $Participante; TenantId = $tenantId; ClientId = $app.AppId
    CertificateThumbprint = $x509.Thumbprint; CorreoInvitado = $CorreoInvitado
}
if (-not (Test-Path $Salida)) { $fila | Export-Csv $Salida -NoTypeInformation -Encoding utf8 }
else { $fila | Export-Csv $Salida -NoTypeInformation -Encoding utf8 -Append }
$fila | Format-List
Write-Host "Aplicación registrada y fila agregada a $Salida" -ForegroundColor Green
