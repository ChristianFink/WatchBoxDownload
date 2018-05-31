#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import requests
from bs4 import BeautifulSoup as bs


from PyQt5 import QtWidgets, QtGui, QtCore, QtWebEngineWidgets

# form-field__input
# search__input
# js-search-input


# url:"https://api.watchbox.de/v1/search/",
# data:n,
# mimeType:"application/json; charset=utf-8",
# method:"GET",
# crossDomain:!0,
# beforeSend:function(){
# i.addClass("loading-slider_show")

class MainWidget(QtWidgets.QWidget):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            vBox = QtWidgets.QVBoxLayout(self)
            self.entry = QtWidgets.QLineEdit(self)
            self.entry.setObjectName("entry")

            webPage = QtWebEngineWidgets.QWebEngineView()
            webPage.setObjectName("web")

            vBox.addWidget(self.entry)
            vBox.addWidget(webPage)
            self.setLayout(vBox)

            QtCore.QMetaObject.connectSlotsByName(self)
            self.show()

            webPage.load(QtCore.QUrl("http://watchbox.de"))

# js-search-result-grid

        def on_web_loadFinished(self, result):
            print("Seite geladen : {0}".format(result))

        def on_web_showEvent(self, event):
            print("Event : {0}".format(event))

        def on_web_selectionChanged(self):
            print("Auswahl geändert")

            print(self.webPage.selectedText())

        def on_web_urlChanged(self, url):
            print("Neue URL : {0}".format(url))


        def on_entry_editingFinished(self):
            print(
                "== {0}".format(
                    self.entry.text()
                )
            )

        def analyse(self, request):
            soup = bs(request.text, 'lxml')

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = MainWidget()
    sys.exit(app.exec_())
