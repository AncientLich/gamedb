from PySide.QtGui import QPushButton
from PySide.QtGui import QPainter
from PySide.QtGui import QPixmap
from PySide.QtCore import QRect
from PySide.QtCore import Qt



class GButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setNull()
    
    def paintEvent(self, ev):
        painter = QPainter(self)
        painter.drawRect(0,0,self.width()-1,self.height()-1);
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        self.pcxrect = QRect(3,3, self.width()-6, self.height()*3/5)
        if self.pcx is not None:
            painter.drawPixmap(self.pcxrect, self.pcx)
        self._drawVote(painter)
        self._drawPriority(painter)
        # 50
        painter.drawText(3,(self.height()*3/5)+5, 
                         self.width()-6, 50,
                         Qt.TextWordWrap,
                         self.title)
    
    def _drawVote(self, painter):
        if self.isFranchise:
            return self._drawFranchise(painter)
        elif not isinstance(self.vote, int) or self.vote not in range(0,101):
            return None
        for rng, favour, color, textcolor in [
                            ((90, 101), 'Acclaimed', Qt.green, Qt.black),
                            ((75, 90), 'Favorable', Qt.darkGreen, Qt.white),
                            ((50,75), 'Mixed/Average', Qt.yellow, Qt.black),
                            ((20,50), 'Unfavorable', Qt.magenta, Qt.white),
                            ((0, 20), 'Disliked', Qt.red, Qt.white)]:
            if self.vote in range(*rng):
                break
        pen = painter.pen()
        rect = QRect(self.pcxrect.x(), self.pcxrect.y(),
                     30, 30)
        painter.fillRect(rect, color)
        painter.setPen(textcolor)
        painter.drawText(rect,
                         Qt.AlignCenter,
                         str(self.vote))
        painter.setPen(pen)
    
    def _drawFranchise(self, painter):
        pen = painter.pen()
        rect = QRect(self.pcxrect.x(), self.pcxrect.y(),
                     8 * len('franchise'), 20)
        painter.fillRect(rect, Qt.blue)
        painter.setPen(Qt.white)
        painter.drawText(rect, Qt.AlignCenter, 'Franchise')
        painter.setPen(pen)
        
    def _drawPriority(self, painter):
        if self.priority not in range(0, 11) or self.isFranchise:
            return None
        pen = painter.pen()
        brush = painter.brush()
        x = self.pcxrect.width() - 30 +1
        y = self.pcxrect.height() - 30 +1
        rect = QRect(x, y, 30, 30)
        for rng, color, pen2 in [((9, 11), Qt.green, Qt.black),
                           ((7, 9), Qt.darkGreen, Qt.white),
                           ((5, 7), Qt.yellow, Qt.black),
                           ((3, 5), Qt.magenta, Qt.white),
                           ((0, 3), Qt.red, Qt.white)]:
            if self.priority in range(*rng):
                break
        painter.setBrush(color)
        painter.drawEllipse(rect)
        painter.setBrush(brush)
        painter.setPen(pen2)
        painter.drawText(rect, Qt.AlignCenter, str(self.priority))
        painter.setPen(pen)
    
    '''
    def _setGameImage(self, imgtext):
        if imgtext is None:
            self.pcx = None
        else:
            self.pcx = QPixmap(imgtext)
    '''
    
    def setNull(self):
        self.xid = 0
        self.title = ""
        self.vote = None
        self.isFranchise = False
        self.priority = None
        self.pcx = None
        self.setVisible(False)
        self.update()
    
    def setGame(self, xid, title, vote, priority, pcx):
        self.xid = xid
        self.title = title
        self.vote = vote
        self.isFranchise = False
        self.priority = priority
        self.pcx = pcx
        self.setVisible(True)
        self.update()
    
    def setFranchise(self, xid, title, pcx):
        self.xid = xid
        self.title = title
        self.vote = None
        self.isFranchise = True
        self.priority = None
        self.pcx = pcx
        self.setVisible(True)
        self.update()

