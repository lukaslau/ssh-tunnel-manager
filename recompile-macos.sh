#!/bin/bash
set -e

echo "[1/4] Compiling UI..."
pyside6-uic -g python tunnelconfig.ui -o tunnelconfig.py

echo "[2/4] Compiling resources..."
pyside6-rcc -g python icons.qrc -o icons.py

echo "[3/4] Building app..."
python3 -m PyInstaller --clean --onefile --windowed --name ssh-tunnel-manager \
    --hidden-import=icons \
    --hidden-import=PySide6.QtWidgets \
    --hidden-import=PySide6.QtCore \
    --hidden-import=PySide6.QtGui \
    --add-data "icons:icons" \
    --add-data "config.example.yml:." \
    app.py

echo "[4/4] Done! Output: dist/ssh-tunnel-manager"
