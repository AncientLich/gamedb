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
        # the following part of code was generated with generators/gen.py:
        # self.connect(self.ui.b01, SIGNAL('clicked()'), self.slot01)
        for i in range(1, 31):
            btn = getattr(self.ui, 'b{:02d}'.format(i))
            self.connect(btn, SIGNAL('clicked()'), 
                         partial(self.callGameViewer, i)
            )
        '''
        self.connect(self.ui.b01, SIGNAL('clicked()'), self.slot01)
        self.connect(self.ui.b02, SIGNAL('clicked()'), self.slot02)
        self.connect(self.ui.b03, SIGNAL('clicked()'), self.slot03)
        self.connect(self.ui.b04, SIGNAL('clicked()'), self.slot04)
        self.connect(self.ui.b05, SIGNAL('clicked()'), self.slot05)
        self.connect(self.ui.b06, SIGNAL('clicked()'), self.slot06)
        self.connect(self.ui.b07, SIGNAL('clicked()'), self.slot07)
        self.connect(self.ui.b08, SIGNAL('clicked()'), self.slot08)
        self.connect(self.ui.b09, SIGNAL('clicked()'), self.slot09)
        self.connect(self.ui.b10, SIGNAL('clicked()'), self.slot10)
        self.connect(self.ui.b11, SIGNAL('clicked()'), self.slot11)
        self.connect(self.ui.b12, SIGNAL('clicked()'), self.slot12)
        self.connect(self.ui.b13, SIGNAL('clicked()'), self.slot13)
        self.connect(self.ui.b14, SIGNAL('clicked()'), self.slot14)
        self.connect(self.ui.b15, SIGNAL('clicked()'), self.slot15)
        self.connect(self.ui.b16, SIGNAL('clicked()'), self.slot16)
        self.connect(self.ui.b17, SIGNAL('clicked()'), self.slot17)
        self.connect(self.ui.b18, SIGNAL('clicked()'), self.slot18)
        self.connect(self.ui.b19, SIGNAL('clicked()'), self.slot19)
        self.connect(self.ui.b20, SIGNAL('clicked()'), self.slot20)
        self.connect(self.ui.b21, SIGNAL('clicked()'), self.slot21)
        self.connect(self.ui.b22, SIGNAL('clicked()'), self.slot22)
        self.connect(self.ui.b23, SIGNAL('clicked()'), self.slot23)
        self.connect(self.ui.b24, SIGNAL('clicked()'), self.slot24)
        self.connect(self.ui.b25, SIGNAL('clicked()'), self.slot25)
        self.connect(self.ui.b26, SIGNAL('clicked()'), self.slot26)
        self.connect(self.ui.b27, SIGNAL('clicked()'), self.slot27)
        self.connect(self.ui.b28, SIGNAL('clicked()'), self.slot28)
        self.connect(self.ui.b29, SIGNAL('clicked()'), self.slot29)
        self.connect(self.ui.b30, SIGNAL('clicked()'), self.slot30)
        '''
        # end of generated code
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
    
    # the following functions were generated with generators/gen.py
    def slot01(self):
        self.callGameViewer(1)

    def slot02(self):
        self.callGameViewer(2)

    def slot03(self):
        self.callGameViewer(3)

    def slot04(self):
        self.callGameViewer(4)

    def slot05(self):
        self.callGameViewer(5)

    def slot06(self):
        self.callGameViewer(6)

    def slot07(self):
        self.callGameViewer(7)

    def slot08(self):
        self.callGameViewer(8)

    def slot09(self):
        self.callGameViewer(9)

    def slot10(self):
        self.callGameViewer(10)

    def slot11(self):
        self.callGameViewer(11)

    def slot12(self):
        self.callGameViewer(12)

    def slot13(self):
        self.callGameViewer(13)

    def slot14(self):
        self.callGameViewer(14)

    def slot15(self):
        self.callGameViewer(15)

    def slot16(self):
        self.callGameViewer(16)

    def slot17(self):
        self.callGameViewer(17)

    def slot18(self):
        self.callGameViewer(18)

    def slot19(self):
        self.callGameViewer(19)

    def slot20(self):
        self.callGameViewer(20)

    def slot21(self):
        self.callGameViewer(21)

    def slot22(self):
        self.callGameViewer(22)

    def slot23(self):
        self.callGameViewer(23)

    def slot24(self):
        self.callGameViewer(24)

    def slot25(self):
        self.callGameViewer(25)

    def slot26(self):
        self.callGameViewer(26)

    def slot27(self):
        self.callGameViewer(27)

    def slot28(self):
        self.callGameViewer(28)

    def slot29(self):
        self.callGameViewer(29)

    def slot30(self):
        self.callGameViewer(30)
