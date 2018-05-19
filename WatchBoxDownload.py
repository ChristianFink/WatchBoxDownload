#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# @Author: Christian Fink <christian>
# @Date:   2018-05-18T08:45:21+02:00
# @Email:  christian.fink@bluewin.ch
# @Last modified by:   christian
# @Last modified time: 2018-05-18T17:15:18+02:00

# import time
# import sys
# import os
# import re
# import urllib2
import os
import sys
from PyQt5 import QtWidgets, QtGui, QtCore
import gi
from gi.repository import GObject
from formular_ui import Ui_Form



class MainWidget(QtWidgets.QWidget):

    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.ui.btn_Insert.clicked.connect(self._insert)
        self.ui.btn_Download.clicked.connect(self._startDownload)
        self.show()
        self.ui.entry_URL.setText("https://www.watchbox.de/serien/yosuga-no-sora-15375/staffel-1/zurueck-in-die-vergangenheit-373928.html")

    @QtCore.pyqtSlot()
    def _insert(self):
        url = self.ui.entry_URL.text()
        success = self.ui.list_URL.addURL(url)
        if not success:
            print("URL \"{0}\" existert bereits".format(url))
        self.ui.entry_URL.setText("")

    @QtCore.pyqtSlot()
    def _startDownload(self):
        a = self.ui.list_URL.startDownload()
        print(a)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = MainWidget(app)
    sys.exit(app.exec_())
