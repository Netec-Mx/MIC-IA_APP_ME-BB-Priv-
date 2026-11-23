<#
.SYNOPSIS
  Práctica 4 (reto opcional). Envía el lote SCIM de RR. HH. al endpoint /bulkUpload del
  aprovisionamiento entrante por API y muestra el resultado en los provisioning logs.
.EXAMPLE
  ./carga-rrhh.ps1 -ServicePrincipalId <object-id-de-la-app> -JobId <id-del-job>
#>
param(
    [Parameter(Mandatory)][string]$ServicePrincipalId,
    [Parameter(Mandatory)][string]$JobId,
    [string]$Lote = "$PSScriptRoot/../datos/lote-rrhh.json"
)

Connect-MgGraph -Scopes "SynchronizationData-User.Upload", "AuditLog.Read.All" -NoWelcome
$uri = "https://graph.microsoft.com/v1.0/servicePrincipals/$ServicePrincipalId/synchronization/jobs/$JobId/bulkUpload"
$cuerpo = Get-Content $Lote -Raw -Encoding utf8
Invoke-MgGraphRequest -Method POST -Uri $uri -Body $cuerpo -ContentType "application/scim+json"
Write-Host "Lote enviado (respuesta 202 = aceptado; el proceso es asíncrono). Esperando 60 s..."
Start-Sleep -Seconds 60
Get-MgAuditLogProvisioning -Filter "jobId eq '$JobId'" -Top 20 |
    Select-Object ActivityDateTime, @{n = "Accion"; e = { $_.ProvisioningAction } },
                  @{n = "Estado"; e = { $_.ProvisioningStatusInfo.Status } },
                  @{n = "Usuario"; e = { $_.SourceIdentity.DisplayName } } |
    Format-Table -AutoSize
