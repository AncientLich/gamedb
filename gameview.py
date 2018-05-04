import sys
from PySide.QtCore import *
from PySide.QtGui import *
from gui.frmMain import frmMain


def main():
    qt_app = QApplication(sys.argv)
    frm_main = frmMain()
    
    frm_main.show()
    qt_app.exec_()



if __name__ == "__main__":
    main()
