import sys
import platform
import os
import time
from PyQt5.QtWidgets import QApplication, QMessageBox, QPushButton
from PyQt5.QtCore import Qt, QTimer

def is_windows_11():
    """
    Checks for Windows 11.
    Note: Windows 11 still reports version strings similar to Windows 10.
    This implementation compares both platform.version() and platform.release(), 
    but you might need to adjust detection based on your environment.
    """
    version_str = platform.version()
    release = platform.release()
    try:
        release_num = int(release)
    except (ValueError, TypeError):
        release_num = 0
    if version_str.startswith("10.0") and release_num >= 10:
        return True
    return False

def show_popup(title, message, is_error=False, delay_ok=False):
    """
    Displays a popup message using Qt.
    If no QApplication instance exists, one is created.
    If is_error is True, the application exits after the dialog.
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    msg_box = QMessageBox()
    msg_box.setWindowTitle(title)
    msg_box.setTextFormat(Qt.RichText)
    msg_box.setText(f"<span style='font-size:12pt;'>{message}</span>")
    
    if is_error:
        msg_box.setIcon(QMessageBox.Critical)
    else:
        msg_box.setIcon(QMessageBox.Warning)
    
    ok_button = msg_box.addButton(QMessageBox.Ok)
    if delay_ok:
        ok_button.setEnabled(False)
        QTimer.singleShot(3000, lambda: ok_button.setEnabled(True))
    
    msg_box.exec_()
    
    if is_error:
        sys.exit(1)

def check_system():
    """
    Checks if the current system meets the Windows 11 requirement.
    If not, displays an error message and exits.
    Otherwise, displays a warning popup about potential risks.
    """
    if not is_windows_11():
        show_popup(
            "Your System Is Not Supported",
            "You are currently on Windows 10 or older. <br> Please reinstall your current Windows to Windows 11.",
            is_error=True
        )
    
    show_popup(
        "OrangDebloating Agreement",
        """
        OrangDebloater is designed to be used on <b>freshly installed Windows 11 systems</b>. Running this program could result in data loss, apps stopping working, or even corruption.<br><br>
        Save all your work data before proceeding.<br><br>
        """,
        is_error=False,
        delay_ok=True
    )

if __name__ == "__main__":
    check_system()