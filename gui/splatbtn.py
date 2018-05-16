from PySide.QtGui import QPushButton
from PySide.QtGui import QPainter
from PySide.QtGui import QPixmap
from PySide.QtCore import QRect
from PySide.QtCore import Qt
from PySide.QtCore import SIGNAL
from datetime import date
from gamedb.gameview import StorePlat
from gamedb.gameview import GameView
import subprocess



class SplatButton(QPushButton):
    def __init__(self, game=None):
        super().__init__()
        self.setNull()
        self.connect(self, SIGNAL("clicked()"), self.launch)
    
    def launch(self):
        if self.link:
            subprocess.call(['firefox', self.link])
    
    def paintEvent(self, ev):
        super().paintEvent(ev)
        painter = QPainter(self)
        pen = painter.pen()
        if self.store is None or self.platform is None:
            painter.drawRect(0,0,self.width()-1,self.height()-1)
            rect = QRect(1,1,self.width()-3,self.height()-3)
            painter.fillRect(rect, Qt.darkBlue)
            return None
        storeRect = QRect(3,3, 30, 30)
        platRect = QRect(43,3, 30, 30)
        langRect = QRect(83,3, 30, 30)
        expRect = QRect(123, 3, self.width()-126, 30)
        storeimg = QPixmap('img/{}'.format(self.store))
        platimg = QPixmap('img/{}'.format(self.platform))
        if self.expire == 'EXPIRED!':
            painter.setPen(Qt.red)
        painter.drawPixmap(storeRect, storeimg)
        painter.drawPixmap(platRect, platimg)
        painter.drawText(langRect, Qt.AlignCenter, self.lang)
        if self.expire is not None:
            painter.drawText(expRect, Qt.AlignCenter, self.expire)
        painter.setPen(pen)
    
    def setNull(self):
        self.store = None
        self.platform = None
        self.lang = None
        self.link = None
        self.expire = None
        self.setVisible(False)
        self.update()
    
    def isNull(self):
        return bool(not self.store)
    
    def setGame(self, store, platform, lang, link, expire):
        self.store = store
        self.platform = platform
        self.lang = lang
        self.link = link
        self.expire = None
        if expire is not None:
            d, m, y = expire
            expdate = date(day=d, month=m, year=y)
            if expdate < date.today():
                self.expire = 'EXPIRED!'
            else:
                self.expire = 'Expiration date: {:02d}/{:02d}/{:04d}'.format(
                    d, m, y)
        self.setVisible(True)
        self.update()