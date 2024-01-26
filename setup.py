from distutils.core import setup # Need this to handle modules
import py2exe
import math # We have to import all modules used in our program

#setup(windows=['morse-ui-round.py'])
setup(windows=[{"script" : "morse-ui-round.py"}],
options={"py2exe" : {'compressed': True, "includes" : ["sip",
            "PyQt5",
            "PyQt5.QtWidgets",
            "PyQt5.QtCore",
            "PyQt5.QtGui",
                                                       "gtts","pydub","os","sys"]
         }
})