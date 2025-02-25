import sys
import os
import ctypes
import subprocess
import threading
import logging
import time
import platform
import winreg
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from browserins import BrowserSelectScreen
from process import InstallScreen
import debloat_windows
import browser
import winver
ORANGDEBLOAT_VERSION = "1.0.1"
LOG_FILE = "info.txt"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
def get_windows_info():
    """Fetch Windows version details."""
    try:
        windows_version = platform.win32_ver()
        reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
        key = winreg.OpenKey(reg, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")

        build_number = winreg.QueryValueEx(key, "CurrentBuildNumber")[0]
        product_name = winreg.QueryValueEx(key, "ProductName")[0]
        try:
            display_version = winreg.QueryValueEx(key, "DisplayVersion")[0]
        except Exception:
            display_version = "N/A"

        return {
            'version': windows_version[0],
            'build': build_number,
            'product_name': product_name,
            'display_version': display_version
        }
    except Exception as e:
        logging.error(f"Error fetching Windows info: {e}")
        return None

def is_running_as_admin():
    """Check if the script is running with administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception as e:
        logging.error(f"Admin privilege check failed: {e}")
        return False

def restart_as_admin():
    """Restart script with admin privileges if not already running as admin."""
    try:
        script = sys.argv[0]
        params = ' '.join(sys.argv[1:])
        logging.info("Restarting with admin privileges...")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}" {params}', None, 1)
        sys.exit()
    except Exception as e:
        logging.error(f"Error restarting as admin: {e}")

def perform_installation(selected_browser, install_screen):
    """Run installation steps in a separate thread."""
    try:
        logging.info(f"Starting browser installation: {selected_browser} ...")
        browser.install_browser(selected_browser)
        logging.info(f"{selected_browser} installation complete.")
    except Exception as e:
        logging.error(f"Error during browser installation: {e}")

    try:
        logging.info("Applying Windows registry modifications and customizations...")
        debloat_windows.apply_registry_changes()
        logging.info("Registry modifications complete.")
    except Exception as e:
        logging.error(f"Error applying registry changes: {e}")

    logging.info("All installations and configurations completed.")
    QTimer.singleShot(0, install_screen.close)

    logging.info("Installation complete. Restarting system...")
    try:
        debloat_windows.finalize_installation()
    except Exception as e:
        logging.error(f"Error during finalization: {e}")

def main():
    logging.info("Starting OrangDebloat Installer")
    logging.info(f"OrangDebloat Version: {ORANGDEBLOAT_VERSION}")
    windows_info = get_windows_info()
    if windows_info:
        logging.info(
            f"Windows Version: {windows_info['product_name']} | "
            f"Build: {windows_info['build']} | "
            f"Display: {windows_info['display_version']}"
        )
    else:
        logging.warning("Unable to fetch Windows version details.")
    app = QApplication(sys.argv)

    try:
        logging.info("Running Windows system check...")
        winver.check_system()
        logging.info("System check passed.")
    except Exception as e:
        logging.error(f"System check failed: {e}")
    selected_browser = None
    try:
        logging.info("Displaying browser selection screen...")
        browser_select_screen = BrowserSelectScreen()
        browser_select_screen.show()
        def poll_browser_selection():
            nonlocal selected_browser
            if browser_select_screen.selected_browser is not None:
                selected_browser = browser_select_screen.selected_browser
                logging.info(f"Browser Selected: {selected_browser}")
                browser_select_screen.close()
            else:
                QTimer.singleShot(100, poll_browser_selection)

        poll_browser_selection()
    except Exception as e:
        logging.error(f"Error during browser selection: {e}")
        app.exit(1)
        return
    while selected_browser is None:
        app.processEvents()
        time.sleep(0.05)
    try:
        logging.info("Displaying installation screen...")
        install_screen = InstallScreen()
        install_screen.show()
    except Exception as e:
        logging.error(f"Error during installation screen setup: {e}")
        app.exit(1)
        return
    try:
        logging.info("Starting installation process in a separate thread...")
        install_thread = threading.Thread(target=perform_installation, args=(selected_browser, install_screen))
        install_thread.start()
        while install_thread.is_alive():
            app.processEvents()
            time.sleep(0.05)

    except Exception as e:
        logging.error(f"Error starting installation thread: {e}")
    app.exec_()
if __name__ == "__main__":
    if not is_running_as_admin():
        restart_as_admin()
    else:
        main()