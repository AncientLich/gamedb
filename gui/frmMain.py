from gui.frmMain_uic import Ui_frmMainDLG
from PySide.QtGui import QMainWindow
from PySide.QtCore import SIGNAL
from gamedb.gamedb import GameDB
from gui.gamedlg import GameDlg
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
        for i in range(1, 31):
            btn = getattr(self.ui, 'b{:02d}'.format(i))
            btn.clicked.connect(partial(self.callGameViewer, i))
        self.ui.sort.currentIndexChanged.connect(lambda x: self.showResult())
        self.showResult()
        
    def getBtn(self, value):
        return getattr(self.ui, 'b{:02d}'.format(value))
   
    def cleanBtns(self):
        for i in range(1,31):
            btn = self.getBtn(i)
            btn.setNull()
    
    def callGameViewer(self, num):
        btn = self.getBtn(num)
        vg = self.gamedb.gameview(btn.xid, view='icon')
        self.gamedlg = GameDlg(vg)
        self.gamedlg.show()
    
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