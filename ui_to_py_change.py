from PyQt5 import uic

with open("mainWindow_ui.py", 'w', encoding="utf-8") as f_out:
    uic.compileUi("mainWindow.ui", f_out)
