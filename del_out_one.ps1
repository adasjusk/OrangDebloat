#Credits For Raven Team For Making These Scripts
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    try {
        Start-Process PowerShell -Verb RunAs "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -WindowStyle Hidden
        exit
    }
    catch {
        exit
    }
}

try {
    Set-ExecutionPolicy Bypass -Scope Process -Force
    $ErrorActionPreference = 'SilentlyContinue'

    # Close Outlook processes
    Get-Process | Where-Object { $_.ProcessName -like "*outlook*" } | Stop-Process -Force
    Start-Sleep -Seconds 2

    # Remove Outlook apps
    Get-AppxPackage *Microsoft.Office.Outlook* | Remove-AppxPackage
    Get-AppxProvisionedPackage -Online | Where-Object {$_.PackageName -like "*Microsoft.Office.Outlook*"} | Remove-AppxProvisionedPackage -Online
    Get-AppxPackage *Microsoft.OutlookForWindows* | Remove-AppxPackage
    Get-AppxProvisionedPackage -Online | Where-Object {$_.PackageName -like "*Microsoft.OutlookForWindows*"} | Remove-AppxProvisionedPackage -Online

    # Remove Outlook folders
    $windowsAppsPath = "C:\Program Files\WindowsApps"
    $outlookFolders = Get-ChildItem -Path $windowsAppsPath -Directory | Where-Object { $_.Name -like "Microsoft.OutlookForWindows*" }
    foreach ($folder in $outlookFolders) {
        $folderPath = Join-Path $windowsAppsPath $folder.Name
        takeown /f $folderPath /r /d Y | Out-Null
        icacls $folderPath /grant administrators:F /t | Out-Null
        Remove-Item -Path $folderPath -Recurse -Force
    }

    # Remove shortcuts
    $shortcutPaths = @(
        "$env:ProgramData\Microsoft\Windows\Start Menu\Programs\Outlook.lnk",
        "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Outlook.lnk",
        "$env:ProgramData\Microsoft\Windows\Start Menu\Programs\Microsoft Office\Outlook.lnk",
        "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Microsoft Office\Outlook.lnk",
        "$env:PUBLIC\Desktop\Outlook.lnk",
        "$env:USERPROFILE\Desktop\Outlook.lnk",
        "$env:PUBLIC\Desktop\Microsoft Outlook.lnk",
        "$env:USERPROFILE\Desktop\Microsoft Outlook.lnk",
        "$env:PUBLIC\Desktop\Outlook (New).lnk",
        "$env:USERPROFILE\Desktop\Outlook (New).lnk",
        "$env:ProgramData\Microsoft\Windows\Start Menu\Programs\Outlook (New).lnk",
        "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Outlook (New).lnk"
    )
    $shortcutPaths | ForEach-Object { Remove-Item $_ -Force }

    # Taskbar cleanup
    Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "ShowTaskViewButton" -Value 0 -Type DWord -Force

    $registryPaths = @(
        "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Taskband",
        "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\TaskbarMRU",
        "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\TaskBar",
        "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
    )
    foreach ($path in $registryPaths) {
        if (Test-Path $path) {
            @("Favorites", "FavoritesResolve", "FavoritesChanges", "FavoritesRemovedChanges", "TaskbarWinXP", "PinnedItems") | 
            ForEach-Object { Remove-ItemProperty -Path $path -Name $_ -ErrorAction SilentlyContinue }
        }
    }

    Remove-Item "$env:LOCALAPPDATA\Microsoft\Windows\Shell\LayoutModification.xml" -Force
    Remove-Item "$env:LOCALAPPDATA\Microsoft\Windows\Explorer\iconcache*" -Force
    Remove-Item "$env:LOCALAPPDATA\Microsoft\Windows\Explorer\thumbcache*" -Force

    # OneDrive removal
    Get-Process | Where-Object { $_.ProcessName -like "*onedrive*" } | Stop-Process -Force
    if (Test-Path "$env:SystemRoot\SysWOW64\OneDriveSetup.exe") {
        & "$env:SystemRoot\SysWOW64\OneDriveSetup.exe" /uninstall
    } elseif (Test-Path "$env:SystemRoot\System32\OneDriveSetup.exe") {
        & "$env:SystemRoot\System32\OneDriveSetup.exe" /uninstall
    }

    @(
        "$env:ProgramData\Microsoft\Windows\Start Menu\Programs\OneDrive.lnk",
        "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\OneDrive.lnk",
        "$env:PUBLIC\Desktop\OneDrive.lnk",
        "$env:USERPROFILE\Desktop\OneDrive.lnk",
        "$env:USERPROFILE\OneDrive",
        "$env:LOCALAPPDATA\Microsoft\OneDrive",
        "$env:ProgramData\Microsoft\OneDrive",
        "$env:SystemDrive\OneDriveTemp"
    ) | ForEach-Object { Remove-Item $_ -Force -Recurse }

    @(
        "HKCR:\CLSID\{018D5C66-4533-4307-9B53-224DE2ED1FE6}",
        "HKCR:\Wow6432Node\CLSID\{018D5C66-4533-4307-9B53-224DE2ED1FE6}",
        "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Desktop\NameSpace\{018D5C66-4533-4307-9B53-224DE2ED1FE6}"
    ) | ForEach-Object { Remove-Item -Path $_ -Recurse -Force }

    # Restart Explorer
    Get-Process explorer | Stop-Process -Force
    Start-Sleep -Seconds 2
    Start-Process explorer
}
catch {}
exit 
