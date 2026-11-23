<#
.SYNOPSIS
  Práctica 9. Reporte de salud de integraciones: errores de inicio de sesión, cambios recientes,
  estado del aprovisionamiento y certificados próximos a vencer. Genera CSV en la carpeta indicada.
.EXAMPLE
  ./reporte-salud.ps1
  ./reporte-salud.ps1 -Aplicaciones "Portal de Proveedores (Lab)","Intranet RR. HH." -Horas 4
#>
param(
    [string[]]$Aplicaciones = @("Portal de Proveedores (Lab)", "Intranet RR. HH.", "ERP heredado"),
    [int]$Horas = 24,
    [int]$DiasCambios = 7,
    [string]$Carpeta = "$PSScriptRoot/../salidas"
)

Connect-MgGraph -Scopes "Application.Read.All", "AuditLog.Read.All", "Directory.Read.All" -NoWelcome
New-Item -ItemType Directory -Force -Path $Carpeta | Out-Null
$desde = (Get-Date).ToUniversalTime().AddHours(-$Horas).ToString("yyyy-MM-ddTHH:mm:ssZ")

# 1. Errores de inicio de sesión por aplicación y código
$errores = foreach ($nombre in $Aplicaciones) {
    $sp = Get-MgServicePrincipal -Filter "displayName eq '$nombre'"
    if (-not $sp) { Write-Warning "No existe la aplicación '$nombre'"; continue }
    $f = "appId eq '$($sp.AppId)' and createdDateTime ge $desde and status/errorCode ne 0"
    Get-MgAuditLogSignIn -Filter $f -All | ForEach-Object {
        [pscustomobject]@{
            Aplicacion = $nombre; Fecha = $_.CreatedDateTime; Usuario = $_.UserPrincipalName
            Codigo = $_.Status.ErrorCode; Motivo = $_.Status.FailureReason
            AccesoCondicional = $_.ConditionalAccessStatus; CorrelationId = $_.CorrelationId
        }
    }
}
$errores | Export-Csv "$Carpeta/errores-inicio-sesion.csv" -NoTypeInformation -Encoding utf8
Write-Host "`n1. Errores de inicio de sesión (últimas $Horas h)" -ForegroundColor Cyan
$errores | Group-Object Aplicacion, Codigo | Select-Object Count, Name | Sort-Object Count -Descending | Format-Table -AutoSize

# 2. Cambios en aplicaciones
$desdeC = (Get-Date).ToUniversalTime().AddDays(-$DiasCambios).ToString("yyyy-MM-ddTHH:mm:ssZ")
$f7 = "category eq 'ApplicationManagement' and activityDateTime ge $desdeC"
$cambios = Get-MgAuditLogDirectoryAudit -Filter $f7 -All | ForEach-Object {
    [pscustomobject]@{
        Fecha = $_.ActivityDateTime; Actividad = $_.ActivityDisplayName
        Por = $_.InitiatedBy.User.UserPrincipalName; Objeto = $_.TargetResources[0].DisplayName
        Propiedades = ($_.TargetResources[0].ModifiedProperties.DisplayName -join ", ")
    }
}
$cambios | Export-Csv "$Carpeta/cambios-aplicaciones.csv" -NoTypeInformation -Encoding utf8
Write-Host "2. Cambios en aplicaciones (últimos $DiasCambios días)" -ForegroundColor Cyan
$cambios | Sort-Object Fecha -Descending | Select-Object -First 15 | Format-Table -AutoSize -Wrap

# 3. Estado del aprovisionamiento
Write-Host "3. Aprovisionamiento" -ForegroundColor Cyan
$aprov = foreach ($nombre in $Aplicaciones) {
    $sp = Get-MgServicePrincipal -Filter "displayName eq '$nombre'"
    if (-not $sp) { continue }
    Get-MgServicePrincipalSynchronizationJob -ServicePrincipalId $sp.Id -ErrorAction SilentlyContinue | ForEach-Object {
        [pscustomobject]@{
            Aplicacion = $nombre; Estado = $_.Status.Code
            Cuarentena = [bool]$_.Status.Quarantine
            UltimoCiclo = $_.Status.LastExecution.TimeEnded
            Resultado = $_.Status.LastExecution.State
        }
    }
}
$aprov | Export-Csv "$Carpeta/aprovisionamiento.csv" -NoTypeInformation -Encoding utf8
$aprov | Format-Table -AutoSize

# 4. Certificados SAML con menos de 90 días
Write-Host "4. Certificados SAML que vencen en menos de 90 días" -ForegroundColor Cyan
$certs = Get-MgServicePrincipal -All -Property displayName,preferredSingleSignOnMode,keyCredentials |
    Where-Object PreferredSingleSignOnMode -eq "saml" | ForEach-Object {
        $sp = $_
        $sp.KeyCredentials | Where-Object Usage -eq "Verify" | ForEach-Object {
            [pscustomobject]@{ Aplicacion = $sp.DisplayName; Vence = $_.EndDateTime
                               Dias = [int]($_.EndDateTime - (Get-Date)).TotalDays }
        }
    } | Where-Object Dias -lt 90
$certs | Export-Csv "$Carpeta/certificados.csv" -NoTypeInformation -Encoding utf8
$certs | Format-Table -AutoSize
Write-Host "Archivos CSV en $((Resolve-Path $Carpeta).Path)"
