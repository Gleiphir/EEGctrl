# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import math
import random
import time

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, \
    QWidget, QMainWindow, QMessageBox, \
    QFileDialog, QPushButton, QLabel, \
    QGridLayout, QLineEdit, QFrame, QProgressBar,QSizePolicy, QVBoxLayout
from PyQt5.QtGui import QFont, QKeyEvent, QTextCharFormat, QPen
from PyQt5.QtCore import QTimer,Qt
import sys
import pygame
from pygame.locals import *
from PyQt5 import QtGui
from io import BytesIO
import gtts
import simpleaudio as sa
from pydub import AudioSegment
from pydub.playback import play
import os
os.environ['TMPDIR'] = os.getcwd()
#from mpyg321.mpyg321 import MPyg321Player


FOCUS_TIME_S = 2.5

FLUSH_INTERVAL_MS = 1000

WIDTH = 800
HEIGHT = 800
NUM_DOTS = 10

class mainWindow (QMainWindow):
    def __init__(self,joystick = False):
        super().__init__()
        self.setObjectName("MainW")

        self.setFont(QFont('microsoft Yahei'))
        self.setWindowTitle('UI')
        #self.setWindowOpacity(0.7)
        self.mainFrame = QFrame(self)


        try:
            qss = open("measureStyleSheet.qss").read()
            self.setStyleSheet(qss)
        except:
            print("Qss not loaded")

        #self.maxLineWidthpx = QApplication.desktop().availableGeometry().width() // 2
        #self.maxLineWidth = self.maxLineWidthpx // (font_size * 4 //3)
        # 1px = 0.75point

        self.Seq = []
        self.area  =  QLabel(self.mainFrame)
        canvas = QtGui.QPixmap(WIDTH, HEIGHT)
        self.area.setPixmap(canvas)
        self.setCentralWidget(self.mainFrame)


        #format = QTextCharFormat()
        #format.setTextOutline(QPen(Qt.black, 0.2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        #mergeCurrentCharFormat(format)

        self.FlushTimer = QTimer()
        self.FlushTimer.timeout.connect(self.update)
        self.FlushTimer.setSingleShot(False)
        self.counting = 0 # 0 ->100
        self.FlushTimer.start(FLUSH_INTERVAL_MS)


        self.setFont(QFont('microsoft Yahei', self.size().height() // 6))
        grid = QGridLayout()
        grid.setSpacing(5)
        sp = QSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)

        self.Xbar = QProgressBar(self.mainFrame)
        self.Xbar.setSizePolicy(sp)
        self.Ybar = QProgressBar(self.mainFrame)
        self.Ybar.setOrientation(Qt.Vertical)
        grid.addWidget(self.area, 0, 1)
        grid.addWidget(self.Ybar, 0, 0)
        grid.addWidget(self.Xbar,1,1)


        self.mainFrame.setLayout(grid)

        #self.paintCanvas()

    def paintCanvas(self):
        from random import randint
        pixmap  = QtGui.QPixmap(WIDTH, HEIGHT)
        painter = QtGui.QPainter(pixmap)
        pen = QtGui.QPen()
        pen.setWidth(10)

        for n in range(NUM_DOTS):
            if n >= len(self.Seq):
                break
            pen.setColor(QtGui.QColor(math.floor(255 / NUM_DOTS * (NUM_DOTS - n)),math.floor(255 / NUM_DOTS * (NUM_DOTS - n)) , math.floor(255 / NUM_DOTS * (NUM_DOTS - n))))
            painter.setPen(pen)
            painter.drawPoint(
                math.floor(self.Seq[-n][0] * WIDTH / 100),  # x
                math.floor(HEIGHT - self.Seq[-n][1] * HEIGHT / 100) # y
            )

        painter.end()
        self.Xbar.setValue(self.Seq[-1][0])
        self.Ybar.setValue(self.Seq[-1][1])
        self.area.setPixmap(pixmap)

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
        self.Seq.append(  (random.randint(0,100),random.randint(0,100),) )
        self.paintCanvas()

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
    mainW.show()
    sys.exit(app.exec_())

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
