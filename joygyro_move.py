from pyjoycon import GyroTrackingJoyCon, get_L_id
import time
from matplotlib import pyplot as plt
from PyQt5 import QtWidgets,QtGui,QtCore
from PyQt5.QtWidgets import QApplication, \
    QWidget, QMainWindow, QMessageBox, \
    QFileDialog, QPushButton, QLabel, \
    QGridLayout, QLineEdit, QFrame, QProgressBar,QSizePolicy, QVBoxLayout,QStackedLayout,QHBoxLayout
from PyQt5.QtGui import QFont, QKeyEvent, QTextCharFormat, QPen,QPainter, QBrush, QColor
from PyQt5.QtCore import QTimer,Qt,QPoint, QRect
import sys
#joycon_id = get_L_id()
#joycon = GyroTrackingJoyCon(*joycon_id)
#plt.ion()

threshold_time = 10 # how many samples


datapack = {
    'ptxs' : [],
    'ptys' : [],
    'rotxs' : [],
    'rotys' : [],
    'rotzs' : [],
    'drcxs' : [],
    'drcys' : [],
    'drczs' : [],
}

validColor = QColor(78 ,238 ,148 , 127)
bkgColor = QColor(255 ,193 ,193 ,127)
markColor = QColor(0, 0, 0, 127)

pi = 3.16

HEIGHT = 20 #px

class DrawFrame(QFrame):
    def __init__(self, parent=None):
        QFrame.__init__(self,parent)
        self._widgetpos = [ 0,0,0,0 ]
        self._range = [0.0,10.0 ]
        print(self._range)
        self.gyropos = 1.7

        self.validPtr = QPainter(self)
        self.validPtr.setBrush(QBrush(validColor, Qt.SolidPattern))
        self.validPtr.setPen(QtCore.Qt.NoPen)
        self.bkgPtr = QPainter(self)
        self.bkgPtr.setBrush(QBrush(bkgColor, Qt.SolidPattern))
        self.bkgPtr.setPen(QtCore.Qt.NoPen)
        self.dataPtr = QPainter(self)
        self.dataPtr.setBrush(QBrush(markColor, Qt.SolidPattern))
        self.dataPtr.setPen(QtCore.Qt.NoPen)

    def setrange(self,new_range,gpos,widgetpos = None):

        if widgetpos:
            self._widgetpos = widgetpos
        self._range = new_range
        self.gyropos =gpos

    def paintEvent(self, event):
        self.bkgPtr.begin(self)

            # bkg area
        self.bkgPtr.fillRect(QRect(
            self._widgetpos[0],
            (self._widgetpos[1] + self._widgetpos[1]) // 2,
            self._widgetpos[2],
            HEIGHT  ), bkgColor
        )
        self.bkgPtr.end()

        self.validPtr.begin(self)

        if self._range[0] <= self._range[1]:
            self.validPtr.fillRect(QRect(
                self._widgetpos[0] + int(self._range[0] / (2* pi) * self._widgetpos[2]) ,
                (self._widgetpos[1] + self._widgetpos[1]) // 2 ,
                int( (self._range[1] - self._range[0]) /  (2* pi) * self._widgetpos[2] ),
                self._widgetpos[1] - self._widgetpos[1]), validColor
            )
        else:
            self.validPtr.fillRect(QRect(
                self._widgetpos[0],
                (self._widgetpos[1] + self._widgetpos[1]) // 2,
                int( self._range[1] /  (2* pi) * self._widgetpos[2] ),
                self._widgetpos[1] - self._widgetpos[1]), validColor
            )# 0- range[1]
            self.validPtr.fillRect(QRect(
                self._widgetpos[0] + int( self._range[0] /  (2* pi) * self._widgetpos[2] ),
                (self._widgetpos[1] + self._widgetpos[1]) // 2,
                int( (1.0 - self._range[0] /  (2* pi))  * self._widgetpos[2] ) ,
                self._widgetpos[1] - self._widgetpos[1]), validColor
            )#  range[0] - 2pi
        self.validPtr.end()

        self.dataPtr.begin(self)

            # bkg area
        self.dataPtr.fillRect(QRect(
            self._widgetpos[0] + int(self.gyropos / (2 * pi) * self._widgetpos[2]),
            (self._widgetpos[1] + self._widgetpos[1]) // 2,
            5,
            self._widgetpos[1] - self._widgetpos[1]), markColor
        )
        self.dataPtr.end()

class Interpretor:
    def __init__(self):
        pass

from PyQt5.QtWidgets import QSlider
MAXVAL = 100
class mainWindow (QMainWindow):
    def __init__(self,joystick = False):
        super().__init__()
        self.setObjectName("MainW")

        self.setFont(QFont('microsoft Yahei'))
        self.setWindowTitle('UI')
        #self.setWindowOpacity(0.7)

        self.mainFrame = DrawFrame(self)

        self.setCentralWidget(self.mainFrame)

        #self.canvas = RangeRect(self.mainFrame)



        self.rangeValues = []
        #self.rangeValues.append(QSlider(self.mainFrame))
        self.output = []


        self.grid = QGridLayout(self.mainFrame)

        #self.canvas.stackUnder(self.mainFrame)
        self.mainFrame.setStyleSheet("background-color: #FFF8DC")
        #self.canvas.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding))
        #self.canvas.setContentsMargins(0,0,0,0)
        self.confirmBtn =QPushButton("-",self.mainFrame,)
        self.confirmBtn.setStyleSheet("background-color: #CAFF70")
        #self.confirmBtnHolder = QWidget(self.mainFrame,)
        self.grid.addWidget(self.confirmBtn,0,0)

        self.setGeometry(600, 600, 700, 600)

        try:
            qss = open("StyleSheet.qss").read()
            self.setStyleSheet(qss)
        except:
            print("Qss not loaded")

        self.sliders = []
        self.sliders.append(QSlider(self.mainFrame))
        for i in self.sliders:
            i.setOrientation(Qt.Horizontal)
        self.grid.addWidget(self.sliders[0],1,0)
        self.mainFrame.setrange()
        #print(t)

    def updRects(self):
        pass

    def updateUILayout(self,text):
        pass

    def getPos(self):
        """l = []
        l.append((self.confirmBtn.x(), self.confirmBtn.y(), self.confirmBtn.size().width(), self.confirmBtn.size().height()))
        for i in range(len(self.sliders)):
            l.append((self.sliders[i].x(),self.sliders[i].y(),self.sliders[i].size().width(),self.sliders[i].size().height()))
        return l"""
        return [ (self.confirmBtn.x(), self.confirmBtn.y(), self.confirmBtn.size().width(), self.confirmBtn.size().height() )]

    def update(self) -> None:
        posL = self.getAllpos()
        rlist = []


        gp = self.mainFrame.gyropos

        #print(rlist)
        self.mainFrame.setrange(rlist,(2.2,2.2,2.2,2.2,2.2,2.2,), posL)
        self.mainFrame.update()

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




if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainW = mainWindow()
    #mainW.updRects()
    mainW.show()
    #mainW.update()
    #print(mainW.getAllpos())
    sys.exit(app.exec_())


"""
for i in range(1000):
    #print("joycon pointer:  ", joycon.pointer)
    #print("joycon rotation: ", joycon.rotation)
    #print("joycon direction:", joycon.direction)
    plt.cla()
    #ptx,pty = joycon.pointer.to_tuple()
    rotx,roty,rotz = joycon.rotation.to_tuple()
    drcx,drcy,drcz = joycon.direction.to_tuple()
    #ptxs.append(ptx)
    #ptys.append(pty)
    datapack['rotxs'].append(rotx)
    datapack['rotys'].append(roty)
    datapack['rotzs'].append(rotz)
    datapack['drcxs'].append(drcx)
    datapack['drcys'].append(drcy)
    datapack['drczs'].append(drcz)
    plt.ylim([-1.0, 4.0])
    for key in datapack:
        plt.plot(datapack[key][-20:],label=key)
    #plt.plot(fake.cpu().detach().numpy()[0, :, 0],color='orange')
    plt.legend()
    plt.draw()
    plt.pause(0.1)
    #time.sleep(0.05)
"""