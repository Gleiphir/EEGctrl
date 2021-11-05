# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import math

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, \
    QWidget, QMainWindow, QMessageBox, \
    QFileDialog, QPushButton, QLabel, \
    QGridLayout, QLineEdit, QFrame, QProgressBar,QSizePolicy, QVBoxLayout
from PyQt5.QtGui import QFont, QKeyEvent, QTextCharFormat, QPen
from PyQt5.QtCore import QTimer,Qt
import sys

from PyQt5 import QtGui

"""
あ　か　さ
た　な　は
ま　や　ら
← 　わ　?
"""

"""
       あ
   か　 さ  た
な　は  〇  ま　や
　  ら  、  わ
 　　   ←
"""

"""

front -> Yes/default
back -> No
chars =[
         'あ',
    'か','さ','た',
'な','は','〇','ま','や',
    'ら','わ','、',
         '←'
]
"""

FOCUS_TIME_S = 1.5

FLUSH_INTERVAL_MS = 50

def FillW(s:str):
    res = [c for c in s]
    res.extend( [ ' ' ]* (13-len(s))  )
    return res

chars ={
    '〇':'',
    'あ':FillW('↑あいうえおぁぃぅぇぉ'),
    'か':FillW('↑かきくけこ'),
    'さ':FillW('↑さしすせそ'),
    'た':FillW('↑たちつてと'),
    'な':FillW('↑なにぬねの'),
    'は':FillW('↑はひふへほ'),
    'ま':FillW('↑まみむめも'),
    'や':FillW('↑やゆよゃゅょ'),
    'ら':FillW('↑らりるれろ'),
    '、':FillW('↑、。？￥！「」'),
    'わ':FillW('↑わをんーっ'),
    '←':''
}

class charsManager:
    def __init__(self,fnshow,fnoutput):
        assert callable(fnshow)
        assert callable(fnoutput)
        self.textString = ""
        self.current = chars
        self.fnshow = fnshow
        self.fnoutput = fnoutput

    def select(self,ch):
        if ch == "〇":
            self.fnoutput(self.textString)
            self.textString = ""
            self.current = chars
            return
        if ch == " ":
            return
        if ch == "←":
            self.textString = self.textString[:-1]
            self.current = chars
            return
        if not isinstance(self.current,dict):
            # in line
            if ch =="↑":
                self.current = chars
                return
            else:
                self.textString += ch
                self.current = chars # ?
                return

        else:
            #
            self.current = chars[ch]
            self.fnshow(self.current)
            #
    def getCurrent(self):
        return [t for t in self.current]

inArea = lambda i,j: abs(2-i)+abs(2-j) <= 2


class UnknownMove(Exception):
    pass

class AreaCord:

    def __init__(self,callback):
        assert callable(callback)
        self._x = 2
        self._y = 2
        self.count = 0
        self.callback = callback

    def move(self,MOVE:int):
        """none,up,right,down,left,reposition"""
        if MOVE ==0:pass
        elif MOVE==1 and inArea(self._x,self._y-1):
            self._y -= 1
        elif MOVE == 2 and inArea(self._x+1, self._y):
            self._x += 1
        elif MOVE == 3 and inArea(self._x, self._y+1):
            self._y += 1
        elif MOVE == 4 and inArea(self._x-1, self._y):
            self._x-=1
        elif MOVE == 5 :
            self._x = 2
            self._y = 2
        else:
            pass
            #raise UnknownMove
        self.count = 0
        #print(MOVE)


    def getCord(self):
        return self._x,self._y

    def back(self):
        self._x = 2
        self._y = 2

    def add(self,x:int):

        self.count = self.count + x
        if self.count > 100:
            self.count = 0
            self.callback()
        #return math.floor(self.count)

    def getCount(self):
        return self.count

    def cordIndex(self):
        return posit.index(self.getCord())

posit = [(i, j) for i in range(5) for j in range(5) if inArea(i, j)]
posit.sort(key=lambda t: abs(t[0]-2) + abs(t[1]-2)+ 0.1 *t[0]+ 0.01*t[1])
#posit = [(2, 2),(2, 0), (2, 1), (2, 3), (2, 4), (0, 2), (1, 1), (1, 2), (1, 3), (3, 1), (3, 2), (3, 3), (4, 2)]
#print(posit)
#print(posit)

class AreaCursor:
    pass


class mainWindow (QMainWindow):
    def __init__(self):
        super().__init__()
        self.setObjectName("MainW")
        self.areaCursor = AreaCord(self.inputT)
        self.setFont(QFont('microsoft Yahei'))
        self.setWindowTitle('UI')
        self.setWindowOpacity(0.7)
        self.mainFrame = QFrame(self)
        self.kbd = QFrame(self)

        self.ShowText = QLabel("  ",self)
        self.ShowText.setObjectName("ShowText")
        self.setCentralWidget(self.mainFrame)
        self.vertic = QVBoxLayout(self.mainFrame)
        self.vertic.addWidget(self.kbd)
        self.vertic.addWidget(self.ShowText)
        self.setGeometry(300, 300, 350, 300)
        self.CM = charsManager(self.updateUILayout,print)
        try:
            qss = open("StyleSheet.qss").read()
            self.setStyleSheet(qss)
        except:
            print("Qss not loaded")

        #self.maxLineWidthpx = QApplication.desktop().availableGeometry().width() // 2
        #self.maxLineWidth = self.maxLineWidthpx // (font_size * 4 //3)
        # 1px = 0.75point


        #format = QTextCharFormat()
        #format.setTextOutline(QPen(Qt.black, 0.2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        #mergeCurrentCharFormat(format)

        self.PrgBar = []
        self.BtnLbls = []
        for i,(x, y) in enumerate(posit):
            self.PrgBar.append(QProgressBar(self))
            self.BtnLbls.append(QLabel(self))
            self.PrgBar[-1].setObjectName("PB_{}_{}".format(x, y))
            self.PrgBar[-1].setTextVisible(False)


        self.blocks = [QFrame(self) for i in posit]
        self.updateUILayout(text = [key for key in chars])
        self.FlushTimer = QTimer()
        self.FlushTimer.timeout.connect(self.update)
        self.counting = 0 # 0 ->100
        self.FlushTimer.start(FLUSH_INTERVAL_MS)

        self.setFont(QFont('microsoft Yahei', self.size().height() // 6))
        grid = QGridLayout()
        grid.setSpacing(5)
        for i,pos in enumerate(posit):
            grid.addWidget(self.PrgBar[i], pos[0], pos[1])
            grid.addWidget(self.blocks[i],pos[0],pos[1])
            grid.addWidget(self.BtnLbls[i], pos[0], pos[1])
            self.PrgBar[i].setValue(0)
            self.PrgBar[i].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.BtnLbls[i].setAlignment(Qt.AlignCenter)
        self.kbd.setLayout(grid)



    def inputT(self):
        t = self.BtnLbls[self.areaCursor.cordIndex()].text()
        self.CM.select(t)
        #print("t", t)
        #print("current",self.CM.getCurrent())
        #print("TEXT ", self.CM.textString)
        self.ShowText.setText(self.CM.textString)
        self.areaCursor.back()
        self.updateUILayout(self.CM.getCurrent())

        #print(t)


    def updateUILayout(self,text):
        """
        for key in self.__dict__:
            if isinstance(self.__dict__[key],QWidget):
                self.__dict__[key].setObjectName(key)
                #print(key)
        """

        assert len(text) <= 13
        #grid.addWidget(self.LHintRT, 0, 0)

        for i,s in enumerate(text):
            self.BtnLbls[i].setText(s)


            #self.Btns[i].




        #self.setLayout(grid)

        #print(conf['customFile','stylish'])
        #self.setStyleSheet('QPushButton{color:red;}')
        #self.setStyleSheet(conf['customFile','stylish'])

    def update(self) -> None:
        for obj in self.PrgBar:
            obj.setValue(self.counting)
        ft = QFont('microsoft Yahei',self.geometry().size().height() //16 )
        for obj in self.BtnLbls:
            obj.setFont(ft)
        self.ShowText.setFont(ft)

        pos = self.areaCursor.cordIndex()
        #print("Cord Index",pos)
        self.areaCursor.add(int(100.0 / (FOCUS_TIME_S * 1000 / FLUSH_INTERVAL_MS)))
        self.PrgBar[pos].setValue(self.areaCursor.getCount())
        #self.BtnLbls[pos].setFocus()
        self.blocks[pos].setFocus()


        #print(self.counting)

    def keyPressEvent(self, a0: QKeyEvent) -> None:
        if a0.key()== Qt.Key_A:
            self.areaCursor.move(1)
            """none,up,right,down,left,reposition"""
        if a0.key()== Qt.Key_S:
            self.areaCursor.move(2)
        if a0.key()== Qt.Key_D:
            self.areaCursor.move(3)
        if a0.key()== Qt.Key_W:
            self.areaCursor.move(4)


class controller:
    pass



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainW = mainWindow()
    mainW.showFullScreen()
    sys.exit(app.exec_())

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
