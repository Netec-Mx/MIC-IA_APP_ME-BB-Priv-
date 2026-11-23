<#
.SYNOPSIS
  Práctica 3. Lista los certificados de firma SAML de las aplicaciones del tenant y su vencimiento.
.EXAMPLE
  ./inventario-certificados.ps1             # certificados que vencen en menos de 90 días
  ./inventario-certificados.ps1 -Dias 1200  # prácticamente todos
#>
param(
    [int]$Dias = 90
)

Connect-MgGraph -Scopes "Application.Read.All" -NoWelcome

$apps = Get-MgServicePrincipal -All -Property id,displayName,preferredSingleSignOnMode,keyCredentials,preferredTokenSigningKeyThumbprint |
    Where-Object PreferredSingleSignOnMode -eq "saml"

$filas = foreach ($sp in $apps) {
    foreach ($k in ($sp.KeyCredentials | Where-Object Usage -eq "Verify")) {
        $huella = ($k.CustomKeyIdentifier | ForEach-Object { $_.ToString("X2") }) -join ""
        [pscustomobject]@{
            Aplicacion = $sp.DisplayName
            Huella     = $huella
            Activo     = ($huella -eq $sp.PreferredTokenSigningKeyThumbprint)
            Vence      = $k.EndDateTime.ToString("yyyy-MM-dd")
            Dias       = [int]($k.EndDateTime - (Get-Date)).TotalDays
        }
    }
}

$filas | Where-Object Dias -lt $Dias | Sort-Object Dias | Format-Table -AutoSize
Write-Host "Aplicaciones SAML: $($apps.Count) · certificados con menos de $Dias días: $(($filas | Where-Object Dias -lt $Dias).Count)"
