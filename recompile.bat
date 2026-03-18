@echo off
setlocal

set PYSIDE6=C:\Users\Lukas\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\site-packages\PySide6

echo [1/4] Compiling UI...
%PYSIDE6%\uic.exe -g python tunnelconfig.ui -o tunnelconfig.py
if errorlevel 1 ( echo FAILED & exit /b 1 )

echo [2/4] Compiling resources...
%PYSIDE6%\rcc.exe -g python icons.qrc -o icons.py
if errorlevel 1 ( echo FAILED & exit /b 1 )

echo [3/4] Building exe...
python -m PyInstaller --clean --onefile --windowed --name ssh-tunnel-manager ^
    --hidden-import=icons ^
    --hidden-import=PySide6.QtWidgets ^
    --hidden-import=PySide6.QtCore ^
    --hidden-import=PySide6.QtGui ^
    --add-data "icons;icons" ^
    --add-data "config.example.yml;." ^
    app.py
if errorlevel 1 ( echo FAILED & exit /b 1 )

echo [4/4] Done! Output: dist\ssh-tunnel-manager.exe
endlocal
