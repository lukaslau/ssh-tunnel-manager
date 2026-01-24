# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'tunnelconfig.ui'
##
## Created by: Qt User Interface Compiler version 6.8.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QGridLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QSpacerItem, QSpinBox,
    QWidget)

class Ui_TunnelConfig(object):
    def setupUi(self, TunnelConfig):
        if not TunnelConfig.objectName():
            TunnelConfig.setObjectName(u"TunnelConfig")
        TunnelConfig.resize(508, 238)
        self.gridLayout = QGridLayout(TunnelConfig)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_remote_address = QLabel(TunnelConfig)
        self.label_remote_address.setObjectName(u"label_remote_address")

        self.gridLayout.addWidget(self.label_remote_address, 1, 0, 1, 1)

        self.label_browser_open = QLabel(TunnelConfig)
        self.label_browser_open.setObjectName(u"label_browser_open")

        self.gridLayout.addWidget(self.label_browser_open, 3, 0, 1, 1)

        self.label_local_port = QLabel(TunnelConfig)
        self.label_local_port.setObjectName(u"label_local_port")

        self.gridLayout.addWidget(self.label_local_port, 0, 0, 1, 1)

        self.ssh_command = QLineEdit(TunnelConfig)
        self.ssh_command.setObjectName(u"ssh_command")
        font = QFont()
        font.setFamilies([u"Monospace"])
        self.ssh_command.setFont(font)
        self.ssh_command.setReadOnly(True)

        self.gridLayout.addWidget(self.ssh_command, 4, 1, 1, 1)

        self.label_ssh_command = QLabel(TunnelConfig)
        self.label_ssh_command.setObjectName(u"label_ssh_command")

        self.gridLayout.addWidget(self.label_ssh_command, 4, 0, 1, 1)

        self.label_proxy_host = QLabel(TunnelConfig)
        self.label_proxy_host.setObjectName(u"label_proxy_host")

        self.gridLayout.addWidget(self.label_proxy_host, 2, 0, 1, 1)

        self.copy = QPushButton(TunnelConfig)
        self.copy.setObjectName(u"copy")

        self.gridLayout.addWidget(self.copy, 4, 2, 1, 1)

        self.browser_open = QLineEdit(TunnelConfig)
        self.browser_open.setObjectName(u"browser_open")
        self.browser_open.setFont(font)

        self.gridLayout.addWidget(self.browser_open, 3, 1, 1, 2)

        self.proxy_host = QLineEdit(TunnelConfig)
        self.proxy_host.setObjectName(u"proxy_host")
        self.proxy_host.setFont(font)

        self.gridLayout.addWidget(self.proxy_host, 2, 1, 1, 2)

        self.remote_address = QLineEdit(TunnelConfig)
        self.remote_address.setObjectName(u"remote_address")
        self.remote_address.setFont(font)
        self.remote_address.setStyleSheet(u"")

        self.gridLayout.addWidget(self.remote_address, 1, 1, 1, 2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(188, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.buttonBox = QDialogButtonBox(TunnelConfig)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Save)

        self.horizontalLayout.addWidget(self.buttonBox)


        self.gridLayout.addLayout(self.horizontalLayout, 5, 0, 1, 3)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.local_port = QSpinBox(TunnelConfig)
        self.local_port.setObjectName(u"local_port")
        self.local_port.setFont(font)
        self.local_port.setMaximum(65365)
        self.local_port.setSingleStep(1000)
        self.local_port.setValue(8443)

        self.horizontalLayout_2.addWidget(self.local_port)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)


        self.gridLayout.addLayout(self.horizontalLayout_2, 0, 1, 1, 2)

        QWidget.setTabOrder(self.local_port, self.remote_address)
        QWidget.setTabOrder(self.remote_address, self.proxy_host)
        QWidget.setTabOrder(self.proxy_host, self.browser_open)
        QWidget.setTabOrder(self.browser_open, self.ssh_command)
        QWidget.setTabOrder(self.ssh_command, self.copy)

        self.retranslateUi(TunnelConfig)
        self.buttonBox.accepted.connect(TunnelConfig.accept)
        self.buttonBox.rejected.connect(TunnelConfig.reject)

        QMetaObject.connectSlotsByName(TunnelConfig)
    # setupUi

    def retranslateUi(self, TunnelConfig):
        TunnelConfig.setWindowTitle(QCoreApplication.translate("TunnelConfig", u"Dialog", None))
        self.label_remote_address.setText(QCoreApplication.translate("TunnelConfig", u"Remote Address", None))
        self.label_browser_open.setText(QCoreApplication.translate("TunnelConfig", u"Address to Open", None))
        self.label_local_port.setText(QCoreApplication.translate("TunnelConfig", u"Local Port", None))
        self.label_ssh_command.setText(QCoreApplication.translate("TunnelConfig", u"SSH Command", None))
        self.label_proxy_host.setText(QCoreApplication.translate("TunnelConfig", u"Proxy Host", None))
        self.copy.setText(QCoreApplication.translate("TunnelConfig", u"Copy", None))
        self.browser_open.setPlaceholderText(QCoreApplication.translate("TunnelConfig", u"https://127.0.0.1:8443", None))
        self.proxy_host.setPlaceholderText(QCoreApplication.translate("TunnelConfig", u"proxy-host", None))
        self.remote_address.setPlaceholderText(QCoreApplication.translate("TunnelConfig", u"10.10.10.10:443", None))
    # retranslateUi

