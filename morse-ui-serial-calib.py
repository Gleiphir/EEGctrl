# Used for Linux on Raspi

import math

from pyjoycon import GyroTrackingJoyCon, get_L_id,get_R_id

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, \
    QWidget, QMainWindow, QMessageBox, \
    QFileDialog, QPushButton, QLabel, \
    QGridLayout, QLineEdit, QFrame, QProgressBar,QSizePolicy, QVBoxLayout
from PyQt5.QtGui import QFont, QKeyEvent, QTextCharFormat, QPen, QFont, QKeyEvent, QTextCharFormat, QPainter, QBrush, QColor
from PyQt5.QtCore import QTimer,Qt, QRect
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
from morse_jp_func import MorseMapping,NearestHint
import urllib,json

import pyttsx3
engine = pyttsx3.init()

import argparse

import serial
from serial.tools import list_ports

print([ port.device for port in list_ports.comports()])

"""
Aparser = argparse.ArgumentParser()
Aparser.add_argument("autocali",type=bool,default=False)


args = Aparser.parse_args()
"""
calib_zero = 0.0

GyroMapFn = lambda AglX, AglY, AglZ: (AglX - calib_zero)

ThresholdL = -10.0
ThresholdR = 5.0

INPUT_SUSPEND_WINDOW_MS = 1000

#scanfloat = lambda S: [ float(x)  for x  in S.split(' ') ]
def scanfloat(chunk:bytes):
    lines = chunk.split(b'\r\n') #  b'0.49 -1.29 -88.62'
    #print(lines)
    for line in reversed(lines):
        nums = line.split(b' ')
        if len(nums) != 3 :
            continue
        try:
            return [ float(num.decode('utf-8')) for num in nums ]
        except ValueError:
            continue
    return None,None,None

def convert_kata_to_hira(katakana):
    hira_tupple = ('あ','い','う','え','お','か','き','く','け','こ','さ','し','す','せ','そ','た','ち','つ','て','と','な','に','ぬ','ね','の','は','ひ','ふ','へ','ほ','ま','み','む','め','も','や','ゆ','よ','ら','り','る','れ','ろ','わ','を','ん','っ','ゃ','ゅ','ょ','ー','が','ぎ','ぐ','げ','ご','ざ','じ','ず','ぜ','ぞ','だ','ぢ','づ','で','ど','ば','び','ぶ','べ','ぼ','ぱ','ぴ','ぷ','ぺ','ぽ')
    kata_tupple = ('ア','イ','ウ','エ','オ','カ','キ','ク','ケ','コ','サ','シ','ス','セ','ソ','タ','チ','ツ','テ','ト','ナ','ニ','ヌ','ネ','ノ','ハ','ヒ','フ','ヘ','ホ','マ','ミ','ム','メ','モ','ヤ','ユ','ヨ','ラ','リ','ル','レ','ロ','ワ','ヲ','ン','ッ','ャ','ュ','ョ','ー','ガ','ギ','グ','ゲ','ゴ','ザ','ジ','ズ','ゼ','ゾ','ダ','ヂ','ヅ','デ','ド','バ','ビ','ブ','ベ','ボ','パ','ピ','プ','ペ','ポ')
    k_to_h_dict = dict()
    for i in range(len(hira_tupple)):
        k_to_h_dict[kata_tupple[i]] = hira_tupple[i]
    hiragana = ""
    for i in range(len(katakana)):
        hiragana += k_to_h_dict[katakana[i]]
    return hiragana

def jp_hira2kanji(input_text:str):
    url = "http://www.google.com/transliterate?"
    param = {'langpair': 'ja-Hira|ja', 'text': input_text}
    paramStr = urllib.parse.urlencode(param)
    #print(url + paramStr)
    readObj = urllib.request.urlopen(url + paramStr)
    response = readObj.read()
    data = json.loads(response)
    fixed_data = json.loads(json.dumps(data, ensure_ascii=False))
    return "".join([word[1][0] for word in fixed_data])

def pytts_audioPlay(text:str):
    engine.say(text)
    engine.runAndWait()

def gTTS_audioPlay(text:str):
    with BytesIO() as f:
        gtts.gTTS(text=text, lang='ja').write_to_fp(f)
        f.seek(0)
        song = AudioSegment.from_file(f, format="mp3")
        play(song)

validColor = QColor(78 ,238 ,148 , 127)
bkgColor = QColor(255 ,193 ,193 ,127)
markColor = QColor(0, 0, 128, 127)

calib_time_ms = 180000
calib_stop_angle = 0.8

class RangeArea(QLabel):
    def __init__(self, parent=None):
        QLabel.__init__(self,parent)
        self._widgetpos = 0.0
        self._range = (ThresholdL,ThresholdR)
        print(self._range)
        self.gyropos = 0

        self.validPtr = QPainter(self)
        self.validPtr.setBrush(QBrush(validColor, Qt.SolidPattern))
        self.validPtr.setPen(Qt.NoPen)
        self.bkgPtr = QPainter(self)
        self.bkgPtr.setBrush(QBrush(bkgColor, Qt.SolidPattern))
        self.bkgPtr.setPen(Qt.NoPen)
        self.dataPtr = QPainter(self)
        self.dataPtr.setBrush(QBrush(markColor, Qt.SolidPattern))
        self.dataPtr.setPen(Qt.NoPen)
        self.setFixedHeight(20)
        self.area = None

    def setArea(self,x,y,width,height):
        self.area = QRect(x,y,width,20)

    def setGpos(self,gpos:float):
        self.gyropos = gpos
        #print("---------------gryopos:{}-------------".format(self.gyropos))
        #print("------area----{},{},{},{},".format(self.area.x(),self.area.y(),self.area.width(),self.area.height()))

    def setrange(self,new_range,gpos,widgetpos = None):
        assert len(new_range) ==6
        assert len(gpos) ==6
        if widgetpos:
            self._widgetpos = widgetpos
        self._range = new_range
        self.gyropos =gpos


    def paintEvent(self, event):
        self.bkgPtr.begin(self)
        self.bkgPtr.fillRect(
            self.area,
            bkgColor
        )
        self.bkgPtr.end()

        self.validPtr.begin(self)
        self.validPtr.fillRect(QRect(
               self.area.x() + self.area.width() // 2 + int(self.area.width() / 2 * calib_zero / 90.0) + int( self.area.width() /2 * ThresholdL / 90.0 )  ,
                self.area.y() ,
                int( self.area.width() /2  * (ThresholdR - ThresholdL) / 90.0 ) ,
                self.area.height()
            ),
            validColor
        )
        self.validPtr.end()

        self.dataPtr.begin(self)
        self.dataPtr.fillRect(QRect(
            self.area.x() + self.area.width() // 2 + int(self.area.width() / 2 * calib_zero / 90.0) - 1,
            self.area.y(),
            3,
            self.area.height()
        )
            , QColor(255, 100, 255, 127)
        )
        self.dataPtr.fillRect(QRect(
            self.area.x() + self.area.width() // 2 + int(self.area.width() / 2 * calib_zero / 90.0) +int(self.area.width() /2  * self.gyropos / 90.0),
            self.area.y(),
            5,
            self.area.height()
        )
        , markColor
        )

        self.dataPtr.end()
        #print(":::: {}".format(self.area.x() // 2 + int(self.area.width() * self.gyropos / 90.0)))

class mainWindow (QMainWindow):
    def __init__(self,fontsize=40,antiDrift = True):
        super().__init__()
        self.setObjectName("MainW")
        self.setFont(QFont('microsoft Yahei'))
        self.setWindowTitle('UI')
        #self.setWindowOpacity(0.7)
        self.mainFrame = QFrame(self)
        self.mainFrame.setStyleSheet("font-size:{}px".format(fontsize))



        self.gryoShow = RangeArea(self)
        self.lastGryo = 0.0


        self.ShowKanji = QLabel("kanji",self)
        self.ShowKanji.setObjectName("ShowKanji")
        self.ShowKanji.setStyleSheet("background-color:#C0E0C0")
        self.ShowText = QLabel("text",self)
        self.ShowText.setObjectName("ShowText")
        self.ShowText.setStyleSheet("background-color:#E0E0C0")
        self.ShowMorse = QLabel("morse", self)
        self.ShowMorse.setObjectName("ShowMorse")
        self.ShowMorse.setStyleSheet("background-color:#E0C0E0")
        self.ShowHint = QLabel("Hint\nHint\nHint",self)
        self.ShowHint.setObjectName("ShowHint")
        self.ShowHint.setStyleSheet("background-color:#C0E0E0")
        self.ShowHint.setWordWrap(True)


        self.setCentralWidget(self.mainFrame)
        self.vertic = QVBoxLayout(self.mainFrame)

        self.vertic.addWidget(self.gryoShow)
        self.vertic.addWidget(self.ShowKanji)
        self.vertic.addWidget(self.ShowText)
        self.vertic.addWidget(self.ShowMorse)
        self.vertic.addWidget(self.ShowHint)
        self.setGeometry(100, 100, 1000, 900)

        try:
            qss = open("StyleSheet.qss").read()
            self.setStyleSheet(qss)
        except:
            print("Qss not loaded")

        self.ser = None




        #self.suspendTimer.timeout.connect()

        self.setFont(QFont('microsoft Yahei', self.size().height() // 6))
        grid = QGridLayout()
        grid.setSpacing(5)

        self.mainFrame.setLayout(grid)
        self.gryoShow.setArea(0,0,self.width(),self.height())

        self.textStr = ""
        self.morseStr = ""

        self.suspendTimer = QTimer(self)
        self.suspendTimer.setSingleShot(True)

        self.defaultOPTimer = QTimer(self)
        self.defaultOPTimer.timeout.connect(lambda : self.MrsInput(0))

        self.autoUpdateTimer  = QTimer(self)
        self.autoUpdateTimer.timeout.connect(self.readSerial)
        self.autoUpdateTimer.start(20)

        self.calibTimer = QTimer(self)
        self.calibTimer.timeout.connect(self.reCalib)

        self.serialInit()

    def reCalib(self):
        global calib_zero
        calib_zero = self.lastGryo
        self.ShowHint.setText("Recalibration")

    def serialInit(self):
        if len(list_ports.comports()) > 0:
            self.ser = serial.Serial(list_ports.comports()[0].device, baudrate=115200)
            if not self.ser.is_open:
                self.ser.open()
        while len(self.ser.read_all() ) == 0:
            pass
        #print(self.ser.read_all())
        self.ser.write(b'H')


    def MrsInput(self,sig:int):
        """ 0 = / ; 1 = . ; 2 = - ;  """
        if sig == 0:
            if len(self.morseStr) ==0 or not self.morseStr in MorseMapping:
                self.morseStr = ""
            else:
                self.addCharWFunc(MorseMapping[self.morseStr])
                #self.textStr = self.textStr + MorseMapping[self.morseStr]
                self.morseStr = ""
        elif sig == 1:
            self.morseStr = self.morseStr +  '・'
        elif sig == 2:
            self.morseStr = self.morseStr + '－'
        else:
            pass
        if len(self.morseStr) >= 8:
            self.morseStr = ""

    def readSerial(self):
        if not self.ser:
            self.update()
            return None

        if not self.ser.readable():
            self.update()
            return None
        datachunk = self.ser.read_all()
        if len(datachunk) ==0:
            return
        #print(datachunk)
        aglx, agly, aglz = scanfloat(datachunk)
        if not aglx:
            return
        controlval = GyroMapFn(aglx, agly, aglz)
        print(aglx, agly, aglz," CtrlVal: " ,controlval)
        self.gryoShow.setGpos(controlval)
        if self.suspendTimer.isActive():
            self.update()
            return None
        if self.lastGryo - controlval > calib_stop_angle:
            self.calibTimer.start(calib_time_ms)

        if controlval <= ThresholdL:
            self.defaultOPTimer.stop()
            self.MrsInput(1)
            self.suspendTimer.start(INPUT_SUSPEND_WINDOW_MS)
        elif controlval >= ThresholdR:

            self.defaultOPTimer.stop()
            self.MrsInput(2)
            self.suspendTimer.start(INPUT_SUSPEND_WINDOW_MS)
        else:
            if not self.defaultOPTimer.isActive():
                self.defaultOPTimer.start(1000)
            #self.MrsInput(0)
        self.update()

    def addCharWFunc(self, chr:str):
        """ funtional chrs"""
        if chr == '入': # input
            self.speak()
            self.clearText()
            return
        if chr == '←': # backspace
            if len(self.textStr) >=1: self.textStr = self.textStr[:-1]
            return
        if chr == '消': # backspace
            self.textStr = ""
            return
        if chr == '礼': # backspace
            self.textStr = "ありがとうございます"
            self.speak()
            self.clearText()
            return
        if chr == '〇': # backspace
            self.textStr = "はい、そうです"
            self.speak()
            self.clearText()
            return
        if chr == '✖': # backspace
            self.textStr = "いいえ、違います"
            self.speak()
            self.clearText()
            return
        if chr == '呼': # backspace
            self.textStr = "介護者を呼んでください"
            self.speak()
            self.clearText()
            return

        self.textStr = self.textStr + chr

    def clearText(self):
        self.textStr = ""
        self.morseStr = ""
        self.ShowHint.setText("")
        self.update()


    def showHint(self):
        if len(self.morseStr) < 1:
            hintText = ""
        else:
            hintText = "\t".join(
                [ h[1]+ "= " + h[0] for h in NearestHint(self.morseStr,pick_num=10)]
            )

        self.ShowHint.setText(hintText)



    def speak(self):
        if len(self.textStr) < 1:
            return
        #pytts_audioPlay(self.textStr)
        try:
            gTTS_audioPlay(self.textStr)
        except Exception as e:
            print(e)
            return

    def update(self) -> None:
        self.ShowText.setText(self.textStr)
        if len(self.morseStr) >= 16: self.morseStr = ""
        self.ShowMorse.setText(self.morseStr)
        self.showHint()
        if len(self.textStr) >= 1:
            try:
                self.ShowKanji.setText(jp_hira2kanji(convert_kata_to_hira(self.textStr)))
            except Exception as e:
                #print(e)
                self.ShowKanji.setText("- | -")
        self.gryoShow.repaint()


    def keyPressEvent(self, a0: QKeyEvent) -> None:
        if a0.key()== Qt.Key_A:
            self.MrsInput(1)
        if a0.key()== Qt.Key_D:
            self.MrsInput(2)
        if a0.key() == Qt.Key_W:
            self.MrsInput(0)
        self.update()

class controller:
    pass



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    #print(jp_hira2kanji("きょうはいいてんき"))

    app = QApplication(sys.argv)
    mainW = mainWindow(fontsize= app.primaryScreen().size().height() // 12 )
    mainW.showFullScreen()
    sys.exit(app.exec_())

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
