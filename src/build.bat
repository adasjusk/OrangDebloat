@echo off
nuitka --onefile --standalone --enable-plugin=pyqt5 --remove-output --windows-icon-from-ico=ICON.ico --windows-console-mode=disable --windows-uac-admin --output-dir=dist --follow-imports --include-data-files="Minecraftia-Regular.ttf=Minecraftia-Regular.ttf" --include-data-files="browser_selection.png=browser_selection.png" orangd.py
pause