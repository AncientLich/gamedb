from gui.frmMain_uic import Ui_frmMainDLG
from PySide.QtGui import QMainWindow
from PySide.QtGui import QIntValidator
from PySide.QtCore import SIGNAL
from PySide.QtCore import Qt
from gamedb.gamedb import GameDB
from gui.gamedlg import GameDlg
from gui.pcosdlg import PcOsDlg
from functools import partial
import re

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
                      'ps_store', 'physical'):
            btn = getattr(self.ui, check)
            btn.stateChanged.connect(lambda x: self.showResult())
        self.ui.pc.stateChanged.connect(self.slotPc)
        self.ui.btnPrev.clicked.connect(lambda: self.slotPageChanged(-1))
        self.ui.btnNext.clicked.connect(lambda: self.slotPageChanged(1))
        self.ui.page.returnPressed.connect(lambda: self.slotPageChanged(0))
        self.ui.btnSearch.clicked.connect(self.exec_searchbar)
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
            # than the result will be refreshed twice
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
    
    def slotPageChanged(self, adder):
        if adder != 0:
            self.ui.btnPrev.setEnabled(True)
            self.ui.btnNext.setEnabled(True)
            totpages = int(self.ui.totalPages.text())
            page = int(self.ui.page.text())
            page += adder
            self.ui.page.setText(str(page))
            if page == 1:
                self.ui.btnPrev.setEnabled(False)
            if page == totpages:
                self.ui.btnNext.setEnabled(False)
        self.showResult(reset_page1=False)
    
    '''
    # esb = exec_searchbar -> this function is used by exec_searchbar
    def _esb_assign(self, value, op='>='):
        try:
            value = (op, int(value))
        except ValueError:
            value = None
        return value
    '''
    
    def exec_searchbar(self):
        searchtxt = self.ui.searchbar.text()
        tags = []
        priority = None
        vote = None
        # ------
        # syntax 1: tag/mytag
        # ------
        # rx = r'((?:tag)|(?:pri(?:ority)?)|(?:vote))\/(\S+)'
        rx = r'tag\/(\S+)'
        m = re.search(rx, searchtxt)
        '''
        while m:
            searchtxt = searchtxt.replace(m.group(0), '')
            if m.group(1) == 'tag':
                tags.append(m.group(2))
            elif m.group(1) in ('pri', 'priority'):
                priority = self._esb_assign(m.group(2))
            else:
                vote = self._esb_assign(m.group(2))
            m = re.search(rx, searchtxt)
        '''
        while m:
            searchtxt = searchtxt.replace(m.group(0), '')
            tags.append(m.group(1))
            m = re.search(rx, searchtxt)
        # ------
        # syntax 2: tag=[tag1, tag2, tag3]
        # ------
        rx = r'tag\=\[(.*?)\]'
        m = re.search(rx, searchtxt)
        if m:
            tags = m.group(1).split(',')
            searchtxt = searchtxt.replace(m.group(0), '')
        for index, tag in enumerate(tags):
            tags[index] = tag.strip()
        # ------
        # the remaining part of search should be used for title search
        # ------
        searchtxt = searchtxt.strip()
        title = None
        if len(searchtxt) > 0:
            title = searchtxt
        self.game_title = title
        self.filter_tags = tags        
        self.showResult()
    
    def showResult(self, *, reset_page1=True):
        if reset_page1:
            self.ui.page.setText('1')
            self.ui.btnPrev.setEnabled(False)
        if self.ui.showFranchises.isChecked():
            # todo
            return None
        # most common case: Show Games
        strs = [('steam', self.ui.steam), ('gog', self.ui.gog),
                ('uplay', self.ui.uplay), ('psn', self.ui.ps_store)]
        stores = [store_name for store_name, store in strs 
                  if store.isChecked()]
        if self.ui.physical.isChecked():
            stores.extend(['cd', 'hd'])
        plats = [('ps4', self.ui.ps4), ('ps3', self.ui.ps3),
                 ('psvita', self.ui.ps_vita)]
        platforms = [platname for platname, platform in plats
                     if platform.isChecked()]
        plats = [('win', self.platform_win), ('mac', self.platform_mac),
                 ('linux', self.platform_linux)]
        platforms.extend([platname for platname, platform in plats
                          if platform])
        franchise = self.ui.franchise.text()
        if stores == []:
            stores = None
        if platforms == []:
            platforms = None
        if len(franchise.strip()) == 0:
            franchise = None
        results, count = self.gamedb.filter_games(
            title = self.game_title,
            tags = self.filter_tags,
            platforms = platforms,
            stores = stores,
            franchise = franchise,
            sortby = self.ui.sort.currentText(),
            page = int(self.ui.page.text()),
            # calculate count_total when pagnum was reset to 1 (new search)
            count_total = reset_page1
        )
        self.cleanBtns()
        for index, result in enumerate(results):
            try:
                btn = self.getBtn(index +1)
            except ValueError:
                break
            btn.setGame(self.gamedb, *result)
        # if reset_page1 -> calculate the amount of total pages
        if not reset_page1:
            return None
        # updating total_page label
        totpages = 1 + int(count / 30)
        if count % 30 == 0 and count != 0:
            totpages -= 1
        self.ui.totalPages.setText(str(totpages))
        # disabling "next page" button if total pages are 1
        if totpages == 1:
            self.ui.btnNext.setEnabled(False)
        # updating self.ui.page Validator to accept from 1 to total_pages
        validator = QIntValidator(1, totpages)
        self.ui.page.setValidator(validator)