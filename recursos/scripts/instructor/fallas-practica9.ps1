<#
.SYNOPSIS
  Práctica 9. Aplica automáticamente las cinco fallas del ejercicio de diagnóstico y guarda el
  estado original para restaurarlo con restaurar-practica9.ps1.

.DESCRIPTION
  Fallas (todas sobre la enterprise app "Portal de Proveedores (Lab)"):
    F1  Reply URL alterada                          -> AADSTS50011 al iniciar desde la aplicación
    F2  NameID = UPN con formato Persistent          -> identificadores incorrectos en el portal
        (si la API de claims no está disponible: valor del rol "Comprador" alterado)
    F3  Certificado de firma nuevo activado          -> la aplicación rechaza la firma
    F4  Scoping filter "department EQUALS Compra"    -> usuarios de Compras fuera de alcance
    F5  Invitado retirado de GRP-Proveedores         -> AADSTS50105 para ese invitado

  Dos modos de uso:
    Instructor (recomendado para grupos): una sola ejecución contra todos los tenants, con la
      aplicación "Netec-Instructor-P9" registrada en cada tenant (ver registrar-app-instructor.ps1).
        ./fallas-practica9.ps1 -Tenants .\tenants.csv
      tenants.csv: Participante,TenantId,ClientId,CertificateThumbprint,CorreoInvitado
    Participante: cada quien lo ejecuta en su LAB-CLIENT con su cuenta (sin abrir el script).
        ./fallas-practica9.ps1

.NOTES
  F2 usa el endpoint beta /servicePrincipals/{id}/claimsPolicy (Custom Claims Policy, preview).
#>
param(
    [string]$Tenants,
    [string]$CorreoInvitado,
    [string]$App = "Portal de Proveedores (Lab)",
    [string]$CarpetaEstado
)

$ErrorActionPreference = "Stop"
$G = "https://graph.microsoft.com"

function Aplicar-Fallas {
    param([string]$CorreoInv, [string]$ArchivoEstado)

    $res = [ordered]@{}
    $estado = [ordered]@{ Fecha = (Get-Date).ToString("s"); App = $App }
    $sp  = Get-MgServicePrincipal -Filter "displayName eq '$App'" -Property id,appId,preferredTokenSigningKeyThumbprint
    if (-not $sp) { throw "No existe la aplicación '$App' en este tenant" }
    $app = Get-MgApplication -Filter "appId eq '$($sp.AppId)'"
    $variante = Get-Random -Minimum 1 -Maximum 4

    # F1. Reply URL alterada (tres variantes para que no sea igual en todos los equipos)
    try {
        $estado.ReplyUrls = @($app.Web.RedirectUris)
        $nuevas = foreach ($u in $app.Web.RedirectUris) {
            if ($u -like "*/saml/acs") {
                switch ($variante) { 1 { "$u/" } 2 { $u -replace "/saml/acs$", "/saml/acs2" } 3 { $u -replace "/saml/acs$", "/SAML/ACS" } }
            } else { $u }
        }
        Update-MgApplication -ApplicationId $app.Id -Web @{ RedirectUris = @($nuevas) }
        $res.F1 = "OK"
    } catch { $res.F1 = "ERROR: $($_.Exception.Message)" }

    # F2. NameID = user.userprincipalname / Persistent (API beta); alternativa: valor del rol alterado
    try {
        $uri = "$G/beta/servicePrincipals/$($sp.Id)/claimsPolicy"
        $pol = Invoke-MgGraphRequest -Method GET -Uri $uri -OutputType Json
        $obj = $pol | ConvertFrom-Json -Depth 50
        $nameId = $obj.claims | Where-Object { $_.'@odata.type' -eq "#microsoft.graph.samlNameIdClaim" }
        if (-not $nameId) { throw "La política de claims no tiene samlNameIdClaim" }
        $estado.ClaimsPolicy = $pol
        $nameId.nameIdFormat = "persistent"
        $nameId.configurations = @(@{
            condition = $null; transformations = @()
            attribute = @{ "@odata.type" = "#microsoft.graph.sourcedAttribute"; id = "userprincipalname"
                           source = "user"; isExtensionAttribute = $false }
        })
        $obj.PSObject.Properties.Remove("@odata.context")
        Invoke-MgGraphRequest -Method PUT -Uri $uri -Body ($obj | ConvertTo-Json -Depth 50) -ContentType "application/json" | Out-Null
        $res.F2 = "OK (NameID)"
    } catch {
        try {
            $roles = $app.AppRoles
            $r = $roles | Where-Object Value -eq "Comprador"
            if (-not $r) { throw "No existe el rol Comprador" }
            $estado.RolOriginal = "Comprador"
            $r.Value = "Compradores"
            Update-MgApplication -ApplicationId $app.Id -AppRoles $roles
            $res.F2 = "OK (rol alterado; claimsPolicy no disponible)"
        } catch { $res.F2 = "ERROR: $($_.Exception.Message)" }
    }

    # F3. Certificado nuevo activo, desconocido para la aplicación de prueba
    try {
        $estado.Huella = $sp.PreferredTokenSigningKeyThumbprint
        $cert = Add-MgServicePrincipalTokenSigningCertificate -ServicePrincipalId $sp.Id `
            -DisplayName "CN=Mantenimiento" -EndDateTime (Get-Date).AddYears(1)
        Update-MgServicePrincipal -ServicePrincipalId $sp.Id -PreferredTokenSigningKeyThumbprint $cert.Thumbprint
        $estado.HuellaFalla = $cert.Thumbprint
        $res.F3 = "OK"
    } catch { $res.F3 = "ERROR: $($_.Exception.Message)" }

    # F4. Scoping filter con error de captura (API de sincronización v1.0)
    try {
        $jobs = Invoke-MgGraphRequest -Method GET -Uri "$G/v1.0/servicePrincipals/$($sp.Id)/synchronization/jobs"
        if (-not $jobs.value) { throw "La aplicación no tiene aprovisionamiento configurado (Práctica 4)" }
        $jobId = $jobs.value[0].id
        $uriS = "$G/v1.0/servicePrincipals/$($sp.Id)/synchronization/jobs/$jobId/schema"
        $esquema = Invoke-MgGraphRequest -Method GET -Uri $uriS -OutputType Json
        $estado.JobId = $jobId
        $estado.Esquema = $esquema
        $s = $esquema | ConvertFrom-Json -Depth 100
        $cambios = 0
        foreach ($regla in $s.synchronizationRules) {
            foreach ($om in ($regla.objectMappings | Where-Object sourceObjectName -eq "User")) {
                foreach ($grupo in $om.scope.groups) {
                    foreach ($c in $grupo.clauses) {
                        if ($c.sourceOperandName -eq "department" -and $c.targetOperand.values -contains "Compras") {
                            $c.targetOperand.values = @("Compra"); $cambios++
                        }
                    }
                }
            }
        }
        if ($cambios -eq 0) { throw "No se encontró la cláusula department EQUALS Compras" }
        $s.PSObject.Properties.Remove("@odata.context")
        Invoke-MgGraphRequest -Method PUT -Uri $uriS -Body ($s | ConvertTo-Json -Depth 100) -ContentType "application/json" | Out-Null
        $res.F4 = "OK"
    } catch { $res.F4 = "ERROR: $($_.Exception.Message)" }

    # F5. Invitado fuera del grupo asignado
    try {
        if (-not $CorreoInv) {
            $csv = Join-Path $PSScriptRoot "..\..\datos\invitados.csv"
            $CorreoInv = (Import-Csv $csv | Where-Object correo -like "*@gmail.com" | Select-Object -First 1).correo
        }
        $grp = Get-MgGroup -Filter "displayName eq 'GRP-Proveedores'"
        $inv = Get-MgUser -Filter "mail eq '$CorreoInv'"
        if (-not $inv) { throw "No existe el invitado $CorreoInv" }
        Remove-MgGroupMemberDirectoryObjectByRef -GroupId $grp.Id -DirectoryObjectId $inv.Id
        $estado.Grupo = $grp.Id
        $estado.Invitado = $inv.Id
        $res.F5 = "OK"
    } catch { $res.F5 = "ERROR: $($_.Exception.Message)" }

    $estado | ConvertTo-Json -Depth 5 | Set-Content $ArchivoEstado -Encoding utf8
    return $res
}

if ($Tenants) {
    # ---------------- modo instructor: todos los tenants
    $CarpetaEstado = if ($CarpetaEstado) { $CarpetaEstado } else { Join-Path $PSScriptRoot "estados" }
    New-Item -ItemType Directory -Force -Path $CarpetaEstado | Out-Null
    $resumen = foreach ($t in Import-Csv $Tenants) {
        $fila = [ordered]@{ Participante = $t.Participante }
        try {
            Connect-MgGraph -TenantId $t.TenantId -ClientId $t.ClientId -CertificateThumbprint $t.CertificateThumbprint -NoWelcome
            $r = Aplicar-Fallas -CorreoInv $t.CorreoInvitado -ArchivoEstado (Join-Path $CarpetaEstado "estado-$($t.Participante).json")
            foreach ($k in $r.Keys) { $fila[$k] = $r[$k] }
        } catch { $fila.Error = $_.Exception.Message }
        finally { Disconnect-MgGraph -ErrorAction SilentlyContinue | Out-Null }
        [pscustomobject]$fila
    }
    $resumen | Format-Table -AutoSize -Wrap
    $resumen | Export-Csv (Join-Path $CarpetaEstado "resumen-fallas.csv") -NoTypeInformation -Encoding utf8
    Write-Host "Estados guardados en $CarpetaEstado" -ForegroundColor Yellow
} else {
    # ---------------- modo participante: su propio tenant, sin mostrar detalles
    Connect-MgGraph -Scopes "Application.ReadWrite.All", "Policy.ReadWrite.ApplicationConfiguration",
                            "Synchronization.ReadWrite.All", "GroupMember.ReadWrite.All", "User.Read.All" -NoWelcome
    $CarpetaEstado = if ($CarpetaEstado) { $CarpetaEstado } else { Join-Path $env:LOCALAPPDATA "MIC_P9" }
    New-Item -ItemType Directory -Force -Path $CarpetaEstado | Out-Null
    $r = Aplicar-Fallas -CorreoInv $CorreoInvitado -ArchivoEstado (Join-Path $CarpetaEstado "estado.json")
    $errores = @($r.Values | Where-Object { $_ -like "ERROR*" })
    if ($errores.Count -eq 0) { Write-Host "Ambiente de la Práctica 9 preparado. Puedes empezar." -ForegroundColor Green }
    else { Write-Host "Ambiente preparado con $($errores.Count) aviso(s); informa al instructor." -ForegroundColor Yellow }
}
