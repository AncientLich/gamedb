# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pcos.ui'
#
# Created: Fri May 18 17:13:31 2018
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_PcOsDLG(object):
    def setupUi(self, PcOsDLG):
        PcOsDLG.setObjectName("PcOsDLG")
        PcOsDLG.resize(196, 131)
        self.verticalLayout = QtGui.QVBoxLayout(PcOsDLG)
        self.verticalLayout.setObjectName("verticalLayout")
        self.linux = QtGui.QCheckBox(PcOsDLG)
        self.linux.setObjectName("linux")
        self.verticalLayout.addWidget(self.linux)
        self.win = QtGui.QCheckBox(PcOsDLG)
        self.win.setObjectName("win")
        self.verticalLayout.addWidget(self.win)
        self.mac = QtGui.QCheckBox(PcOsDLG)
        self.mac.setObjectName("mac")
        self.verticalLayout.addWidget(self.mac)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.ok = QtGui.QPushButton(PcOsDLG)
        self.ok.setObjectName("ok")
        self.horizontalLayout.addWidget(self.ok)
        self.canc = QtGui.QPushButton(PcOsDLG)
        self.canc.setObjectName("canc")
        self.horizontalLayout.addWidget(self.canc)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(PcOsDLG)
        QtCore.QMetaObject.connectSlotsByName(PcOsDLG)

    def retranslateUi(self, PcOsDLG):
        PcOsDLG.setWindowTitle(QtGui.QApplication.translate("PcOsDLG", "PC Os", None, QtGui.QApplication.UnicodeUTF8))
        self.linux.setText(QtGui.QApplication.translate("PcOsDLG", "Linux", None, QtGui.QApplication.UnicodeUTF8))
        self.win.setText(QtGui.QApplication.translate("PcOsDLG", "Windows", None, QtGui.QApplication.UnicodeUTF8))
        self.mac.setText(QtGui.QApplication.translate("PcOsDLG", "Mac", None, QtGui.QApplication.UnicodeUTF8))
        self.ok.setText(QtGui.QApplication.translate("PcOsDLG", "&OK", None, QtGui.QApplication.UnicodeUTF8))
        self.canc.setText(QtGui.QApplication.translate("PcOsDLG", "&Cancel", None, QtGui.QApplication.UnicodeUTF8))

