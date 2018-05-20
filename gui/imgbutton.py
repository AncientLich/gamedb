from PySide.QtGui import QPushButton
from PySide.QtGui import QPainter
from PySide.QtGui import QPixmap
from PySide.QtGui import QSizePolicy
from PySide.QtCore import QRect
from PySide.QtCore import Qt



class ImgButton(QPushButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.pcx = None
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    
    def paintEvent(self, ev):
        if self.pcx is None:
            super().paintEvent(ev)
            self.setText('NO IMAGE')
            return None
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        self.pcxrect = QRect(0,0,self.width()-1,self.height()-1)
        painter.drawPixmap(self.pcxrect, self.pcx)
    
    def setPicture(self, pcx):
        if pcx is None or pcx == '':
            self.pcx = None
            return None
        self.pcx = QPixmap('img/{}'.format(pcx))
        self.update()
