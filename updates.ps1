# Credits to DTLegit for this script!

$RegPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate"
$RegistrySettings = @{
    "DeferQualityUpdates"              = 1
    "DeferQualityUpdatesPeriodInDays"  = 4
    "ProductVersion"                   = "Windows 11"
    "TargetReleaseVersion"             = 1
    "TargetReleaseVersionInfo"         = "24H2"
}
if (-not (Test-Path $RegPath)) {
    New-Item -Path $RegPath -Force | Out-Null
}
foreach ($Name in $RegistrySettings.Keys) {
    $Value = $RegistrySettings[$Name]
    $Type = if ($Value -is [int]) { "DWord" } else { "String" }
    Set-ItemProperty -Path $RegPath -Name $Name -Value $Value -Type $Type -Force
    Write-Host "Set $Name to $Value ($Type)"
}

Write-Host "`nRegistry settings applied successfully."
