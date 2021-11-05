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
from pyjoycon import GyroTrackingJoyCon, get_R_id


threshold_time = 10 # how many samples

validColor = QColor(78 ,238 ,148 , 127)
bkgColor = QColor(255 ,193 ,193 ,127)
markColor = QColor(0, 0, 0, 127)

pi = 3.16

class RangeRect(QLabel):
    def __init__(self,parent):
        super().__init__(parent)
        self.begin = QPoint()
        self.end = QPoint()

    def paintEvent(self, event):
        qp = QPainter(self)
        br = QBrush()
        qp.setBrush(br)
        qp.drawRect(QRect(self.begin, self.end))
    """
    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = event.pos()
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        self.begin = event.pos()
        self.end = event.pos()
        self.update()
    """

class Arc:
    # 2Pi < 6.40
    def __init__(self,xfrom:float,xto:float):
        assert 0 <= xfrom < 6.40
        assert 0 <= xto < 6.40
        self.fromB = xfrom
        self.toB = xto

    def isIn(self,value:float):
        assert 0 <= value < 6.40
        if self.fromB <= self.toB:
            return self.fromB <= value <= self.toB
        else:
            return 0 <= value <= self.toB or self.fromB <= value < 6.40

class DrawFrame(QFrame):
    def __init__(self, parent=None,joycon = None):
        self.joycon = joycon
        QFrame.__init__(self,parent)
        self._widgetpos = [ (0,0,0,0) ]* 12
        self._range = [(0.1,1.0) ] * 6
        print(self._range)
        self.gyropos = [1.7] * 6

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
        assert len(new_range) ==6
        assert len(gpos) ==6
        if widgetpos:
            self._widgetpos = widgetpos
        self._range = new_range
        self.gyropos =gpos

    def paintEvent(self, event):
        self.bkgPtr.begin(self)
        for i in range(6):
            # bkg area
            self.bkgPtr.fillRect(QRect(
                self._widgetpos[2 * i][0],
                (self._widgetpos[2 * i][1] + self._widgetpos[2 * i + 1][1]) // 2,
                self._widgetpos[2 * i][2],
                (self._widgetpos[2 * i + 1][1] - self._widgetpos[2 * i][1])  ), bkgColor
            )
        self.bkgPtr.end()

        self.validPtr.begin(self)
        for i in range(6):
            # bkg area
            if self._range[i][0] <= self._range[i][1]:
                self.validPtr.fillRect(QRect(
                    self._widgetpos[2 * i][0] + int(self._range[i][0] / (2* pi) * self._widgetpos[2 * i][2]) ,
                    (self._widgetpos[2 * i][1] + self._widgetpos[2 * i + 1][1]) // 2 ,
                    int( (self._range[i][1] - self._range[i][0]) /  (2* pi) * self._widgetpos[2 * i][2] ),
                    self._widgetpos[2 * i + 1][1] - self._widgetpos[2 * i][1]), validColor
                )
            else:
                self.validPtr.fillRect(QRect(
                    self._widgetpos[2 * i][0],
                    (self._widgetpos[2 * i][1] + self._widgetpos[2 * i + 1][1]) // 2,
                    int( self._range[i][1] /  (2* pi) * self._widgetpos[2 * i][2] ),
                    self._widgetpos[2 * i + 1][1] - self._widgetpos[2 * i][1]), validColor
                )# 0- range[1]
                self.validPtr.fillRect(QRect(
                    self._widgetpos[2 * i][0] + int( self._range[i][0] /  (2* pi) * self._widgetpos[2 * i][2] ),
                    (self._widgetpos[2 * i][1] + self._widgetpos[2 * i + 1][1]) // 2,
                    int( (1.0 - self._range[i][0] /  (2* pi))  * self._widgetpos[2 * i][2] ) ,
                    self._widgetpos[2 * i + 1][1] - self._widgetpos[2 * i][1]), validColor
                )#  range[0] - 2pi
        self.validPtr.end()

        self.dataPtr.begin(self)
        for i in range(6):
            # bkg area
            self.dataPtr.fillRect(QRect(
                self._widgetpos[2 * i][0] + int(self.gyropos[i] / (2 * pi) * self._widgetpos[2 * i][2]),
                (self._widgetpos[2 * i][1] + self._widgetpos[2 * i + 1][1]) // 2,
                5,
                self._widgetpos[2 * i + 1][1] - self._widgetpos[2 * i][1]), markColor
            )
        self.dataPtr.end()


    def readJoyCon(self):
        if not self.joystick:
            return None
        rotx, roty, rotz = self.joycon.rotation.to_tuple()
        drcx, drcy, drcz = self.joycon.direction.to_tuple()
        self.gyropos = [rotx, roty, rotz , drcx, drcy, drcz ]

class Interpretor:
    def __init__(self):
        pass

from PyQt5.QtWidgets import QSlider
MAXVAL = 100
class mainWindow (QMainWindow):
    def __init__(self,joystick = None):
        super().__init__()
        self.setObjectName("MainW")

        self.joystick = joystick

        self.setFont(QFont('microsoft Yahei'))
        self.setWindowTitle('UI')
        #self.setWindowOpacity(0.7)

        self.mainFrame = DrawFrame(self)

        self.setCentralWidget(self.mainFrame)

        #self.canvas = RangeRect(self.mainFrame)

        self.gryos = [0.,0.,0.,0.,0.,0.]

        self.rangeValues = []
        self.output = []

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.readGryo)
        self.timer.start(25)

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
        for i in range(6):
            self.rangeValues.append(QLabel('0.0000 -- 0.0000',self.mainFrame))
            self.output.append(QLabel('POS : 0.0000 | ___ ', self.mainFrame))
            self.sliders.append([])
            for j in range(2):
                self.sliders[i].append(QSlider(Qt.Horizontal,self.mainFrame,))
                self.sliders[i][j].setMaximum(100)
                self.sliders[i][j].valueChanged.connect(self.update)
        for i in range(6):
            self.grid.addWidget(self.rangeValues[i],i*2+1,1)
            self.grid.addWidget(self.output[i],i*2+2,1)
            for j in range(2):
                self.grid.addWidget(self.sliders[i][j],i*2+1+j,0)

        #print(t)



    def readGryo(self):
        if not self.joystick:
            return
        rotx, roty, rotz = self.joystick.rotation.to_tuple()
        drcx, drcy, drcz = self.joystick.direction.to_tuple()
        self.gryos = [rotx+ pi, roty+ pi, rotz + pi, drcx + pi, drcy+ pi, drcz+ pi]
        self.update()

    def updateUILayout(self,text):
        pass

    def getAllpos(self):
        l = []
        for i in range(6):
            for j in range(2):
                l.append((self.sliders[i][j].x(),self.sliders[i][j].y(),self.sliders[i][j].size().width(),self.sliders[i][j].size().height()))
        return l

    def update(self) -> None:
        posL = self.getAllpos()
        rlist = []
        for i in range(6):
            L = self.sliders[i][0].value()/100 * 2* pi
            R =self.sliders[i][1].value()/100 * 2* pi
            gp = self.mainFrame.gyropos[i]
            rlist.append(( L  , R ))
            self.rangeValues[i].setText("{:4f} {} {:4f}".format(L,
                                                                ('<>','--',)[L <= R] ,
                                                                R))

            SIGN = (L <= R and L <= gp <=R) or ( L > R and (0 <= gp <=R or L <= gp <= 2 * pi ) )
            self.output[i].setText("POS : {:4f} | {} ".format(self.mainFrame.gyropos[i],
                                                              ('OUT','IN ',)[SIGN] ) )
        #print(rlist)
        self.mainFrame.setrange(rlist,self.gryos, posL)
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
    joycon_id = get_R_id()
    joycon = GyroTrackingJoyCon(*joycon_id)
    print(joycon_id)
    app = QApplication(sys.argv)
    mainW = mainWindow(joycon)

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