# SSH Tunnel Manager

A cross-platform GUI application for managing SSH tunnels, built with PySide6.

![SSH Tunnel Manager](.screenshot.png)

## Features

- Manage multiple SSH tunnels from a single interface
- Start/stop tunnels with one click
- Auto-open URLs in browser when tunnel starts
- Custom icons per tunnel
- Configuration backup on save (keeps last 10 backups)
- Single instance enforcement

## Supported Platforms

Pre-built binaries are available for:
- Windows (x64)
- Linux (x64)
- macOS (Apple Silicon)

## Installation

### Standalone Executable

Download the latest release from the [Releases](https://github.com/mdminhazulhaque/ssh-tunnel-manager/releases) page.

**Windows:** Double-click `ssh-tunnel-manager.exe` to run.

**Linux:**
```bash
chmod +x ssh-tunnel-manager
./ssh-tunnel-manager
```

**macOS:**
```bash
chmod +x ssh-tunnel-manager
./ssh-tunnel-manager
```

On macOS, you may see a security warning saying the app "cannot be opened because the developer cannot be verified". To allow it:
1. Open **System Settings → Privacy & Security**
2. Scroll down and click **Open Anyway** next to the blocked app message

> **Note:** The first launch may take a few seconds as the app extracts its bundled resources. This is normal for static binaries.

### From Source

```bash
# Install dependencies
pip install -r requirements.txt

# Compile UI and resource files
make

# Create your configuration
cp config.example.yml config.yml

# Run the application
python3 app.py
```

#### Linux Desktop Shortcut

Edit `sshtunnelmgr.desktop` with your paths and copy it to create an application menu entry:

```bash
cp sshtunnelmgr.desktop ~/.local/share/applications/
```

## Configuration

Tunnels are configured in `config.yml`. See `config.example.yml` for the format.

### Example Entry

```yaml
rabbitmq:
  remote_address: 10.10.10.30:15672
  proxy_host: demo-bastion
  local_port: 15672
  browser_open: http://127.0.0.1
```

This creates a tunnel equivalent to:

```bash
ssh -L 127.0.0.1:15672:10.10.10.30:15672 demo-bastion
```

### Configuration Options

| Key | Required | Description |
|-----|----------|-------------|
| `remote_address` | Yes | Target host:port to tunnel to |
| `proxy_host` | Yes | SSH bastion/jump host |
| `local_port` | Yes | Local port to bind |
| `browser_open` | No | URL to open when tunnel starts (local_port is appended automatically) |

## Custom Icons

Place image files (PNG/JPG/BMP) in the `./icons/` directory with the same name as the tunnel identifier.

For example, for a tunnel named `kubernetes`, place an icon at `./icons/kubernetes.png`.

## SSH Binding on Privileged Ports

Binding to ports below 1024 requires elevated privileges. On Linux/macOS, you can grant this capability to SSH:

```bash
sudo setcap CAP_NET_BIND_SERVICE=+eip /usr/bin/ssh
```

## Migration

If migrating from older versions, change `local_address` to `local_port` in your config and ensure it's a number (not a string).

## TODO

- Gracefully close SSH sessions instead of using `kill`
- Add/edit/delete tunnels via the GUI

## Known Issues

- Icons may not be visible in static builds
