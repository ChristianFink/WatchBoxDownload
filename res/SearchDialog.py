#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# @Author: Christian Fink <christian>
# @Date:   2018-05-31T17:33:08+02:00
# @Email:  christian.fink@bluewin.ch
# @Last modified by:   christian
# @Last modified time: 2018-06-08T11:45:23+02:00

import sys
import requests
import json

from PyQt5 import QtWidgets, QtGui, QtCore, QtWebEngineWidgets
from .SearchResultsList import SearchListWidget


class SEARCHDIALOG(QtWidgets.QWidget):

    newElement = QtCore.pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setGeometry(0, 0, 500, 600)
        vBox = QtWidgets.QVBoxLayout(self)
        self.searchResult = SearchListWidget(self)
        self.searchResult.newSelection.connect(self._newSelection)
        vBox.addWidget(self.searchResult)
        self.setLayout(vBox)

    @QtCore.pyqtSlot(dict)
    def _newSelection(self, item):
        self.newElement.emit(item['url'])

    def search(self, term, film=True, serie=True):
        self.searchResult.clear()
        _types = []
        if film:
            _types.append("film")
        if serie:
            _types.append("serie")

        _strTypes = ", ".join(
            '"{0}"'.format(x) for x in _types
        )

        payload = {
            'active': "true",
            'maxPerPage': 28,
            'page': 1,
            'term': term,
            'types': '[{0}]'.format(_strTypes)
        }

        url = "https://api.watchbox.de/v1/search/"
        r = requests.get(url, params=payload)
        urlBase = "https://www.watchbox.de/{0}/{1}-{2}/"

        if r.status_code == 200:
            data = r.json()
            for item in data['items']:
                itemURL = urlBase.format(
                    "filme" if item['type'] == "film" else "serien",
                    item['seoPath'],
                    item['entityId']
                )
                print("{0} {1} [{2}]".format(
                    "*" if item["active"] else " ",
                    item["formatTitle"],
                    itemURL
                ))
                imageurl = "http://aiswatchbox-a.akamaihd.net/watchbox/format/{0}_dvdcover/484x677/{1}.jpg".format(
                    item['entityId'],
                    item['seoPath']
                )
                data = {
                    'url': itemURL,
                    'title': item['formatTitle'],
                    'image': self.cover(imageurl),
                    'rawData': item
                }
                self.searchResult.add_Element(data)
        else:
            return None
            # yield None

    def cover(self, url):
        r = requests.get(url)
        pixmap = QtGui.QPixmap()
        if r.status_code == 200:
            pixmap.loadFromData(r.content, "JPG")
        return pixmap
