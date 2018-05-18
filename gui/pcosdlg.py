from gui.pcos_uic import Ui_PcOsDLG
from PySide.QtGui import QDialog
from PySide.QtCore import Qt

class PcOsDlg(QDialog):
    def __init__(self, parent, linux, win, mac):
        super().__init__(parent)
        self.ui = Ui_PcOsDLG()
        self.ui.setupUi(self)
        self.ui.linux.setChecked(linux)
        self.ui.win.setChecked(win)
        self.ui.mac.setChecked(mac)
        self.org_linux = linux
        self.org_win = win 
        self.org_mac = mac 
        self.ui.ok.clicked.connect(self.accept)
        self.ui.canc.clicked.connect(self.discardChanges)
    
    def discardChanges(self):
        for xosname in ['linux', 'win', 'mac']:
            xbool = getattr(self, 'org_{}'.format(xosname))
            btn = getattr(self.ui, xosname)
            if xbool:
                btn.setCheckState(Qt.Checked)
            else:
                btn.setCheckState(Qt.Unchecked)
        self.reject()