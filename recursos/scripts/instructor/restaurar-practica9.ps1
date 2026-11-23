<#
.SYNOPSIS
  Práctica 9. Revierte las fallas aplicadas por fallas-practica9.ps1 con el estado guardado.
  Úsalo al final de la práctica para los equipos que no terminaron, o para repetir el ejercicio.
.EXAMPLE
  ./restaurar-practica9.ps1 -Tenants .\tenants.csv        # instructor: todos los tenants
  ./restaurar-practica9.ps1                               # participante: su propio tenant
#>
param(
    [string]$Tenants,
    [string]$CarpetaEstado
)

$ErrorActionPreference = "Stop"
$G = "https://graph.microsoft.com"

function Restaurar {
    param([string]$ArchivoEstado)
    $e = Get-Content $ArchivoEstado -Raw | ConvertFrom-Json -Depth 100
    $res = [ordered]@{}
    $sp  = Get-MgServicePrincipal -Filter "displayName eq '$($e.App)'"
    $app = Get-MgApplication -Filter "appId eq '$($sp.AppId)'"

    try { Update-MgApplication -ApplicationId $app.Id -Web @{ RedirectUris = @($e.ReplyUrls) }; $res.F1 = "OK" }
    catch { $res.F1 = "ERROR: $($_.Exception.Message)" }

    try {
        if ($e.ClaimsPolicy) {
            $pol = $e.ClaimsPolicy | ConvertFrom-Json -Depth 50
            $pol.PSObject.Properties.Remove("@odata.context")
            Invoke-MgGraphRequest -Method PUT -Uri "$G/beta/servicePrincipals/$($sp.Id)/claimsPolicy" `
                -Body ($pol | ConvertTo-Json -Depth 50) -ContentType "application/json" | Out-Null
        }
        if ($e.RolOriginal) {
            $roles = $app.AppRoles
            ($roles | Where-Object Value -eq "Compradores").Value = $e.RolOriginal
            Update-MgApplication -ApplicationId $app.Id -AppRoles $roles
        }
        $res.F2 = "OK"
    } catch { $res.F2 = "ERROR: $($_.Exception.Message)" }

    try {
        Update-MgServicePrincipal -ServicePrincipalId $sp.Id -PreferredTokenSigningKeyThumbprint $e.Huella
        $res.F3 = "OK (el certificado CN=Mantenimiento queda inactivo)"
    } catch { $res.F3 = "ERROR: $($_.Exception.Message)" }

    try {
        if ($e.Esquema) {
            $s = $e.Esquema | ConvertFrom-Json -Depth 100
            $s.PSObject.Properties.Remove("@odata.context")
            Invoke-MgGraphRequest -Method PUT -Uri "$G/v1.0/servicePrincipals/$($sp.Id)/synchronization/jobs/$($e.JobId)/schema" `
                -Body ($s | ConvertTo-Json -Depth 100) -ContentType "application/json" | Out-Null
        }
        $res.F4 = "OK"
    } catch { $res.F4 = "ERROR: $($_.Exception.Message)" }

    try {
        if ($e.Invitado -and $e.Invitado -notin (Get-MgGroupMember -GroupId $e.Grupo -All).Id) {
            New-MgGroupMember -GroupId $e.Grupo -DirectoryObjectId $e.Invitado
        }
        $res.F5 = "OK"
    } catch { $res.F5 = "ERROR: $($_.Exception.Message)" }
    return $res
}

if ($Tenants) {
    $CarpetaEstado = if ($CarpetaEstado) { $CarpetaEstado } else { Join-Path $PSScriptRoot "estados" }
    $resumen = foreach ($t in Import-Csv $Tenants) {
        $fila = [ordered]@{ Participante = $t.Participante }
        $archivo = Join-Path $CarpetaEstado "estado-$($t.Participante).json"
        try {
            if (-not (Test-Path $archivo)) { throw "No hay estado guardado" }
            Connect-MgGraph -TenantId $t.TenantId -ClientId $t.ClientId -CertificateThumbprint $t.CertificateThumbprint -NoWelcome
            $r = Restaurar -ArchivoEstado $archivo
            foreach ($k in $r.Keys) { $fila[$k] = $r[$k] }
        } catch { $fila.Error = $_.Exception.Message }
        finally { Disconnect-MgGraph -ErrorAction SilentlyContinue | Out-Null }
        [pscustomobject]$fila
    }
    $resumen | Format-Table -AutoSize -Wrap
} else {
    Connect-MgGraph -Scopes "Application.ReadWrite.All", "Policy.ReadWrite.ApplicationConfiguration",
                            "Synchronization.ReadWrite.All", "GroupMember.ReadWrite.All", "User.Read.All" -NoWelcome
    $CarpetaEstado = if ($CarpetaEstado) { $CarpetaEstado } else { Join-Path $env:LOCALAPPDATA "MIC_P9" }
    [pscustomobject](Restaurar -ArchivoEstado (Join-Path $CarpetaEstado "estado.json")) | Format-List
}
