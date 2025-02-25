import sys
import ctypes
import os
import tempfile
import subprocess
import requests
import winreg
import shutil
import time
import logging
import json

LOG_FILE = "info.txt"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
def log(message):
    logging.info(message)
    print(message)

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception as e:
        log(f"Error checking admin status: {e}")
        return False


if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(sys.argv), None, 1
    )
    sys.exit(0)


def apply_registry_changes():
    log("Applying registry modifications...")
    try:
        registry_modifications = [
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "TaskbarAl", winreg.REG_DWORD, 0),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", "AppsUseLightTheme", winreg.REG_DWORD, 0),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", "SystemUsesLightTheme", winreg.REG_DWORD, 0),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Accent", "AccentColorMenu", winreg.REG_DWORD, 1),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", "ColorPrevalence", winreg.REG_DWORD, 1),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\DWM", "AccentColorInStartAndTaskbar", winreg.REG_DWORD, 1),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Accent", "AccentPalette", winreg.REG_BINARY, b"\x00" * 32),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\GameDVR", "AppCaptureEnabled", winreg.REG_DWORD, 0),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\PolicyManager\default\ApplicationManagement\AllowGameDVR", "Value", winreg.REG_DWORD, 0),
            (winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop", "MenuShowDelay", winreg.REG_SZ, "0"),
            (winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop\WindowMetrics", "MinAnimate", winreg.REG_DWORD, 0),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "ExtendedUIHoverTime", winreg.REG_DWORD, 1),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "HideFileExt", winreg.REG_DWORD, 0),
            (winreg.HKEY_CURRENT_USER, r"Control Panel\Colors", "Hilight", winreg.REG_SZ, "0 0 0"),
            (winreg.HKEY_CURRENT_USER, r"Control Panel\Colors", "HotTrackingColor", winreg.REG_SZ, "0 0 0"),
        ]
        for root_key, key_path, value_name, value_type, value in registry_modifications:
            try:
                with winreg.CreateKeyEx(root_key, key_path, 0, winreg.KEY_SET_VALUE) as key:
                    winreg.SetValueEx(key, value_name, 0, value_type, value)
                    log(f"Applied {value_name} to {key_path}")
            except Exception as e:
                log(f"Failed to modify {value_name} in {key_path}: {e}")
        log("Registry was applied successfully.")
        subprocess.run(["taskkill", "/F", "/IM", "explorer.exe"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["cmd", "/c", "start", "explorer.exe"], shell=True)


        log("Explorer restarted to apply all tasks.")
        run_edge_remover()
        log("Edge removal initiated successfully.")
    except Exception as e:
        log(f"Error applying registry modifications: {e}")

def disable_reserved_storage():
    command = "Set-WindowsReservedStorageState -State Disabled"
    try:
        result = subprocess.run(
            ["powershell", "-Command", command],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            print("Reserved storage has been disabled successfully.")
        else:
            print("Failed to disable reserved storage:", result.stderr)
    except Exception as e:
        print("Error executing the command:", e)

def run_edge_remover():
    log("Starting Edge remover script execution...")
    try:
        script_url = "https://raw.githubusercontent.com/InterJavas-Projects/OrangDebloat/main/edge.ps1"
        temp_dir = tempfile.gettempdir()
        script_path = os.path.join(temp_dir, "edge.ps1")
        log(f"Downloading Edge remover script from: {script_url}")
        log(f"Target script path: {script_path}")

        response = requests.get(script_url, timeout=30)
        log(f"Download response status code: {response.status_code}")
        response.raise_for_status()

        with open(script_path, "wb") as file:
            file.write(response.content)
        log("Edge remover script saved successfully.")

        powershell_command = (
            f"Set-ExecutionPolicy Bypass -Scope Process -Force; "
            f"& '{script_path}'; exit"
        )
        log(f"Executing PowerShell command: {powershell_command}")

        process = subprocess.run(
            ["powershell", "-Command", powershell_command],
            capture_output=True,
            text=True,
            timeout=300
        )
        if process.returncode == 0:
            log("Edge remover script executed successfully.")
        else:
            log(f"Edge remover script failed with return code {process.returncode}")
            log(f"Error output: {process.stderr}")
        run_oouninstall()
    except requests.RequestException as e:
        log(f"Network error during Edge remover download: {e}")
        run_oouninstall()
    except IOError as e:
        log(f"File I/O error while saving Edge remover script: {e}")
        run_oouninstall()
    except Exception as e:
        log(f"Unexpected error during Edge remover execution: {e}")
        run_oouninstall()


def run_oouninstall():
    log("Starting uninstallation of select programs...")
    try:
        script_url = "https://raw.githubusercontent.com/InterJavas-Projects/OrangDebloat/refs/heads/main/del_out_one.ps1"
        temp_dir = tempfile.gettempdir()
        script_path = os.path.join(temp_dir, "del_out_one.ps1")
        log(f"Downloading uninstallation script from: {script_url}")
        log(f"Target script path: {script_path}")

        response = requests.get(script_url, timeout=30)
        log(f"Download response status code: {response.status_code}")
        response.raise_for_status()

        with open(script_path, "wb") as file:
            file.write(response.content)
        log("Uninstallation script saved successfully.")

        powershell_command = f"Set-ExecutionPolicy Bypass -Scope Process -Force; & '{script_path}'"
        log(f"Executing PowerShell command: {powershell_command}")

        process = subprocess.run(
            ["powershell", "-Command", powershell_command],
            capture_output=True,
            text=True,
            timeout=300
        )
        if process.returncode == 0:
            log("Uninstallation script executed successfully.")
        else:
            log(f"Uninstallation script failed with return code {process.returncode}")
        run_tweaks()
    except Exception as e:
        log(f"Unexpected error during uninstallation: {e}")
        run_tweaks()


def run_tweaks():
    log("Starting system tweaks...")
    if not is_admin():
        log("Must be run as an administrator.")
        sys.exit(1)
    try:
        config_url = "https://raw.githubusercontent.com/InterJavas-Projects/OrangDebloat/main/tasks.json"
        log(f"Downloading config from: {config_url}")
        response = requests.get(config_url, timeout=30)
        response.raise_for_status()
        config = json.loads(response.content.decode('utf-8-sig'))
        temp_dir = tempfile.gettempdir()
        json_path = os.path.join(temp_dir, "custom_config.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
        log(f"Config saved to {json_path}")

        log_file = os.path.join(temp_dir, "cttwinutil.log")
        command = [
            "powershell",
            "-NoProfile",
            "-NonInteractive",
            "-Command",
            (
                "$ErrorActionPreference = 'SilentlyContinue'; "
                "iex \"& { $(irm christitus.com/win) } -Config '{0}' -Run\" *>&1 | "
                "Tee-Object -FilePath '{1}'"
            ).format(json_path, log_file)
        ]
        log(f"Executing system tweaks command: {' '.join(command)}")
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace',
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        while True:
            output = process.stdout.readline()
            if output:
                output = output.strip()
                log(f"CTT Output: {output}")
                if "Tweaks are Finished" in output:
                    log("Tweaks completed successfully. Terminating tweak process.")
                    subprocess.run(
                        ["powershell", "-Command", "Stop-Process -Name powershell -Force"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    break
            else:
                if process.poll() is not None:
                    break
        run_winconfig()
    except Exception as e:
        log(f"Error during tweaks execution: {e}")
        run_winconfig()


def run_winconfig():
    log("Starting Windows configuration process...")
    try:
        script_url = "https://win11debloat.raphi.re/"
        temp_dir = tempfile.gettempdir()
        script_path = os.path.join(temp_dir, "Win11Debloat.ps1")
        log(f"Downloading Windows configuration script from: {script_url}")
        log(f"Target script path: {script_path}")

        response = requests.get(script_url, timeout=30)
        log(f"Download response status code: {response.status_code}")
        response.raise_for_status()

        with open(script_path, "wb") as file:
            file.write(response.content)
        log("Windows configuration script saved successfully.")

        powershell_command = (
            "Set-ExecutionPolicy Bypass -Scope Process -Force; "
            f"& '{script_path}' -Silent -RemoveApps -RemoveGamingApps -DisableTelemetry "
            "-DisableBing -DisableSuggestions -DisableLockscreenTips -RevertContextMenu "
            "-TaskbarAlignLeft -HideSearchTb -DisableWidgets -DisableCopilot -ExplorerToThisPC "
            "-ClearStartAllUsers -DisableDVR -DisableStartRecommended "
            "-DisableMouseAcceleration"
        )
        log("Executing Windows configuration command:")
        log(f"Command: {powershell_command}")

        process = subprocess.run(
            ["powershell", "-Command", powershell_command],
            capture_output=True,
            text=True,
            timeout=300
        )
        if process.returncode == 0:
            log("Windows configuration executed successfully.")
            log(f"Process stdout: {process.stdout}")
        else:
            log(f"Windows configuration failed with return code: {process.returncode}")
            log(f"Process stderr: {process.stderr}")
        run_updatepolicychanger()
    except requests.RequestException as e:
        log(f"Network error during Windows configuration download: {e}")
        run_updatepolicychanger()
    except IOError as e:
        log(f"File I/O error while saving Windows configuration script: {e}")
        run_updatepolicychanger()
    except Exception as e:
        log(f"Unexpected error during Windows configuration: {e}")
        run_updatepolicychanger()


def run_updatepolicychanger():
    log("Starting UpdatePolicyChanger script execution...")
    try:
        script_url = "https://raw.githubusercontent.com/InterJavas-Projects/OrangDebloat/main/updates.ps1"
        temp_dir = tempfile.gettempdir()
        script_path = os.path.join(temp_dir, "updates.ps1")
        log(f"Downloading UpdatePolicyChanger script from: {script_url}")
        log(f"Target script path: {script_path}")

        response = requests.get(script_url, timeout=30)
        log(f"Download response status code: {response.status_code}")
        response.raise_for_status()

        content_length = len(response.content)
        log(f"Downloaded content length: {content_length} bytes")
        with open(script_path, "wb") as file:
            file.write(response.content)
        log("UpdatePolicyChanger script saved successfully.")
        if not os.path.exists(script_path):
            raise IOError("Script file not found after saving")
        file_size = os.path.getsize(script_path)
        log(f"Saved file size: {file_size} bytes")
        powershell_command = (
            "Set-ExecutionPolicy Bypass -Scope Process -Force; "
            f"& '{script_path}'; exit"
        )
        log(f"Executing UpdatePolicyChanger command: {powershell_command}")
        process = subprocess.run(
            ["powershell", "-Command", powershell_command],
            capture_output=True,
            text=True,
            timeout=300
        )
        log(f"UpdatePolicyChanger process return code: {process.returncode}")
        if process.stdout:
            log(f"Process output: {process.stdout}")
        if process.stderr:
            log(f"Process errors: {process.stderr}")
        if process.returncode == 0:
            log("UpdatePolicyChanger executed successfully.")
        else:
            log("UpdatePolicyChanger execution failed, continuing finalization...")
        finalize_installation()
    except Exception as e:
        log(f"Critical error in UpdatePolicyChanger: {e}")
        log("Proceeding to finalization due to critical error...")
        finalize_installation()


def finalize_installation():
    log("Installation complete. Restarting system...")
    try:
        subprocess.run(["shutdown", "/r", "/t", "0"], check=True)
    except subprocess.CalledProcessError as e:
        log(f"Error during system restart: {e}")
        try:
            os.system("shutdown /r /t 0")
        except Exception as inner_e:
            log(f"Failed to restart system: {inner_e}")

def download_exe():
    url = "https://github.com/InterJavas-Projects/OrangWallpapers/releases/download/2.0/orangwp.exe"
    response = requests.get(url)
    if response.status_code == 200:
        desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        file_path = os.path.join(desktop_path, "orangwp.exe")
        with open(file_path, 'wb') as file:
            file.write(response.content)
        log(f"Downloaded orangwp.exe to {file_path}")
    else:
        log(f"Failed to download file: {response.status_code}")

def finalize_installation():
    log("Installation complete. Restarting system...")
    try:
        subprocess.run(["shutdown", "/r", "/t", "0"], check=True)
    except subprocess.CalledProcessError as e:
        log(f"Error during system restart: {e}")
        try:
            os.system("shutdown /r /t 0")
        except Exception as inner_e:
            log(f"Failed to restart system: {inner_e}")

if __name__ == "__main__":
    apply_registry_changes()
    download_exe()