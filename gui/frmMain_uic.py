# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'frmMain.ui'
#
# Created: Thu May 17 19:13:12 2018
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_frmMainDLG(object):
    def setupUi(self, frmMainDLG):
        frmMainDLG.setObjectName("frmMainDLG")
        frmMainDLG.resize(1235, 597)
        self.centralwidget = QtGui.QWidget(frmMainDLG)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout_4 = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.labsort = QtGui.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.labsort.setFont(font)
        self.labsort.setObjectName("labsort")
        self.verticalLayout_3.addWidget(self.labsort)
        self.sort = QtGui.QComboBox(self.centralwidget)
        self.sort.setObjectName("sort")
        self.verticalLayout_3.addWidget(self.sort)
        self.box_hardware = QtGui.QGroupBox(self.centralwidget)
        self.box_hardware.setObjectName("box_hardware")
        self.verticalLayout = QtGui.QVBoxLayout(self.box_hardware)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setSpacing(2)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.pc = QtGui.QCheckBox(self.box_hardware)
        self.pc.setChecked(False)
        self.pc.setObjectName("pc")
        self.horizontalLayout_2.addWidget(self.pc)
        self.btnPcplat = QtGui.QPushButton(self.box_hardware)
        self.btnPcplat.setMaximumSize(QtCore.QSize(30, 30))
        self.btnPcplat.setObjectName("btnPcplat")
        self.horizontalLayout_2.addWidget(self.btnPcplat)
        self.horizontalLayout_2.setStretch(0, 10)
        self.horizontalLayout_2.setStretch(1, 1)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.ps4 = QtGui.QCheckBox(self.box_hardware)
        self.ps4.setChecked(False)
        self.ps4.setObjectName("ps4")
        self.verticalLayout.addWidget(self.ps4)
        self.ps3 = QtGui.QCheckBox(self.box_hardware)
        self.ps3.setChecked(False)
        self.ps3.setObjectName("ps3")
        self.verticalLayout.addWidget(self.ps3)
        self.ps_vita = QtGui.QCheckBox(self.box_hardware)
        self.ps_vita.setChecked(False)
        self.ps_vita.setObjectName("ps_vita")
        self.verticalLayout.addWidget(self.ps_vita)
        self.verticalLayout_3.addWidget(self.box_hardware)
        self.box_store = QtGui.QGroupBox(self.centralwidget)
        self.box_store.setObjectName("box_store")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.box_store)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.steam = QtGui.QCheckBox(self.box_store)
        self.steam.setChecked(False)
        self.steam.setObjectName("steam")
        self.verticalLayout_2.addWidget(self.steam)
        self.gog = QtGui.QCheckBox(self.box_store)
        self.gog.setChecked(False)
        self.gog.setObjectName("gog")
        self.verticalLayout_2.addWidget(self.gog)
        self.uplay = QtGui.QCheckBox(self.box_store)
        self.uplay.setChecked(False)
        self.uplay.setObjectName("uplay")
        self.verticalLayout_2.addWidget(self.uplay)
        self.ps_store = QtGui.QCheckBox(self.box_store)
        self.ps_store.setChecked(False)
        self.ps_store.setObjectName("ps_store")
        self.verticalLayout_2.addWidget(self.ps_store)
        self.phisical = QtGui.QCheckBox(self.box_store)
        self.phisical.setChecked(False)
        self.phisical.setObjectName("phisical")
        self.verticalLayout_2.addWidget(self.phisical)
        self.verticalLayout_3.addWidget(self.box_store)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem)
        self.box_display = QtGui.QGroupBox(self.centralwidget)
        self.box_display.setObjectName("box_display")
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.box_display)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.showGames = QtGui.QRadioButton(self.box_display)
        self.showGames.setChecked(True)
        self.showGames.setObjectName("showGames")
        self.verticalLayout_5.addWidget(self.showGames)
        self.showFranchises = QtGui.QRadioButton(self.box_display)
        self.showFranchises.setObjectName("showFranchises")
        self.verticalLayout_5.addWidget(self.showFranchises)
        self.franchise = QtGui.QLineEdit(self.box_display)
        self.franchise.setEnabled(False)
        self.franchise.setObjectName("franchise")
        self.verticalLayout_5.addWidget(self.franchise)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_5.addItem(spacerItem1)
        self.verticalLayout_5.setStretch(0, 4)
        self.verticalLayout_5.setStretch(1, 5)
        self.verticalLayout_5.setStretch(2, 2)
        self.verticalLayout_5.setStretch(3, 3)
        self.verticalLayout_3.addWidget(self.box_display)
        self.verticalLayout_3.setStretch(2, 3)
        self.verticalLayout_3.setStretch(3, 4)
        self.verticalLayout_3.setStretch(4, 1)
        self.verticalLayout_3.setStretch(5, 3)
        self.horizontalLayout_4.addLayout(self.verticalLayout_3)
        self.verticalLayout_4 = QtGui.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.brnSearch = QtGui.QPushButton(self.centralwidget)
        self.brnSearch.setObjectName("brnSearch")
        self.horizontalLayout_3.addWidget(self.brnSearch)
        self.searchbar = QtGui.QLineEdit(self.centralwidget)
        self.searchbar.setMaximumSize(QtCore.QSize(16777215, 30))
        self.searchbar.setObjectName("searchbar")
        self.horizontalLayout_3.addWidget(self.searchbar)
        self.verticalLayout_4.addLayout(self.horizontalLayout_3)
        self.scrollArea = QtGui.QScrollArea(self.centralwidget)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.gameArea = QtGui.QWidget()
        self.gameArea.setGeometry(QtCore.QRect(0, 0, 1068, 1068))
        self.gameArea.setObjectName("gameArea")
        self.gridLayout = QtGui.QGridLayout(self.gameArea)
        self.gridLayout.setObjectName("gridLayout")
        self.b28 = GButton(self.gameArea)
        self.b28.setMinimumSize(QtCore.QSize(0, 170))
        self.b28.setObjectName("b28")
        self.gridLayout.addWidget(self.b28, 5, 2, 1, 1)
        self.b02 = GButton(self.gameArea)
        self.b02.setMinimumSize(QtCore.QSize(0, 170))
        self.b02.setObjectName("b02")
        self.gridLayout.addWidget(self.b02, 0, 1, 1, 1)
        self.b03 = GButton(self.gameArea)
        self.b03.setMinimumSize(QtCore.QSize(0, 170))
        self.b03.setObjectName("b03")
        self.gridLayout.addWidget(self.b03, 0, 2, 1, 1)
        self.b04 = GButton(self.gameArea)
        self.b04.setMinimumSize(QtCore.QSize(0, 170))
        self.b04.setObjectName("b04")
        self.gridLayout.addWidget(self.b04, 0, 3, 1, 1)
        self.b05 = GButton(self.gameArea)
        self.b05.setMinimumSize(QtCore.QSize(0, 170))
        self.b05.setObjectName("b05")
        self.gridLayout.addWidget(self.b05, 0, 4, 1, 1)
        self.b06 = GButton(self.gameArea)
        self.b06.setMinimumSize(QtCore.QSize(0, 170))
        self.b06.setObjectName("b06")
        self.gridLayout.addWidget(self.b06, 1, 0, 1, 1)
        self.b07 = GButton(self.gameArea)
        self.b07.setMinimumSize(QtCore.QSize(0, 170))
        self.b07.setObjectName("b07")
        self.gridLayout.addWidget(self.b07, 1, 1, 1, 1)
        self.b08 = GButton(self.gameArea)
        self.b08.setMinimumSize(QtCore.QSize(0, 170))
        self.b08.setObjectName("b08")
        self.gridLayout.addWidget(self.b08, 1, 2, 1, 1)
        self.b09 = GButton(self.gameArea)
        self.b09.setMinimumSize(QtCore.QSize(0, 170))
        self.b09.setObjectName("b09")
        self.gridLayout.addWidget(self.b09, 1, 3, 1, 1)
        self.b10 = GButton(self.gameArea)
        self.b10.setMinimumSize(QtCore.QSize(0, 170))
        self.b10.setObjectName("b10")
        self.gridLayout.addWidget(self.b10, 1, 4, 1, 1)
        self.b11 = GButton(self.gameArea)
        self.b11.setMinimumSize(QtCore.QSize(0, 170))
        self.b11.setObjectName("b11")
        self.gridLayout.addWidget(self.b11, 2, 0, 1, 1)
        self.b12 = GButton(self.gameArea)
        self.b12.setMinimumSize(QtCore.QSize(0, 170))
        self.b12.setObjectName("b12")
        self.gridLayout.addWidget(self.b12, 2, 1, 1, 1)
        self.b13 = GButton(self.gameArea)
        self.b13.setMinimumSize(QtCore.QSize(0, 170))
        self.b13.setObjectName("b13")
        self.gridLayout.addWidget(self.b13, 2, 2, 1, 1)
        self.b14 = GButton(self.gameArea)
        self.b14.setMinimumSize(QtCore.QSize(0, 170))
        self.b14.setObjectName("b14")
        self.gridLayout.addWidget(self.b14, 2, 3, 1, 1)
        self.b15 = GButton(self.gameArea)
        self.b15.setMinimumSize(QtCore.QSize(0, 170))
        self.b15.setObjectName("b15")
        self.gridLayout.addWidget(self.b15, 2, 4, 1, 1)
        self.b16 = GButton(self.gameArea)
        self.b16.setMinimumSize(QtCore.QSize(0, 170))
        self.b16.setObjectName("b16")
        self.gridLayout.addWidget(self.b16, 3, 0, 1, 1)
        self.b17 = GButton(self.gameArea)
        self.b17.setMinimumSize(QtCore.QSize(0, 170))
        self.b17.setObjectName("b17")
        self.gridLayout.addWidget(self.b17, 3, 1, 1, 1)
        self.b18 = GButton(self.gameArea)
        self.b18.setMinimumSize(QtCore.QSize(0, 170))
        self.b18.setObjectName("b18")
        self.gridLayout.addWidget(self.b18, 3, 2, 1, 1)
        self.b19 = GButton(self.gameArea)
        self.b19.setMinimumSize(QtCore.QSize(0, 170))
        self.b19.setObjectName("b19")
        self.gridLayout.addWidget(self.b19, 3, 3, 1, 1)
        self.b20 = GButton(self.gameArea)
        self.b20.setMinimumSize(QtCore.QSize(0, 170))
        self.b20.setObjectName("b20")
        self.gridLayout.addWidget(self.b20, 3, 4, 1, 1)
        self.b21 = GButton(self.gameArea)
        self.b21.setMinimumSize(QtCore.QSize(0, 170))
        self.b21.setObjectName("b21")
        self.gridLayout.addWidget(self.b21, 4, 0, 1, 1)
        self.b22 = GButton(self.gameArea)
        self.b22.setMinimumSize(QtCore.QSize(0, 170))
        self.b22.setObjectName("b22")
        self.gridLayout.addWidget(self.b22, 4, 1, 1, 1)
        self.b23 = GButton(self.gameArea)
        self.b23.setMinimumSize(QtCore.QSize(0, 170))
        self.b23.setObjectName("b23")
        self.gridLayout.addWidget(self.b23, 4, 2, 1, 1)
        self.b24 = GButton(self.gameArea)
        self.b24.setMinimumSize(QtCore.QSize(0, 170))
        self.b24.setObjectName("b24")
        self.gridLayout.addWidget(self.b24, 4, 3, 1, 1)
        self.b25 = GButton(self.gameArea)
        self.b25.setMinimumSize(QtCore.QSize(0, 170))
        self.b25.setObjectName("b25")
        self.gridLayout.addWidget(self.b25, 4, 4, 1, 1)
        self.b27 = GButton(self.gameArea)
        self.b27.setMinimumSize(QtCore.QSize(0, 170))
        self.b27.setObjectName("b27")
        self.gridLayout.addWidget(self.b27, 5, 1, 1, 1)
        self.b01 = GButton(self.gameArea)
        self.b01.setMinimumSize(QtCore.QSize(0, 170))
        self.b01.setObjectName("b01")
        self.gridLayout.addWidget(self.b01, 0, 0, 1, 1)
        self.b26 = GButton(self.gameArea)
        self.b26.setMinimumSize(QtCore.QSize(0, 170))
        self.b26.setObjectName("b26")
        self.gridLayout.addWidget(self.b26, 5, 0, 1, 1)
        self.b29 = GButton(self.gameArea)
        self.b29.setMinimumSize(QtCore.QSize(0, 170))
        self.b29.setObjectName("b29")
        self.gridLayout.addWidget(self.b29, 5, 3, 1, 1)
        self.b30 = GButton(self.gameArea)
        self.b30.setMinimumSize(QtCore.QSize(0, 170))
        self.b30.setObjectName("b30")
        self.gridLayout.addWidget(self.b30, 5, 4, 1, 1)
        self.scrollArea.setWidget(self.gameArea)
        self.verticalLayout_4.addWidget(self.scrollArea)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.btnPrev = QtGui.QPushButton(self.centralwidget)
        self.btnPrev.setMaximumSize(QtCore.QSize(40, 16777215))
        self.btnPrev.setObjectName("btnPrev")
        self.horizontalLayout.addWidget(self.btnPrev)
        self.page = QtGui.QLineEdit(self.centralwidget)
        self.page.setMaximumSize(QtCore.QSize(50, 30))
        self.page.setObjectName("page")
        self.horizontalLayout.addWidget(self.page)
        self.totalPages = QtGui.QLabel(self.centralwidget)
        self.totalPages.setObjectName("totalPages")
        self.horizontalLayout.addWidget(self.totalPages)
        self.btnNext = QtGui.QPushButton(self.centralwidget)
        self.btnNext.setMaximumSize(QtCore.QSize(40, 16777215))
        self.btnNext.setObjectName("btnNext")
        self.horizontalLayout.addWidget(self.btnNext)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 1)
        self.horizontalLayout.setStretch(2, 1)
        self.horizontalLayout.setStretch(3, 1)
        self.horizontalLayout.setStretch(4, 20)
        self.verticalLayout_4.addLayout(self.horizontalLayout)
        self.horizontalLayout_4.addLayout(self.verticalLayout_4)
        self.horizontalLayout_4.setStretch(0, 1)
        self.horizontalLayout_4.setStretch(1, 9)
        frmMainDLG.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(frmMainDLG)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1235, 25))
        self.menubar.setObjectName("menubar")
        frmMainDLG.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(frmMainDLG)
        self.statusbar.setObjectName("statusbar")
        frmMainDLG.setStatusBar(self.statusbar)

        self.retranslateUi(frmMainDLG)
        self.sort.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(frmMainDLG)

    def retranslateUi(self, frmMainDLG):
        frmMainDLG.setWindowTitle(QtGui.QApplication.translate("frmMainDLG", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.labsort.setText(QtGui.QApplication.translate("frmMainDLG", "Sort by...", None, QtGui.QApplication.UnicodeUTF8))
        self.box_hardware.setTitle(QtGui.QApplication.translate("frmMainDLG", "Hardware", None, QtGui.QApplication.UnicodeUTF8))
        self.pc.setText(QtGui.QApplication.translate("frmMainDLG", "PC", None, QtGui.QApplication.UnicodeUTF8))
        self.btnPcplat.setText(QtGui.QApplication.translate("frmMainDLG", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.ps4.setText(QtGui.QApplication.translate("frmMainDLG", "PS4", None, QtGui.QApplication.UnicodeUTF8))
        self.ps3.setText(QtGui.QApplication.translate("frmMainDLG", "PS3", None, QtGui.QApplication.UnicodeUTF8))
        self.ps_vita.setText(QtGui.QApplication.translate("frmMainDLG", "PS vita", None, QtGui.QApplication.UnicodeUTF8))
        self.box_store.setTitle(QtGui.QApplication.translate("frmMainDLG", "Store", None, QtGui.QApplication.UnicodeUTF8))
        self.steam.setText(QtGui.QApplication.translate("frmMainDLG", "Steam", None, QtGui.QApplication.UnicodeUTF8))
        self.gog.setText(QtGui.QApplication.translate("frmMainDLG", "GOG", None, QtGui.QApplication.UnicodeUTF8))
        self.uplay.setText(QtGui.QApplication.translate("frmMainDLG", "Uplay", None, QtGui.QApplication.UnicodeUTF8))
        self.ps_store.setText(QtGui.QApplication.translate("frmMainDLG", "PS store", None, QtGui.QApplication.UnicodeUTF8))
        self.phisical.setText(QtGui.QApplication.translate("frmMainDLG", "<phisical>", None, QtGui.QApplication.UnicodeUTF8))
        self.box_display.setTitle(QtGui.QApplication.translate("frmMainDLG", "Show by...", None, QtGui.QApplication.UnicodeUTF8))
        self.showGames.setText(QtGui.QApplication.translate("frmMainDLG", "Game", None, QtGui.QApplication.UnicodeUTF8))
        self.showFranchises.setText(QtGui.QApplication.translate("frmMainDLG", "Franchise", None, QtGui.QApplication.UnicodeUTF8))
        self.brnSearch.setText(QtGui.QApplication.translate("frmMainDLG", "Search...", None, QtGui.QApplication.UnicodeUTF8))
        self.b28.setText(QtGui.QApplication.translate("frmMainDLG", "PushButton", None, QtGui.QApplication.UnicodeUTF8))
        self.b02.setText(QtGui.QApplication.translate("frmMainDLG", "PushButton", None, QtGui.QApplication.UnicodeUTF8))
        self.b03.setText(QtGui.QApplication.translate("frmMainDLG", "PushButton", None, QtGui.QApplication.UnicodeUTF8))
        self.b04.setText(QtGui.QApplication.translate("frmMainDLG", "PushButton", None, QtGui.QApplication.UnicodeUTF8))
        self.b05.setText(QtGui.QApplication.translate("frmMainDLG", "PushButton", None, QtGui.QApplication.UnicodeUTF8))
        self.b06.setText(QtGui.QApplication.translate("frmMainDLG", "PushButton", None, QtGui.QApplication.UnicodeUTF8))
        self.b07.setText(QtGui.QApplication.translate("frmMainDLG", "PushButton", None, QtGui.QApplication.UnicodeUTF8))
        self.b08.setText(QtGui.QApplication.translate("frmMainDLG", "PushButton", None, QtGui.QApplication.UnicodeUTF8))
        self.b09.setText(QtGui.QApplication.translate("frmMainDLG", "PushButton", None, QtGui.QApplication.UnicodeUTF8))
        self.b10.setText(QtGui.QApplication.translate("frmMainDLG", "PushButton", None, QtGui.QApplication.UnicodeUTF8))
        self.b11.setText(QtGui.QApplication.translate("frmMainDLG", "PushButton", None, QtGui.QApplication.UnicodeUTF8))
        self.b12.setText(QtGui.QApplication.translate("frmMainDLG", "PushButton", None, QtGui.QApplication.UnicodeUTF8))
        self.b13.setText(QtGui.QApplication.translate("frmMainDLG", "PushButton", None, QtGui.QApplication.UnicodeUTF8))
        self.b14.setText(QtGui.QApplication.translate("frmMainDLG", "PushButton", None, QtGui.QApplication.UnicodeUTF8))
        self.b15.setText(QtGui.QApplication.translate("frmMainDLG", "PushButton", None, QtGui.QApplication.UnicodeUTF8))
        self.b16.setText(QtGui.QApplication.translate("frmMainDLG", "PushButton", None, QtGui.QApplication.UnicodeUTF8))
        self.b17.setText(QtGui.QApplication.translate("frmMainDLG", "PushButton", None, QtGui.QApplication.UnicodeUTF8))
        self.b18.setText(QtGui.QApplication.translate("frmMainDLG", "PushButton", None, QtGui.QApplication.UnicodeUTF8))
        self.b19.setText(QtGui.QApplication.translate("frmMainDLG", "PushButton", None, QtGui.QApplication.UnicodeUTF8))
        self.b20.setText(QtGui.QApplication.translate("frmMainDLG", "PushButton", None, QtGui.QApplication.UnicodeUTF8))
        self.b21.setText(QtGui.QApplication.translate("frmMainDLG", "PushButton", None, QtGui.QApplication.UnicodeUTF8))
        self.b22.setText(QtGui.QApplication.translate("frmMainDLG", "PushButton", None, QtGui.QApplication.UnicodeUTF8))
        self.b23.setText(QtGui.QApplication.translate("frmMainDLG", "PushButton", None, QtGui.QApplication.UnicodeUTF8))
        self.b24.setText(QtGui.QApplication.translate("frmMainDLG", "PushButton", None, QtGui.QApplication.UnicodeUTF8))
        self.b25.setText(QtGui.QApplication.translate("frmMainDLG", "PushButton", None, QtGui.QApplication.UnicodeUTF8))
        self.b27.setText(QtGui.QApplication.translate("frmMainDLG", "PushButton", None, QtGui.QApplication.UnicodeUTF8))
        self.b01.setText(QtGui.QApplication.translate("frmMainDLG", "PushButton", None, QtGui.QApplication.UnicodeUTF8))
        self.b26.setText(QtGui.QApplication.translate("frmMainDLG", "PushButton", None, QtGui.QApplication.UnicodeUTF8))
        self.b29.setText(QtGui.QApplication.translate("frmMainDLG", "PushButton", None, QtGui.QApplication.UnicodeUTF8))
        self.b30.setText(QtGui.QApplication.translate("frmMainDLG", "PushButton", None, QtGui.QApplication.UnicodeUTF8))
        self.btnPrev.setText(QtGui.QApplication.translate("frmMainDLG", "<", None, QtGui.QApplication.UnicodeUTF8))
        self.page.setText(QtGui.QApplication.translate("frmMainDLG", "1", None, QtGui.QApplication.UnicodeUTF8))
        self.totalPages.setText(QtGui.QApplication.translate("frmMainDLG", "/ 999", None, QtGui.QApplication.UnicodeUTF8))
        self.btnNext.setText(QtGui.QApplication.translate("frmMainDLG", ">", None, QtGui.QApplication.UnicodeUTF8))

from gui.gbutton import GButton
