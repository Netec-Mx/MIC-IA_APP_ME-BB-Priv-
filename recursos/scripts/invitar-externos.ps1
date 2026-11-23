<#
.SYNOPSIS
  Práctica 7. Invita usuarios externos (B2B) desde un CSV, registra su empresa y los agrega a un grupo.
.DESCRIPTION
  El CSV debe tener las columnas: correo, nombre, empresa.
.EXAMPLE
  ./invitar-externos.ps1 -Csv ../datos/invitados.csv
#>
param(
    [Parameter(Mandatory)][string]$Csv,
    [string]$Grupo = "GRP-Proveedores",
    [switch]$SinCorreo
)

Connect-MgGraph -Scopes "User.Invite.All", "User.ReadWrite.All", "GroupMember.ReadWrite.All" -NoWelcome
$tenantId = (Get-MgContext).TenantId
$g = Get-MgGroup -Filter "displayName eq '$Grupo'"
if (-not $g) { throw "No existe el grupo $Grupo" }

foreach ($fila in Import-Csv $Csv) {
    $params = @{
        InvitedUserEmailAddress = $fila.correo
        InvitedUserDisplayName  = "$($fila.nombre) ($($fila.empresa))"
        InviteRedirectUrl       = "https://myapps.microsoft.com/?tenantid=$tenantId"
        SendInvitationMessage   = -not $SinCorreo
        InvitedUserMessageInfo  = @{ CustomizedMessageBody = "Bienvenido al portal de proveedores de Contoso." }
    }
    $inv = New-MgInvitation -BodyParameter $params
    Update-MgUser -UserId $inv.InvitedUser.Id -CompanyName $fila.empresa
    $miembros = (Get-MgGroupMember -GroupId $g.Id -All).Id
    if ($inv.InvitedUser.Id -notin $miembros) {
        New-MgGroupMember -GroupId $g.Id -DirectoryObjectId $inv.InvitedUser.Id
    }
    [pscustomobject]@{
        Correo = $fila.correo; ObjectId = $inv.InvitedUser.Id
        Estado = $inv.Status; EnlaceCanje = $inv.InviteRedeemUrl
    }
}
