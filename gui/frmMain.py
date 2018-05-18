from gui.frmMain_uic import Ui_frmMainDLG
from PySide.QtGui import QMainWindow
from PySide.QtCore import SIGNAL
from PySide.QtCore import Qt
from gamedb.gamedb import GameDB
from gui.gamedlg import GameDlg
from gui.pcosdlg import PcOsDlg
from functools import partial

class frmMain(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_frmMainDLG()
        self.ui.setupUi(self)
        self.ui.searchbar.setFocus()
        # self.setFocus(self.searchbar)
        self.gamedb = GameDB('games.db')
        self.platform_win = False
        self.platform_linux = False
        self.platform_mac = False
        self.filter_tags = None
        self.game_title = None
        self.game = None
        self.ui.sort.addItem("title")
        self.ui.sort.addItem("priority")
        self.ui.sort.addItem("vote")
        self.ui.sort.setCurrentIndex(0)
        self.ui.btnPcplat.clicked.connect(self.callPcOs)
        for i in range(1, 31):
            btn = getattr(self.ui, 'b{:02d}'.format(i))
            btn.clicked.connect(partial(self.callGameViewer, i))
        self.ui.sort.currentIndexChanged.connect(lambda x: self.showResult())
        for check in ('ps4', 'ps3', 'ps_vita', 'steam', 'gog', 'uplay',
                      'ps_store', 'phisical'):
            btn = getattr(self.ui, check)
            btn.stateChanged.connect(lambda x: self.showResult())
        self.ui.pc.stateChanged.connect(self.slotPc)
        self.showResult()
        self.ui.showFranchises.setEnabled(False)
        
    def getBtn(self, value):
        return getattr(self.ui, 'b{:02d}'.format(value))
   
    def cleanBtns(self):
        for i in range(1,31):
            btn = self.getBtn(i)
            btn.setNull()
    
    def callPcOs(self):
        print('call pc os')
        self.pcos_dlg = PcOsDlg(self, self.platform_linux, 
                                self.platform_win, self.platform_mac)
        self.pcos_dlg.exec()
        self.platform_linux = self.pcos_dlg.ui.linux.isChecked()
        self.platform_win = self.pcos_dlg.ui.win.isChecked()
        self.platform_mac = self.pcos_dlg.ui.mac.isChecked()
        plats = (self.platform_linux, self.platform_win, self.platform_mac)
        if any(plats) and not all(plats):
            self.ui.pc.setCheckState(Qt.PartiallyChecked)
            # the following line will force refresh in PartiallyChecked state
            # this means that, if previous checkstate was Checked or Unchecked
            # than the result is refreshed twice
            self.showResult()
        elif all(plats):
            self.ui.pc.setCheckState(Qt.Checked)
        else:
            self.ui.pc.setCheckState(Qt.Unchecked)
    
    def callGameViewer(self, num):
        btn = self.getBtn(num)
        vg = self.gamedb.gameview(btn.xid, view='icon')
        self.gamedlg = GameDlg(vg)
        self.gamedlg.show()
    
    def slotPc(self, checkstate):
        if checkstate == Qt.Unchecked:
            self.platform_win = False
            self.platform_linux = False
            self.platform_mac = False
        elif checkstate == Qt.Checked:
            self.platform_win = True
            self.platform_linux = True
            self.platform_mac = True
        # if, instead, self.ui.pc is partially checked, no changes 
        self.showResult()
    
    def showResult(self):
        if self.ui.showFranchises.isChecked():
            # todo
            return None
        # most common case: Show Games
        stores = [
            store_name for store_name, store in 
            (
                ('steam', self.ui.steam), ('gog', self.ui.gog),
                ('uplay', self.ui.uplay), ('psn', self.ui.ps_store)
            )  if store.isChecked()
        ]
        if self.ui.phisical.isChecked():
            stores.extend(['cd', 'hd'])
        platforms = [
            platname for platname, platform in
            (
                ('ps4', self.ui.ps4), ('ps3', self.ui.ps3),
                ('psvita', self.ui.ps_vita)
            )  if platform.isChecked()
        ]
        platforms.extend(
            [ 
                platname for platname, platform in
                (
                    ('win', self.platform_win), ('mac', self.platform_mac),
                    ('linux', self.platform_linux),
                )  if platform
            ]
        )
        franchise = self.ui.franchise.text()
        if stores == []:
            stores = None
        if platforms == []:
            platforms = None
        if len(franchise.strip()) == 0:
            franchise = None
        results = self.gamedb.filter_games(
            title = self.game_title,
            tags = self.filter_tags,
            platforms = platforms,
            stores = stores,
            franchise = franchise,
            sortby = self.ui.sort.currentText(),
            page = int(self.ui.page.text())
        )
        # results = self.gamedb.filter_games()
        self.cleanBtns()
        for index, result in enumerate(results):
            try:
                btn = self.getBtn(index +1)
            except ValueError:
                break
            btn.setGame(self.gamedb, *result)