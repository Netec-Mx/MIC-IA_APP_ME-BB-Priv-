# Práctica 4. Prueba del endpoint SCIM como lo usará Microsoft Entra
param(
    [Parameter(Mandatory)][string]$Url,     # https://scim-labXX.azurewebsites.net/scim/v2
    [Parameter(Mandatory)][string]$Token
)
$h = @{ Authorization = "Bearer $Token" }

# 1. Sin token: el endpoint debe rechazar la solicitud
try { Invoke-RestMethod "$Url/Users" | Out-Null }
catch { "1. Sin token -> HTTP $([int]$_.Exception.Response.StatusCode)" }

# 2. Capacidades del servidor
$spc = Invoke-RestMethod "$Url/ServiceProviderConfig" -Headers $h
"2. PATCH soportado: $($spc.patch.supported) | Filtros: $($spc.filter.supported)"

# 3. Búsqueda por userName, igual que la que hace Entra antes de crear
$r = Invoke-RestMethod "$Url/Users?filter=userName eq `"prueba.manual@contoso.com`"" -Headers $h
"3. Coincidencias: $($r.totalResults)"

# 4. Alta, desactivación y baja de un usuario de prueba
$cuerpo = @{
    schemas  = @("urn:ietf:params:scim:schemas:core:2.0:User")
    userName = "prueba.manual@contoso.com"
    active   = $true
    name     = @{ givenName = "Prueba"; familyName = "Manual" }
} | ConvertTo-Json -Depth 5
$u = Invoke-RestMethod "$Url/Users" -Method Post -Headers $h -Body $cuerpo -ContentType "application/scim+json"
"4a. Creado con id $($u.id)"
$patch = @{
    schemas    = @("urn:ietf:params:scim:api:messages:2.0:PatchOp")
    Operations = @(@{ op = "Replace"; path = "active"; value = $false })
} | ConvertTo-Json -Depth 5
$u2 = Invoke-RestMethod "$Url/Users/$($u.id)" -Method Patch -Headers $h -Body $patch -ContentType "application/scim+json"
"4b. active = $($u2.active)"
Invoke-RestMethod "$Url/Users/$($u.id)" -Method Delete -Headers $h | Out-Null
"4c. Eliminado"
