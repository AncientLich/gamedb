from gui.gamedlg_uic import Ui_GameDlgUI
from PySide.QtGui import QDialog
from PySide.QtGui import QGraphicsScene
from PySide.QtGui import QPixmap
from PySide.QtGui import QGraphicsPixmapItem
from PySide.QtCore import SIGNAL
from PySide.QtCore import Qt
from gamedb.gamedb import GameDB
from gamedb.gameview import StorePlat
from gamedb.gameview import GameView



class GameDlg(QDialog):
    def __init__(self, game):
        super().__init__()
        self.ui = Ui_GameDlgUI()
        self.ui.setupUi(self)
        self.xset(game)
        
    def getBtn(self, value):
        return getattr(self.ui, 'b{:02d}'.format(value))
    
    def cleanBtns(self):
        for i in range(1,11):
            btn = self.getBtn(i)
            btn.setNull()
    
    def xset(self, game):
        self.game = game
        self.ui.picture.setPicture(self.game.img)
        self.ui.show_tags.clear()
        for tag in self.game.tags:
            self.ui.show_tags.addItem(tag)
        self.ui.img.setText(self.game.img)
        self.ui.title.setText(self.game.title)
        # self.ui.franchise.setText(self.game.franchise)
        self.ui.year.setText(str(self.game.year))
        self.ui.vote.setText(str(self.game.vote))
        self.ui.priority.setText(str(self.game.priority))
        self.ui.note.setText(self.game.note)
        self.cleanBtns()
        for index, storeplat in enumerate(self.game.storeplats):
            try:
                btn = self.getBtn(index +1)
            except ValueError:
                break
            btn.setGame(storeplat.store, storeplat.platform,
                        storeplat.lang, storeplat.link,
                        storeplat.expiredate)
        
        self.setWindowTitle(
            'Game Details (#{})'.format(self.game.xid)
        )
    
    