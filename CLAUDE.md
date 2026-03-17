# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build Commands

```bash
# Install dependencies
pip3 install -r requirements.txt

# Compile UI and resource files (required before running)
make

# Compile only UI files
make ui

# Compile only resource file (icons)
make resources

# Clean generated files
make clean

# Run the application
python3 app.py
```

## Architecture

SSH Tunnel Manager is a PySide6 desktop application for managing SSH tunnels via a GUI.

### Key Files

- **app.py** - Main application entry point containing three main classes:
  - `TunnelManager` - Main window that loads config and displays tunnel list
  - `Tunnel` - Widget representing a single tunnel entry with start/stop/settings buttons
  - `TunnelConfig` - Dialog for editing tunnel settings (remote address, proxy host, local port)

- **vars.py** - Constants for configuration keys, UI strings, icon paths, and system commands

- **tunnel.ui / tunnelconfig.ui** - Qt Designer UI files (compiled to Python via `pyside6-uic`)

- **icons.qrc** - Qt resource file for bundled icons (compiled to Python via `pyside6-rcc`)

### Generated Files (not in git)

These files are compiled from `.ui` and `.qrc` sources:
- `tunnel.py` - from tunnel.ui
- `tunnelconfig.py` - from tunnelconfig.ui
- `icons.py` - from icons.qrc

### Configuration

The app reads tunnel configurations from `config.yml` (see `config.example.yml` for format). Each tunnel entry specifies:
- `remote_address` - Target host:port
- `proxy_host` - SSH bastion/jump host
- `local_port` - Local port to bind
- `browser_open` - Optional URL to open after tunnel starts (port is replaced with `local_port` at open time)

Tunnel names (top-level YAML keys) are displayed in the UI and sorted alphabetically. A tunnel-specific icon is loaded from `icons/{name}.png` if it exists, otherwise falls back to the default tunnel icon.

The SSH command executed per tunnel: `ssh -L 127.0.0.1:{local_port}:{remote_address} {proxy_host}`

### Single Instance

Uses `QSharedMemory` with a fixed UUID to prevent multiple instances.

### Config Persistence

On close, if config changed (detected via `deepdiff`), saves to `config.yml` and creates timestamped backup (keeps last 10).

### Releases

Releases are built via GitHub Actions (`.github/workflows/build.yml`) and triggered by pushing a `v*` tag. Builds produce standalone executables for win64, linux64, and macos-arm64 using PyInstaller.
