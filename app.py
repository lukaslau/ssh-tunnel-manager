#!/usr/bin/python3

# -*- coding: utf-8 -*-

__author__ = "Md. Minhazul Haque"
__license__ = "GPLv3"

from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QApplication,
    QVBoxLayout, QHBoxLayout, QGridLayout, QDialog, QMessageBox,
    QComboBox, QSpinBox, QDialogButtonBox, QScrollArea, QFrame, QSizePolicy,
    QSystemTrayIcon, QMenu)
from PySide6.QtCore import QProcess, Qt, QUrl, QSharedMemory, Signal, QTimer, QSize
from PySide6.QtGui import QIcon, QDesktopServices, QPainter, QColor

from urllib.parse import urlparse

import sys
import yaml
import os
import re
import socket
import subprocess
import atexit
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


class ToggleSwitch(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setFixedSize(44, 26)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setStyleSheet("border: none; background: transparent;")

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(Qt.PenStyle.NoPen)

        track_color = QColor("#34C759") if self.isChecked() else QColor("#E5E5EA")
        p.setBrush(track_color)
        p.drawRoundedRect(0, 3, 44, 20, 10, 10)

        thumb_x = 24 if self.isChecked() else 2
        p.setBrush(QColor("white"))
        p.drawEllipse(thumb_x, 4, 18, 18)
        p.end()


class StatusDot(QWidget):
    COLORS = {
        "idle":       "#C7C7CC",
        "connecting": "#FF9500",
        "connected":  "#34C759",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(10, 10)
        self._color = QColor(self.COLORS["idle"])

    def set_status(self, status):
        self._color = QColor(self.COLORS.get(status, self.COLORS["idle"]))
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(self._color)
        p.drawEllipse(0, 0, 10, 10)


class TunnelConfig(QDialog):
    def __init__(self, parent, name, data):
        super().__init__(parent)

        self.ui = Ui_TunnelConfig()
        self.ui.setupUi(self)

        self.ui.name_field.setText(name)
        self.ui.remote_address.setText(data.get(KEYS.REMOTE_ADDRESS) or "")
        self.ui.browser_open.setText(data.get(KEYS.BROWSER_OPEN) or "")
        self.ui.local_port.setValue(data.get(KEYS.LOCAL_PORT) or 8443)

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
        ssh_command = F"ssh -o StrictHostKeyChecking=accept-new -L 127.0.0.1:{self.ui.local_port.value()}:{self.ui.remote_address.text()} {self.ui.proxy_host.currentText()}"
        self.ui.ssh_command.setText(ssh_command)

    def do_copy_ssh_command(self):
        QApplication.clipboard().setText(self.ui.ssh_command.text())

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
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
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
        ssh_command = F"ssh -o StrictHostKeyChecking=accept-new -L 127.0.0.1:{self.local_port.value()}:{self.remote_address.text()} {self.proxy_host.currentText()}"
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
    deleted = Signal()
    state_changed = Signal()

    STATUS_IDLE       = "idle"
    STATUS_CONNECTING = "connecting"
    STATUS_CONNECTED  = "connected"

    BADGE_STYLES = {
        STATUS_IDLE:       ("Not connected",   "color:#8E8E93; background:#F2F2F7; border-radius:8px; padding:2px 8px; font-size:11px;"),
        STATUS_CONNECTING: ("Connecting...",   "color:#FF9500; background:#FFF3E0; border-radius:8px; padding:2px 8px; font-size:11px;"),
        STATUS_CONNECTED:  ("Connected",       "color:#34C759; background:#E8F8ED; border-radius:8px; padding:2px 8px; font-size:11px;"),
    }

    def __init__(self, name, data):
        super().__init__()
        self._status = self.STATUS_IDLE
        self.process = None
        self._stopping = False
        self.tunnel_name = name
        self.data = dict(data)

        self._connect_timer = QTimer(self)
        self._connect_timer.setSingleShot(True)
        self._connect_timer.timeout.connect(self._on_connect_confirmed)

        self._timeout_timer = QTimer(self)
        self._timeout_timer.setSingleShot(True)
        self._timeout_timer.timeout.connect(self._on_connect_timeout)

        self._build_ui(name)
        self._update_command_preview()
        self._update_status(self.STATUS_IDLE)

    def _build_ui(self, name):
        self.setMinimumHeight(68)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        main = QHBoxLayout(self)
        main.setContentsMargins(14, 12, 14, 12)
        main.setSpacing(10)

        self.status_dot = StatusDot()
        main.addWidget(self.status_dot, 0, Qt.AlignmentFlag.AlignVCenter)

        info = QVBoxLayout()
        info.setSpacing(3)
        info.setContentsMargins(0, 0, 0, 0)

        self.name_label = QLabel(name)
        self.name_label.setStyleSheet("font-size:13px; font-weight:600; color:#1C1C1E;")

        self.command_preview = QLabel()
        self.command_preview.setStyleSheet("font-size:11px; color:#8E8E93; font-family:monospace;")

        info.addWidget(self.name_label)
        info.addWidget(self.command_preview)
        main.addLayout(info, 1)

        self.status_badge = QLabel()
        self.status_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_badge.setFixedWidth(110)
        main.addWidget(self.status_badge, 0, Qt.AlignmentFlag.AlignVCenter)

        btn_style = "QPushButton{border:none;background:transparent;border-radius:4px;padding:3px;} QPushButton:hover{background:#F0F0F5;}"

        self.settings_btn = QPushButton()
        self.settings_btn.setIcon(QIcon(ICONS.SETTINGS))
        self.settings_btn.setFixedSize(28, 28)
        self.settings_btn.setFlat(True)
        self.settings_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings_btn.setStyleSheet(btn_style)
        main.addWidget(self.settings_btn, 0, Qt.AlignmentFlag.AlignVCenter)

        self.delete_btn = QPushButton()
        self.delete_btn.setIcon(QIcon(ICONS.TRASH))
        self.delete_btn.setFixedSize(28, 28)
        self.delete_btn.setFlat(True)
        self.delete_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_btn.setStyleSheet("QPushButton{border:none;background:transparent;border-radius:4px;padding:3px;} QPushButton:hover{background:#FFF0F0;}")
        self.delete_btn.clicked.connect(self.deleted)
        main.addWidget(self.delete_btn, 0, Qt.AlignmentFlag.AlignVCenter)

        self.toggle = ToggleSwitch()
        self.toggle.toggled.connect(self._on_toggled)
        main.addWidget(self.toggle, 0, Qt.AlignmentFlag.AlignVCenter)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor("white"))
        p.drawRoundedRect(self.rect(), 10, 10)

    def _update_command_preview(self):
        proxy  = self.data.get(KEYS.PROXY_HOST) or "proxy-host"
        port   = self.data.get(KEYS.LOCAL_PORT) or 0
        remote = self.data.get(KEYS.REMOTE_ADDRESS) or "remote:port"
        self.command_preview.setText(f">_ {proxy} → localhost:{port} → {remote}")

    def _update_status(self, status):
        self._status = status
        self.status_dot.set_status(status)
        text, style = self.BADGE_STYLES[status]
        self.status_badge.setText(text)
        self.status_badge.setStyleSheet(style)
        self.state_changed.emit()

    def _on_toggled(self, checked):
        if checked:
            self.start_tunnel()
        else:
            self.stop_tunnel()

    def do_open_browser(self):
        browser_open = self.data.get(KEYS.BROWSER_OPEN)
        if browser_open:
            urlobj = urlparse(browser_open)
            local_port = self.data.get(KEYS.LOCAL_PORT)
            new_url = urlobj._replace(netloc=F"{urlobj.hostname}:{local_port}").geturl()
            QDesktopServices.openUrl(QUrl(new_url))

    def _is_port_open(self):
        port = self.data.get(KEYS.LOCAL_PORT)
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.3):
                return True
        except OSError:
            return False

    def start_tunnel(self):
        self._stopping = False
        port   = self.data.get(KEYS.LOCAL_PORT)
        remote = self.data.get(KEYS.REMOTE_ADDRESS)
        proxy  = self.data.get(KEYS.PROXY_HOST)
        params = ["ssh", "-o", "StrictHostKeyChecking=accept-new",
                  "-L", f"127.0.0.1:{port}:{remote}", proxy]

        self.process = QProcess()
        self.process.errorOccurred.connect(self._on_process_error)
        self.process.finished.connect(self._on_process_finished)
        self.process.start(params[0], params[1:])

        self._update_status(self.STATUS_CONNECTING)
        self._connect_timer.start(1000)
        self._timeout_timer.start(40000)
        self.do_open_browser()

    def stop_tunnel(self):
        self._stopping = True
        self._connect_timer.stop()
        self._timeout_timer.stop()
        if self.process:
            try:
                self.process.kill()
            except:
                pass
            self.process = None
        self.toggle.blockSignals(True)
        self.toggle.setChecked(False)
        self.toggle.blockSignals(False)
        self._update_status(self.STATUS_IDLE)

    def _on_connect_confirmed(self):
        if self.process and self._status == self.STATUS_CONNECTING:
            if self._is_port_open():
                self._timeout_timer.stop()
                self._update_status(self.STATUS_CONNECTED)
            else:
                self._connect_timer.start(1000)

    def _on_connect_timeout(self):
        if self._status == self.STATUS_CONNECTING:
            self.stop_tunnel()

    def _on_process_error(self, error):
        if not self._stopping:
            self._stopping = True
            QMessageBox.warning(self, LANG.OOPS, LANG.SSH_ERROR.format(self.name_label.text()))
        self._cleanup_process()

    def _on_process_finished(self, exit_code, exit_status):
        if not self._stopping:
            self._stopping = True
            QMessageBox.warning(self, LANG.OOPS, LANG.SSH_EXITED.format(self.name_label.text(), exit_code))
        self._cleanup_process()

    def _cleanup_process(self):
        self._connect_timer.stop()
        self._timeout_timer.stop()
        self.process = None
        self.toggle.blockSignals(True)
        self.toggle.setChecked(False)
        self.toggle.blockSignals(False)
        self._update_status(self.STATUS_IDLE)


class TunnelManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(LANG.TITLE)
        self.setWindowIcon(QIcon(ICONS.TUNNEL))
        self.setMinimumSize(750, 320)
        self.setObjectName("TunnelManager")
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowMinimizeButtonHint | Qt.WindowType.WindowCloseButtonHint)

        self._setup_tray()

        with open(CONF_FILE, "r") as fp:
            data = yaml.load(fp, Loader=yaml.FullLoader) or {}

        self.tunnels = []
        self._build_ui()

        for name in sorted(data.keys()):
            self._add_tunnel_widget(Tunnel(name, data[name]))

        self._update_status_label()
        self.show()

    def _setup_tray(self):
        self.tray = QSystemTrayIcon(QIcon(ICONS.TUNNEL), self)
        menu = QMenu()
        menu.addAction("Show", self._tray_show)
        menu.addSeparator()
        menu.addAction("Quit", self._tray_quit)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._tray_activated)
        self.tray.show()

    def _tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._tray_show()

    def _tray_show(self):
        self.showNormal()
        self.activateWindow()

    def _tray_quit(self):
        self.close()
        QApplication.quit()

    def changeEvent(self, event):
        from PySide6.QtCore import QEvent
        if event.type() == QEvent.Type.WindowStateChange:
            if self.isMinimized():
                event.ignore()
                self.hide()
                return
        super().changeEvent(event)

    def _build_ui(self):
        self.setStyleSheet("""
            #TunnelManager { background-color: #F2F2F7; }
            QScrollArea, QScrollArea > QWidget > QWidget { background: transparent; border: none; }
            QLineEdit {
                background: white;
                border: 1px solid #E5E5EA;
                border-radius: 10px;
                padding: 7px 12px;
                font-size: 13px;
                color: #1C1C1E;
            }
            QLineEdit:focus { border-color: #007AFF; }
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(10)

        self.status_label = QLabel()
        self.status_label.setStyleSheet("font-size:12px; color:#8E8E93; font-weight:500;")
        root.addWidget(self.status_label)

        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("🔍  Filter tunnels...")
        self.filter_input.textChanged.connect(self._apply_filter)
        root.addWidget(self.filter_input)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        self.scroll_content = QWidget()
        self.tunnel_list = QVBoxLayout(self.scroll_content)
        self.tunnel_list.setContentsMargins(0, 0, 0, 0)
        self.tunnel_list.setSpacing(8)
        self.tunnel_list.addStretch()

        self.scroll_area.setWidget(self.scroll_content)
        root.addWidget(self.scroll_area)

        footer = QHBoxLayout()
        footer.setContentsMargins(0, 4, 0, 0)

        self.add_button = QPushButton("+ Add Tunnel")
        self.add_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.add_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_button.clicked.connect(self.do_add_tunnel)
        self.add_button.setStyleSheet("""
            QPushButton { background:white; border:1px solid #E5E5EA; border-radius:8px;
                          padding:6px 14px; font-size:13px; color:#007AFF; font-weight:500; }
            QPushButton:hover { background:#F0F0F5; }
            QPushButton:pressed { background:#E5E5EA; }
        """)

        self.kill_button = QPushButton(" Kill All")
        self.kill_button.setIcon(QIcon(ICONS.KILL_SSH))
        self.kill_button.setIconSize(QSize(14, 14))
        self.kill_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.kill_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.kill_button.clicked.connect(self.do_killall_ssh)
        self.kill_button.setStyleSheet("""
            QPushButton { background:white; border:1px solid #E5E5EA; border-radius:8px;
                          padding:6px 14px; font-size:13px; color:#FF3B30; font-weight:500; }
            QPushButton:hover { background:#FFF0F0; border-color:#FF3B30; }
            QPushButton:pressed { background:#FFE5E5; }
            QPushButton:disabled { background:#F2F2F7; border-color:#E5E5EA; color:#C7C7CC; }
        """)

        footer.addWidget(self.kill_button)
        footer.addStretch()
        footer.addWidget(self.add_button)
        root.addLayout(footer)

    def _add_tunnel_widget(self, tunnel):
        self.tunnels.append(tunnel)
        self.tunnel_list.insertWidget(self.tunnel_list.count() - 1, tunnel)
        tunnel.settings_btn.clicked.connect(lambda checked=False, t=tunnel: self.show_tunnel_settings(t))
        tunnel.deleted.connect(lambda t=tunnel: self.do_delete_tunnel(t))
        tunnel.state_changed.connect(self._update_status_label)
        self._resize_scroll_area()

    def _resize_scroll_area(self):
        row_h = 76
        visible = min(len(self.tunnels), 5)
        h = visible * row_h + max(0, visible - 1) * 8
        self.scroll_area.setFixedHeight(max(h, 10))
        self.adjustSize()

    def _update_status_label(self):
        active = sum(1 for t in self.tunnels if t._status != Tunnel.STATUS_IDLE)
        total = len(self.tunnels)
        self.status_label.setText(f"{active} active · {total} total")
        self.kill_button.setEnabled(active > 0)

    def _apply_filter(self, text):
        for tunnel in self.tunnels:
            tunnel.setVisible(text.lower() in tunnel.name_label.text().lower())

    def _get_used_ports(self, exclude=None):
        return {t.data.get(KEYS.LOCAL_PORT) for t in self.tunnels if t is not exclude}

    def _get_used_names(self, exclude=None):
        return {t.tunnel_name for t in self.tunnels if t is not exclude}

    def show_tunnel_settings(self, tunnel):
        try:
            dialog = TunnelConfig(self, tunnel.tunnel_name, tunnel.data)
            dialog.used_ports = self._get_used_ports(exclude=tunnel)
            dialog.used_names = self._get_used_names(exclude=tunnel)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                tunnel.tunnel_name = dialog.get_name()
                tunnel.data = dialog.as_dict()
                tunnel.name_label.setText(tunnel.tunnel_name)
                tunnel._update_command_preview()
                self.save_config()
        except Exception as e:
            import traceback
            QMessageBox.critical(self, "Error", traceback.format_exc())

    def do_add_tunnel(self):
        dialog = AddTunnelDialog(self)
        dialog.used_ports = self._get_used_ports()
        dialog.used_names = self._get_used_names()
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        tunnel = Tunnel(dialog.get_name(), dialog.as_dict())
        self._add_tunnel_widget(tunnel)
        self._update_status_label()
        self.save_config()

    def do_delete_tunnel(self, tunnel):
        tunnel.stop_tunnel()
        self.tunnels.remove(tunnel)
        self.tunnel_list.removeWidget(tunnel)
        tunnel.deleteLater()
        self._update_status_label()
        self._resize_scroll_area()
        self.save_config()

    def do_killall_ssh(self):
        for tunnel in self.tunnels:
            tunnel.stop_tunnel()
        if os.name == 'nt':
            subprocess.Popen(CMDS.SSH_KILL_WIN.split(), creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            subprocess.Popen(CMDS.SSH_KILL_NIX.split())

    def save_config(self):
        data = {t.tunnel_name: t.data for t in self.tunnels}
        with open(CONF_FILE, "w") as fp:
            yaml.dump(data, fp)

    def closeEvent(self, event):
        for tunnel in self.tunnels:
            tunnel.stop_tunnel()
        event.accept()


def _kill_ssh_on_exit():
    if os.name == 'nt':
        subprocess.Popen(CMDS.SSH_KILL_WIN.split(), creationflags=subprocess.CREATE_NO_WINDOW)
    else:
        subprocess.Popen(CMDS.SSH_KILL_NIX.split())

if __name__ == '__main__':
    atexit.register(_kill_ssh_on_exit)
    app = QApplication(sys.argv)

    sm = QSharedMemory("3866273d-f4d5-4bf3-b27b-772ca7915a61")

    if not sm.create(1):
        mb = QMessageBox()
        mb.setIcon(QMessageBox.Icon.Information)
        mb.setText(LANG.ALREADY_RUNNING)
        mb.setWindowTitle(LANG.OOPS)
        mb.setStandardButtons(QMessageBox.StandardButton.Close)
        mb.show()
    else:
        if not os.path.exists(CONF_FILE):
            open(CONF_FILE, "w").close()
        tm = TunnelManager()

    sys.exit(app.exec())
