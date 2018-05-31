#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import requests
import json

from PyQt5 import QtWidgets, QtGui, QtCore, QtWebEngineWidgets
from SearchResultsList import SearchListWidget

class MainWidget(QtWidgets.QWidget):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.setGeometry(0,0,200,200)
            vBox = QtWidgets.QVBoxLayout(self)

            # self.resultList = QtWidgets.QListWidget(self)

            self.searchResult = SearchListWidget(self)
            # labels = []
            # images = []
            for item in self.search("Mord", film=True):
                self.searchResult.add_Element(item)
                # self.resultList.addItem(
                #     QtWidgets.QListWidgetItem(
                #         item['title']
                #     )
                # )
                # print(item)
                # labels.append(
                #     QtWidgets.QLabel(item['title'], self)
                # )
                # vBox.addWidget(labels[-1])
                # images.append(
                #     QtWidgets.QLabel()
                # )
                # images[-1].setPixmap(item['image'])
                # vBox.addWidget(images[-1])

            vBox.addWidget(self.searchResult)
            self.setLayout(vBox)
            self.show()

        def search(self, term, film=True, serie=True):
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
            # mimeType = "application/json; charset=utf-8"
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
                    yield {
                        'url': itemURL,
                        'title': item['formatTitle'],
                        'image': self.cover(imageurl),
                        'rawData': item
                    }
            else:
                yield None


        def cover(self, url):
            r = requests.get(url)
            pixmap = QtGui.QPixmap()
            if r.status_code == 200:
                pixmap.loadFromData(r.content, "JPG")
            return pixmap
            # <img
            #     src="//aiswatchbox-a.akamaihd.net/watchbox/format/15263_dvdcover/484x677/k-ein-bisschen-schwanger.jpg"
            #     aria-hidden="true"
            #     alt="(K)Ein bisschen schwanger"
            #     class=" text_image-alt-tag"
            #     itemprop="thumbnailUrl"
            #     srcset="//aiswatchbox-a.akamaihd.net/watchbox/format/15263_dvdcover/484x677/k-ein-bisschen-schwanger.jpg
            # 484w, //aiswatchbox-a.akamaihd.net/watchbox/format/15263_dvdcover/371x520/k-ein-bisschen-schwanger.jpg 371w,
            # //aiswatchbox-a.akamaihd.net/watchbox/format/15263_dvdcover/373x522/k-ein-bisschen-schwanger.jpg
            # 373w, //aiswatchbox-a.akamaihd.net/watchbox/format/15263_dvdcover/352x493/k-ein-bisschen-schwanger.jpg 352w"
            # >
# type                                               : film
# entityId                                           : 15887
# headline                                           : Hentai Kamen 2 - The Abnormal Crisis
# description                                        : Die Welt steht vor dramatischen Veränderungen: Täglich verschwinden immer mehr Damenhöschen von der Bildfläche! Für Kyosuke, den Superhelden Hentai Kamen, sind die Slips aber unabdingbar, denn nur mit einem Schlüpfer seiner Freundin Aiko über dem Gesicht kann er seine Superkräfte entfalten und die Welt vor allem Übel beschützen. Als Aiko ihre Höschen aufgrund der weltweiten Knappheit zurückfordert, wird es tragisch: Unbeabsichtigt verletzt Kyosuke Aikos Gefühle, nicht wissend, dass Tadashi Makoto, ein Klassenkamerad von Aiko, die Beziehung der beiden argwöhnisch beäugt. Ausgerechnet jetzt, wo er Aikos Zuneigung verliert und die Schlüpfer von der Erde weichen, trifft Hentai Kamen auf seinen größten Feind...
# fsk                                                : 16
# duration                                           : 01:53:07
# views                                              : {'last24Hours': 2, 'last7Days': 33, 'allTime': 298}
# productionCountry                                  : Japan
# productionYear                                     : 2016
# seoPath                                            : hentai-kamen-2-the-abnormal-crisis
# genres                                             : ['Action', 'Fantasy', 'Komödie', 'Asian']
# tags                                               : []Hentai
# createdAt                                          : {'date': '2018-03-01 00:00:00', 'timezone_type': 1, 'timezone': '+01:00'}
# active                                             : True
# rating                                             :
# onlineDate                                         : {'date': '2018-03-01 00:00:00', 'timezone_type': 1, 'timezone': '+01:00'}
# offlineDate                                        : {'date': '2019-12-31 23:59:59', 'timezone_type': 1, 'timezone': '+01:00'}
# season                                             : None
# episode                                            : None
# movieId                                            : 422590
# formatTitle                                        : Hentai Kamen 2 - The Abnormal Crisis
# teaserText                                         : None
# infoTextShort                                      : Fortsetzung der abgedrehten Superhelden-Geschichte mit Trash-Faktor.
# subHeadline                                        : None



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = MainWidget()
    sys.exit(app.exec_())
