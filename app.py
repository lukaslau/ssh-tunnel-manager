#!/usr/bin/python3

# -*- coding: utf-8 -*-

__author__ = "Md. Minhazul Haque"
__license__ = "GPLv3"

from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QApplication, QGridLayout, QDialog, QMessageBox, QComboBox, QSpinBox, QDialogButtonBox, QHBoxLayout
from PySide6.QtCore import QProcess, Qt, QUrl, QSharedMemory
from PySide6.QtGui import QIcon, QDesktopServices, QPixmap

from urllib.parse import urlparse
from deepdiff import DeepDiff

import sys
import yaml
import shutil
import time
import glob
import os
import re
from tunnel import Ui_Tunnel
from tunnelconfig import Ui_TunnelConfig
from vars import CONF_FILE, LANG, KEYS, ICONS, CMDS
import icons

def parse_ssh_config():
    hosts = []
    ssh_config_path = os.path.expanduser("~/.ssh/config")
    if os.path.exists(ssh_config_path):
        with open(ssh_config_path, "r") as f:
            for line in f:
                m = re.match(r'^\s*[Hh]ost\s+(.+)', line)
                if m:
                    for host in m.group(1).split():
                        if '*' not in host and '?' not in host:
                            hosts.append(host)
    return hosts

class TunnelConfig(QDialog):
    def __init__(self, parent, name, data):
        super(TunnelConfig, self).__init__(parent)

        self.ui = Ui_TunnelConfig()
        self.ui.setupUi(self)

        self.ui.name_field.setText(name)
        self.ui.remote_address.setText(data.get(KEYS.REMOTE_ADDRESS))
        self.ui.browser_open.setText(data.get(KEYS.BROWSER_OPEN) or "")
        self.ui.local_port.setValue(data.get(KEYS.LOCAL_PORT))

        self.ui.proxy_host.addItems(parse_ssh_config())
        self.ui.proxy_host.setCurrentText(data.get(KEYS.PROXY_HOST) or "")
        if self.ui.proxy_host.lineEdit():
            self.ui.proxy_host.lineEdit().setPlaceholderText("proxy-host")

        self.ui.remote_address.textChanged.connect(self.render_ssh_command)
        self.ui.proxy_host.currentTextChanged.connect(self.render_ssh_command)
        self.ui.local_port.valueChanged.connect(self.render_ssh_command)
        self.ui.copy.clicked.connect(self.do_copy_ssh_command)

        self.used_ports = set()
        self.used_names = set()

        self.render_ssh_command()

    def accept(self):
        name = self.get_name()
        if not name:
            QMessageBox.warning(self, LANG.OOPS, LANG.NAME_EMPTY)
            return
        if name in self.used_names:
            QMessageBox.warning(self, LANG.OOPS, LANG.NAME_IN_USE.format(name))
            return
        if self.ui.local_port.value() in self.used_ports:
            QMessageBox.warning(self, LANG.OOPS, LANG.PORT_IN_USE.format(self.ui.local_port.value()))
            return
        super().accept()

    def get_name(self):
        return self.ui.name_field.text().strip()

    def render_ssh_command(self):
        ssh_command = F"ssh -L 127.0.0.1:{self.ui.local_port.value()}:{self.ui.remote_address.text()} {self.ui.proxy_host.currentText()}"
        self.ui.ssh_command.setText(ssh_command)

    def do_copy_ssh_command(self):
        cb = QApplication.clipboard()
        cb.setText(self.ui.ssh_command.text())

    def as_dict(self):
        return {
            KEYS.REMOTE_ADDRESS: self.ui.remote_address.text(),
            KEYS.PROXY_HOST: self.ui.proxy_host.currentText(),
            KEYS.BROWSER_OPEN: self.ui.browser_open.text(),
            KEYS.LOCAL_PORT: self.ui.local_port.value(),
        }

class AddTunnelDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle(LANG.ADD_TUNNEL)
        self.setModal(True)

        layout = QGridLayout(self)
        mono = "font-family: Monospace;"

        layout.addWidget(QLabel("Name"), 0, 0)
        self.name_field = QLineEdit()
        self.name_field.setPlaceholderText("my-tunnel")
        layout.addWidget(self.name_field, 0, 1, 1, 2)

        layout.addWidget(QLabel("Local Port"), 1, 0)
        port_row = QHBoxLayout()
        self.local_port = QSpinBox()
        self.local_port.setStyleSheet(mono)
        self.local_port.setMaximum(65535)
        self.local_port.setSingleStep(1000)
        self.local_port.setValue(8443)
        port_row.addWidget(self.local_port)
        port_row.addStretch()
        layout.addLayout(port_row, 1, 1, 1, 2)

        layout.addWidget(QLabel("Remote Address"), 2, 0)
        self.remote_address = QLineEdit()
        self.remote_address.setStyleSheet(mono)
        self.remote_address.setPlaceholderText("10.10.10.10:443")
        layout.addWidget(self.remote_address, 2, 1, 1, 2)

        layout.addWidget(QLabel("Proxy Host"), 3, 0)
        self.proxy_host = QComboBox()
        self.proxy_host.setStyleSheet(mono)
        self.proxy_host.setEditable(True)
        self.proxy_host.addItems(parse_ssh_config())
        self.proxy_host.setCurrentIndex(-1)
        if self.proxy_host.lineEdit():
            self.proxy_host.lineEdit().setPlaceholderText("proxy-host")
        layout.addWidget(self.proxy_host, 3, 1, 1, 2)

        layout.addWidget(QLabel("Address to Open"), 4, 0)
        self.browser_open = QLineEdit()
        self.browser_open.setStyleSheet(mono)
        self.browser_open.setPlaceholderText("https://127.0.0.1:8443")
        layout.addWidget(self.browser_open, 4, 1, 1, 2)

        layout.addWidget(QLabel("SSH Command"), 5, 0)
        self.ssh_command = QLineEdit()
        self.ssh_command.setStyleSheet(mono)
        self.ssh_command.setReadOnly(True)
        layout.addWidget(self.ssh_command, 5, 1)
        copy_btn = QPushButton("Copy")
        copy_btn.clicked.connect(self.do_copy_ssh_command)
        layout.addWidget(copy_btn, 5, 2)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        btn_row.addWidget(button_box)
        layout.addLayout(btn_row, 6, 0, 1, 3)

        self.remote_address.textChanged.connect(self.render_ssh_command)
        self.proxy_host.currentTextChanged.connect(self.render_ssh_command)
        self.local_port.valueChanged.connect(self.render_ssh_command)

        self.used_ports = set()
        self.used_names = set()

        self.render_ssh_command()

    def accept(self):
        name = self.get_name()
        if not name:
            QMessageBox.warning(self, LANG.OOPS, LANG.NAME_EMPTY)
            return
        if name in self.used_names:
            QMessageBox.warning(self, LANG.OOPS, LANG.NAME_IN_USE.format(name))
            return
        if self.local_port.value() in self.used_ports:
            QMessageBox.warning(self, LANG.OOPS, LANG.PORT_IN_USE.format(self.local_port.value()))
            return
        super().accept()

    def render_ssh_command(self):
        ssh_command = F"ssh -L 127.0.0.1:{self.local_port.value()}:{self.remote_address.text()} {self.proxy_host.currentText()}"
        self.ssh_command.setText(ssh_command)

    def do_copy_ssh_command(self):
        QApplication.clipboard().setText(self.ssh_command.text())

    def get_name(self):
        return self.name_field.text().strip()

    def as_dict(self):
        return {
            KEYS.REMOTE_ADDRESS: self.remote_address.text(),
            KEYS.PROXY_HOST: self.proxy_host.currentText(),
            KEYS.BROWSER_OPEN: self.browser_open.text(),
            KEYS.LOCAL_PORT: self.local_port.value(),
        }

class Tunnel(QWidget):
    def __init__(self, name, data):
        super(Tunnel, self).__init__()

        self.ui = Ui_Tunnel()
        self.ui.setupUi(self)

        self.tunnelconfig = TunnelConfig(self, name, data)
        self.tunnelconfig.setWindowTitle(name)
        self.tunnelconfig.setModal(True)
        self.tunnelconfig.accepted.connect(self._on_config_accepted)
        self.ui.name.setText(name)

        self.tunnelconfig.icon = F"./icons/{name}.png"

        if not os.path.exists(self.tunnelconfig.icon):
          self.tunnelconfig.icon = ICONS.TUNNEL

        self.ui.icon.setPixmap(QPixmap(self.tunnelconfig.icon))
        self.ui.action_tunnel.clicked.connect(self.do_tunnel)
        self.ui.action_settings.clicked.connect(self.tunnelconfig.show)
        self.ui.action_open.clicked.connect(self.do_open_browser)

        self.process = None
        self._stopping = False

    def _on_config_accepted(self):
        self.ui.name.setText(self.tunnelconfig.get_name())

    def do_open_browser(self):
        browser_open = self.tunnelconfig.ui.browser_open.text()
        if browser_open:
            urlobj = urlparse(browser_open)
            local_port = self.tunnelconfig.ui.local_port.value()
            new_url = urlobj._replace(netloc=F"{urlobj.hostname}:{local_port}").geturl()
            QDesktopServices.openUrl(QUrl(new_url))

    def do_tunnel(self):
        if self.process:
            self.stop_tunnel()
        else:
            self.start_tunnel()

    def start_tunnel(self):
        self._stopping = False
        params = self.tunnelconfig.ui.ssh_command.text().split(" ")

        self.process = QProcess()
        self.process.errorOccurred.connect(self._on_process_error)
        self.process.finished.connect(self._on_process_finished)
        self.process.start(params[0], params[1:])

        self.ui.action_tunnel.setIcon(QIcon(ICONS.STOP))

        self.do_open_browser()

    def stop_tunnel(self):
        self._stopping = True
        if self.process:
            try:
                self.process.kill()
            except:
                pass
            self.process = None
        self.ui.action_tunnel.setIcon(QIcon(ICONS.START))

    def _on_process_error(self, error):
        if not self._stopping:
            self._stopping = True
            name = self.ui.name.text()
            QMessageBox.warning(self, LANG.OOPS, LANG.SSH_ERROR.format(name))
        self._cleanup_process()

    def _on_process_finished(self, exit_code, exit_status):
        if not self._stopping and exit_code != 0:
            self._stopping = True
            name = self.ui.name.text()
            QMessageBox.warning(self, LANG.OOPS, LANG.SSH_EXITED.format(name, exit_code))
        self._cleanup_process()

    def _cleanup_process(self):
        self.process = None
        self.ui.action_tunnel.setIcon(QIcon(ICONS.START))

class TunnelManager(QWidget):
    def __init__(self):
        super().__init__()

        with open(CONF_FILE, "r") as fp:
            self.data = yaml.load(fp, Loader=yaml.FullLoader)

        self.grid = QGridLayout(self)
        self.tunnels = []

        for i, name in enumerate(sorted(self.data.keys())):
            tunnel = Tunnel(name, self.data[name])
            self.tunnels.append(tunnel)
            self.grid.addWidget(tunnel, i, 0)
            tunnel.ui.action_settings.clicked.disconnect()
            tunnel.ui.action_settings.clicked.connect(
                lambda checked=False, t=tunnel: self.show_tunnel_settings(t)
            )

        self.add_button = QPushButton(LANG.ADD_TUNNEL)
        self.add_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.add_button.clicked.connect(self.do_add_tunnel)

        self.kill_button = QPushButton(LANG.KILL_SSH)
        self.kill_button.setIcon(QIcon(ICONS.KILL_SSH))
        self.kill_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.kill_button.clicked.connect(self.do_killall_ssh)

        self.grid.addWidget(self.add_button, i+1, 0)
        self.grid.addWidget(self.kill_button, i+2, 0)

        self.setLayout(self.grid)
        self.resize(10, 10)
        self.setWindowTitle(LANG.TITLE)
        self.setWindowIcon(QIcon(ICONS.TUNNEL))
        self.show()

    def _get_used_ports(self, exclude=None):
        return {t.tunnelconfig.ui.local_port.value() for t in self.tunnels if t is not exclude}

    def _get_used_names(self, exclude=None):
        return {t.ui.name.text() for t in self.tunnels if t is not exclude}

    def show_tunnel_settings(self, tunnel):
        tunnel.tunnelconfig.used_ports = self._get_used_ports(exclude=tunnel)
        tunnel.tunnelconfig.used_names = self._get_used_names(exclude=tunnel)
        tunnel.tunnelconfig.show()

    def do_add_tunnel(self):
        dialog = AddTunnelDialog(self)
        dialog.used_ports = self._get_used_ports()
        dialog.used_names = self._get_used_names()
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        name = dialog.get_name()
        data = dialog.as_dict()

        tunnel = Tunnel(name, data)
        self.tunnels.append(tunnel)
        tunnel.ui.action_settings.clicked.disconnect()
        tunnel.ui.action_settings.clicked.connect(
            lambda checked=False, t=tunnel: self.show_tunnel_settings(t)
        )

        row = len(self.tunnels) - 1
        self.grid.removeWidget(self.add_button)
        self.grid.removeWidget(self.kill_button)
        self.grid.addWidget(tunnel, row, 0)
        self.grid.addWidget(self.add_button, row + 1, 0)
        self.grid.addWidget(self.kill_button, row + 2, 0)

        self.resize(10, 10)

    def do_killall_ssh(self):
        for tunnel in self.tunnels:
            tunnel.stop_tunnel()
        if os.name == 'nt':
            os.system(CMDS.SSH_KILL_WIN)
        else:
            os.system(CMDS.SSH_KILL_NIX)

    def closeEvent(self, event):
        data = {}
        for tunnel in self.tunnels:
            name = tunnel.ui.name.text()
            data[name] = tunnel.tunnelconfig.as_dict()

        changed = DeepDiff(self.data, data, ignore_order=True)

        if changed:
            timestamp = int(time.time())
            shutil.copy(CONF_FILE, F"{CONF_FILE}-{timestamp}")
            with open(CONF_FILE, "w") as fp:
                yaml.dump(data, fp)
            backup_configs = glob.glob(F"{CONF_FILE}-*")
            if len(backup_configs) > 10:
                for config in sorted(backup_configs, reverse=True)[10:]:
                    os.remove(config)
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    sm = QSharedMemory("3866273d-f4d5-4bf3-b27b-772ca7915a61")

    if not sm.create(1):
        mb = QMessageBox()
        mb.setIcon(QMessageBox.Icon.Information)
        mb.setText(LANG.ALREADY_RUNNING)
        mb.setWindowTitle(LANG.OOPS)
        mb.setStandardButtons(QMessageBox.StandardButton.Close)
        mb.show()
    elif not os.path.exists(CONF_FILE):
        mb = QMessageBox()
        mb.setIcon(QMessageBox.Icon.Information)
        mb.setText(LANG.CONF_NOT_FOUND)
        mb.setWindowTitle(LANG.OOPS)
        mb.setStandardButtons(QMessageBox.StandardButton.Close)
        mb.show()
    else:
        tm = TunnelManager()

    sys.exit(app.exec())
