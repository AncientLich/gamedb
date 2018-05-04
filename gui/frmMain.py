from gui.frmMain_uic import Ui_frmMainDLG
from PySide.QtGui import QMainWindow
from gamedb.gamedb import GameDB

class frmMain(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_frmMainDLG()
        self.ui.setupUi(self)
        self.ui.searchbar.setFocus()
        # self.setFocus(self.searchbar)
        self.gamedb = GameDB('games.db')
    
    def getBtn(self, num):
        if num not in range(1,31):
            raise ValueError('frmMain.getBtn accept values from 1 to 30')
        return getattr(self.ui, 'b{:02d}'.format(num))
    
    def cleanBtns(self):
        for i in range(1,31):
            btn = self.getBtn(i)
            btn.setNull()
    
    