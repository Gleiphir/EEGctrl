# Used for Linux on Raspi

import math
import re

from PyQt5.QtWidgets import QApplication, \
    QWidget, QMainWindow, QMessageBox, \
    QFileDialog, QPushButton, QLabel, \
    QGridLayout, QLineEdit, QFrame, QProgressBar,QSizePolicy, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import *
from PyQt5.QtCore import QTimer,Qt, QRect,QRectF,pyqtSignal,pyqtSlot,QLineF
import sys
from PyQt5 import QtGui
from io import BytesIO
import gtts

from pydub import AudioSegment
from pydub.playback import play
import os
os.environ['TMPDIR'] = os.getcwd()
#import urllib,json

takutennMap = {
    "か゛":"が",
    "き゛":"ぎ",
    "く゛":"ぐ",
    "け゛":"げ",
    "こ゛":"ご",#たちつてと
    "さ゛":"ざ",
    "し゛":"じ",
    "す゛":"ず",
    "せ゛":"ぜ",
    "そ゛":"ぞ",
    "た゛":"だ",
    "ち゛":"ぢ",
    "つ゛":"づ",
    "て゛":"で",
    "と゛":"ど",
    "は゛":"ば",
    "ひ゛":"び",
    "ふ゛":"ぶ",
    "へ゛":"べ",
    "ほ゛":"ぼ",
    "はﾟ": "ぱ",
    "ひﾟ":"ぴ",
    "ふﾟ":"ぷ",
    "へﾟ":"ぺ",
    "ほﾟ":"ぽ",



}


lvl1Dict = {
    '機':['入','〇','✖','礼','消','疲','←'],
    'あ':['あ','い','う','え','お'],
    'か':['か','き','く','け','こ'],
    'さ':['さ','し','す','せ','そ'],
    'た':['た','ち','つ','て','と'],
    'な':['な','に','ぬ','ね','の'],
    'は':['は','ひ','ふ','へ','ほ'],
    'ま':['ま','み','む','め','も'],
    'や':['や','ゃ','ゆ','ゅ','よ','ょ'],
    'ら':['ら','り','る','れ','ろ'],
    'わ':['わ','っ','ん'],
    '点':['゛','ﾟ','ー'],
}


WHEEL_MAX = 8

class NaviSys:
    """
    Serves as a hook for future updates
    like sending to server, bkg Thread et cetera
    """
    sendStr = pyqtSignal(str) # Send to text UI
    sendFnSig = pyqtSignal(str) # Functional
    # TODO : detach FnSig and make NaviSys judge
    currentList =[]
    index = 0
    def __init__(self):
        self.currentList = [key for key in lvl1Dict.keys()]

    def lookUp(self,chr:str,lvl:int):
        """
        :param chr: str title showed on wheel UI
        :param lvl: 1 or 0, 1 for choose category, 0 for base operation, 2 for super operation(flip).
        :return: New list to display on wheel UI
        """
        choice = None
        res = []
        # if lvl != 1 always make ('↑',0,"戻る") 1st
        if lvl == 0:
            if chr != '↑':
                #self.sendStr.emit(chr)
                choice = chr

            self.currentList = [key for key in lvl1Dict.keys()]  # reload
            if len(self.currentList) <= self.index + WHEEL_MAX - 1 :
                res.extend(self.currentList)
                self.index =0
                return res,1,choice # res & lvl


            res.extend(self.currentList[self.index:WHEEL_MAX - 1])
            self.index += WHEEL_MAX - 1
            return res, 1,choice

        if lvl > 0 : # 1 for now ,will enter lvl 0 , with backwards Btn

            self.currentList = lvl1Dict[chr]
            self.index = 0
            res.extend(lvl1Dict[chr])
            return res, 0,choice

    def Nextpage(self): #ignore lvl, len(res) <= WHEEL_MAX - 1
        res =[]
        if len(self.currentList) <= self.index + WHEEL_MAX - 1 :

            res = self.currentList[self.index : ]
            self.index = 0
            return res
        else:
            res.extend(self.currentList[self.index : self.index + WHEEL_MAX -1  ])
            self.index+= WHEEL_MAX -1
            return res


INPUT_SUSPEND_WINDOW_MS = 2000

crcl = lambda x: 16 * 360 + x if x < 0 else x % (16 * 360)

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

"""
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
"""
def gTTS_audioPlay(text:str):
    with BytesIO() as f:
        gtts.gTTS(text=text, lang='ja').write_to_fp(f)
        f.seek(0)
        song = AudioSegment.from_file(f, format="mp3")
        play(song)

validColor = QColor(78 ,238 ,148)
bkgColor = QColor(255 ,193 ,193)
markColor = QColor(0, 0, 128,)
edgeColor = QColor(0, 0, 0,)
rollingColor = QColor(127, 0, 0,)

POINTER_WIDTH = 300
MAIN_FONT_SIZE = 50
HINT_FONT_SIZE = 25

WHEEL_SIZE = 900
CENTER_SIZE = 250
ROLL_SPEED = 20 # 2pi/5760 per update
class RoundWheel(QLabel):
    sendStr = pyqtSignal(str)
    def __init__(self, parent=None):
        QLabel.__init__(self, parent)
        self._pos = 300 # int : 0 -> 16 * 360 =5760
        self.level = 1

        self.NS = NaviSys()
        self.optList = []

        self.textFont = QFont('monospace',MAIN_FONT_SIZE)
        self.textFont.setBold(True)
        self.hintFont = QFont('monospace', HINT_FONT_SIZE)


        self.setFixedHeight(900)
        self.area = None
        self.centerArea =None

    def init(self):
        self.area = QRectF(0.0,0.0,900.0,900.0)
        self.centerArea = QRectF(
            self.area.x() + self.area.width() /2 - CENTER_SIZE /2,
            self.area.y() + self.area.height() / 2 - CENTER_SIZE /2,
            CENTER_SIZE,
            CENTER_SIZE
        )
        self.optList = [key for key in lvl1Dict][:WHEEL_MAX-1]

    def setPos(self,gpos:float):
        self._pos = gpos

    def addPos(self):
        self._pos =  crcl(self._pos + ROLL_SPEED)

    def setrange(self,new_range,gpos,widgetpos = None):
        assert len(new_range) ==6
        assert len(gpos) ==6
        if widgetpos:
            self._widgetpos = widgetpos
        self._range = new_range
        self.gyropos =gpos

    def updateList(self,lst:list):
        self.optList = lst.copy()

    def getCurrentOpt(self):
        N = len(self.optList)
        Nth = math.floor(self._pos / (16 * 360 / N))
        return Nth,N,self.optList[Nth]


    def navigate(self):

        N = len(self.optList)
        Nth = math.floor(self._pos / (16 * 360 / N))
        self.optList, self.level, choice = self.NS.lookUp(self.optList[Nth],self.level)
        if self.level ==0:
            self.optList.insert(0,'↑')
        #print(self.optList, self.NS.index, '/', self.NS.currentList)
        #print(self.level)
        self._pos = 0
        if choice:
            self.sendStr.emit(choice)
        #return Nth, N, self.optList[Nth]

    def nextPage(self):
        self.optList = self.NS.Nextpage()
        if self.level ==0:
            self.optList.insert(0,'↑')

    def paintEvent(self, event):
        #print("painters init")

        bkgPtr = QPainter(self)
        bkgPtr.setBrush(bkgColor)
        bkgPtr.setPen(Qt.NoPen)

        N = len(self.optList)
        Nth = math.floor( self._pos / ( 16 * 360 / N) )

        bkgPtr.fillRect(
            self.area,
            bkgColor
        )

        nonpickPtr = QPainter(self)
        nonpickPtr.setBrush(Qt.darkGray)
        nonpickPtr.setPen(Qt.NoPen)
        nonpickPtr.drawEllipse(self.area)

        pickPtr = QPainter(self)
        pickPtr.setBrush(validColor)
        pickPtr.setPen(Qt.NoPen)

        pickPtr.drawPie(self.area,
                             int( 16* 360 / N * Nth),
                             int( 16* 360 / N )
                             )

        edgePtr = QPainter(self)
        edgePtr.setBrush(Qt.NoBrush)
        edgePtr.setPen(QtGui.QPen(Qt.white, 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

        for i in range(N):
            edgePtr.drawLine(QLineF(450.0, 450.0, 450 * (1 + math.cos(2 * math.pi * i / N)), 450 * (1 - math.sin(2 * math.pi * i / N)) ))

        rollingPtr = QPainter(self)
        rollingPtr.setBrush(rollingColor)
        rollingPtr.setPen(QtGui.QPen(Qt.red, 5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        rollingPtr.drawArc(self.area, crcl(self._pos - POINTER_WIDTH // 2), POINTER_WIDTH)

        rollingPtr.drawPie(self.centerArea,
                           int(16 * 360 / N * Nth),
                           int(16 * 360 / N)
                           )

        textPtr = QPainter(self)
        textPtr.setBrush(Qt.white)
        textPtr.setPen(QtGui.QPen(Qt.black, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

        for i in range(N):
            textpath = QPainterPath()
            textpath.addText( 450 + 350 * (math.cos(2 * math.pi * (i+ 0.5) / N)),450 - 350 * ( math.sin(2 * math.pi * (i+ 0.5)  / N)) ,self.textFont , self.optList[i][0] )
            textPtr.drawPath(textpath)

        subtextPtr = QPainter(self)
        subtextPtr.setBrush(Qt.blue)
        subtextPtr.setPen(Qt.NoPen)
        """
        for i in range(N):
                hintpath = QPainterPath()
                hintpath.addText(450 + 350 * (math.cos(2 * math.pi * (i + 0.5) / N)),
                                 450 + MAIN_FONT_SIZE - 350 * (math.sin(2 * math.pi * (i + 0.5) / N)), self.hintFont,
                                 self.optList[i][2])
                subtextPtr.drawPath(hintpath)
        """


    #print(":::: {}".format(self.area.x() // 2 + int(self.area.width() * self.gyropos / 90.0)))
    @property
    def pos(self):
        return self._pos


class TriggerFrame(QFrame):
    inputSig = pyqtSignal(int)

    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        "L = . | Q = -"
        #print(a0.key())
        if a0.key() == Qt.Key_L:
            self.inputSig.emit(1)
        elif a0.key() == Qt.Key_Q:
            self.inputSig.emit(2)

class mainWindow (QMainWindow):
    def __init__(self,fontsize=40):
        super().__init__()
        self.setObjectName("MainW")
        self.setFont(QFont('microsoft Yahei'))
        self.setWindowTitle('UI')
        #self.setWindowOpacity(0.7)
        self.mainFrame = TriggerFrame(self)
        self.mainFrame.setStyleSheet("font-size:{}px".format(fontsize))

        self.roundUI = RoundWheel(self)
        self.roundUI.init()
        self.roundUI.sendStr.connect(self.addCharWFunc)

        self.setCentralWidget(self.mainFrame)
        self.lout = QHBoxLayout(self)
        self.lout.setSpacing(30)


        self.lout.addWidget(self.roundUI)

        self.ShowText = QLabel("text", self)
        self.ShowText.setObjectName("ShowText")
        self.ShowText.setStyleSheet("background-color:#E0E0C0")
        self.ShowText.setWordWrap(True)
        self.ShowText.setFixedWidth(700)



        self.lout.addWidget(self.ShowText)



        self.setGeometry(100, 100, 1000, 1000)

        try:
            qss = open("StyleSheet.qss").read()
            self.setStyleSheet(qss)
        except:
            print("Qss not loaded")

        #self.suspendTimer.timeout.connect()

        self.setFont(QFont('microsoft Yahei', self.size().height() // 6))
        grid = QGridLayout()
        grid.setSpacing(5)

        self.mainFrame.setLayout(self.lout)

        self.textStr = ""

        self.mainFrame.inputSig.connect(self.BinaryInput)
        """
        self.defaultOPTimer = QTimer(self)
        self.defaultOPTimer.timeout.connect(lambda : self.MrsInput(0))
        self.defaultOPTimer.start(INPUT_SUSPEND_WINDOW_MS)
        """

        self.autoUpdateTimer  = QTimer(self)
        self.autoUpdateTimer.timeout.connect(self.UIrefresh)
        self.autoUpdateTimer.start(20)

        #self.serialInit()


    @pyqtSlot(int)
    def BinaryInput(self, sig:int):

        """ 0 = / ; 1 = . ; 2 = - ;  """
        if sig == 0:
            pass
        elif sig == 1:
            self.roundUI.navigate()
            #N,Nth,target = self.roundUI.getCurrentOpt()
            #self.textStr += target[0]
        elif sig == 2:
            self.roundUI.nextPage()

            #self.morseStr = self.morseStr + '－'
        else:
            pass
        self.update()

    @pyqtSlot()
    def UIrefresh(self):
        self.roundUI.addPos()
        self.roundUI.update()
        #print(self.roundUI.pos)
        self.update()


    @pyqtSlot(str)
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
        if chr == '礼':
            self.textStr = "ありがとうございます"
            self.speak()
            self.clearText()
            return
        if chr == '〇':
            self.textStr = "はい、そうです"
            self.speak()
            self.clearText()
            return
        if chr == '✖':
            self.textStr = "いいえ、違います"
            self.speak()
            self.clearText()
            return
        if chr == '呼':
            self.textStr = "介護者を呼んでください"
            self.speak()
            self.clearText()
            return
        if chr == '疲':
            self.textStr = "疲れたのです"
            self.speak()
            self.clearText()
            return

        self.textStr = self.textStr + chr
        if '' in self.textStr or '' in self.textStr:
            for key in takutennMap:
                self.textStr = re.sub(key, takutennMap[key],self.textStr)
        #self.textStr = self.textStr.translate(str.maketrans(takutennMap))

    def clearText(self):
        self.textStr = ""
        #self.morseStr = ""
        #self.ShowHint.setText("")
        self.update()


    def showHint(self):
        pass



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




    def keyPressEvent(self, a0: QKeyEvent) -> None:
        if a0.key()== Qt.Key_L:
            self.BinaryInput(1)

        if a0.key()== Qt.Key_Q:
            self.BinaryInput(2)

        if a0.key() == Qt.Key_W:
            self.BinaryInput(0)
        #self.defaultOPTimer.start(INPUT_SUSPEND_WINDOW_MS)
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
