#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# @Author: Christian Fink <christian>
# @Date:   2018-05-18T08:45:21+02:00
# @Email:  christian.fink@bluewin.ch
# @Last modified by:   christian
# @Last modified time: 2018-06-08T11:43:03+02:00
#
#
#


import os
import sys
from PyQt5 import QtWidgets, QtGui, QtCore
import gi
from gi.repository import GObject
import requests
from bs4 import BeautifulSoup
import json
import re
from res.formular_ui import Ui_Form
from res.SearchDialog import SEARCHDIALOG


class MainWidget(QtWidgets.QWidget):

    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.searchDialog = SEARCHDIALOG()
        self.searchDialog.newElement.connect(self._insertElement)

        self.ui.btn_Insert.clicked.connect(self._insert)
        self.ui.btn_Search.clicked.connect(self._search)
        self.ui.btn_Download.clicked.connect(self._startDownload)

        self.show()

    @QtCore.pyqtSlot()
    def _search(self):
        _term = self.ui.search.text()
        if _term != "":
            self.searchDialog.search(_term)
            self.searchDialog.show()

    @QtCore.pyqtSlot(str)
    def _insertElement(self, url):
        for data in self.__mainContent(url):
            success = self.ui.list_URL.addURL(data)
            print("{0} : {1}".format(data['title'], success))
        self.ui.entry_URL.setText("")

    @QtCore.pyqtSlot()
    def _insert(self):
        url = self.ui.entry_URL.text()
        for data in self.__mainContent(url):
            success = self.ui.list_URL.addURL(data)
            print("{0} : {1}".format(data['title'], success))
        self.ui.entry_URL.setText("")

    @QtCore.pyqtSlot()
    def _startDownload(self):
        self.ui.list_URL.startDownload()

    def __mainContent(self, url):
        if url.endswith("/"):
            url = url[0:-1]
        breadCrumb = url.split("/")[3:]
        details = {
            'contentType': breadCrumb[0],
            'url': url
        }
        r = requests.get(url)
        if r.status_code != 200:
            return False
        soup = BeautifulSoup(r.text, 'html.parser')

        _image = soup.find("div", attrs={'class': "video-details__image"})
        if _image:
            _img = _image.find('img')
            if _img['src'].startswith("/"):
                _img['src'] = "http:{0}".format(_img['src'])
                details['image'] = _img["src"]
                details['title'] = _img['alt']

                if details['contentType'] == "filme":
                    details['destName'] = "{0}.%(ext)s".format(
                        details['title']
                    )
        _dataAsset = soup.find("div", class_="big-teaser-video")
        if _dataAsset:
            details['data-asset-id'] = _dataAsset['data-asset-id']

        for _js in soup.find_all('script', attrs={'type': 'text/javascript'}):
            if _js.get("src", None):
                continue
            m = re.search("var playerConf = ({.*);", _js.text)
            if not m:
                continue
            playerConf = json.loads(m.group(1))
            details['hls'] = playerConf['source']['hls']
            details['dash'] = playerConf['source']['dash']
            break

        if details['contentType'] == "filme":
            yield details
        elif details['contentType'] == "serien":
            _SerienURL = ['http://watchbox.de', 'serien', breadCrumb[1]]
            if 'dash' in details:
                """
                url war Episode
                Serientitel, Bild und Episodentitel ermitteln
                """
                serien_content = self.__serienContent("/".join(_SerienURL))
                episoden_content = self.__episodeContent(url, soup)
                details['title'] = "{0} - S{1:02d} E{2:02d} - {3}".format(
                    serien_content['title'],
                    episoden_content['season'],
                    episoden_content['episode'],
                    episoden_content['episodeTitle']
                )
                details['image'] = serien_content['image']
                yield details
            else:
                """
                url war Staffel oder Serie
                Staffelinhalt oder Serieninhalt ermitteln
                und alle Episoden zurückgeben
                """
                serien_content = self.__serienContent(url)
                if len(breadCrumb) == 2:
                    for season in serien_content['seasons']:
                        for episode in self.__staffelContent(
                            season['url'],
                            details['data-asset-id']
                        ):
                            episoden_content = self.__episodeContent(episode['url'])
                            yield {
                                'url': episode['url'],
                                'contentType': 'serien',
                                'hls': episoden_content['hls'],
                                'dash': episoden_content['dash'],
                                'title': "{0} - S{1:02d} E{2:02d} - {3}".format(
                                    serien_content['title'],
                                    episoden_content['season'],
                                    episoden_content['episode'],
                                    episoden_content['episodeTitle']
                                ),
                                'image': serien_content['image']
                            }
                elif len(breadCrumb) == 3:
                    staffelContent = self.__staffelContent(
                        url,
                        details['data-asset-id'],
                        soup
                    )
                    for episode in staffelContent:
                        episoden_content = self.__episodeContent(episode['url'])
                        yield {
                            'url': episode['url'],
                            'contentType': 'serien',
                            'hls': episoden_content['hls'],
                            'dash': episoden_content['dash'],
                            'title': "{0} - S{1:02d} E{2:02d} - {3}".format(
                                serien_content['title'],
                                episoden_content['season'],
                                episoden_content['episode'],
                                episoden_content['episodeTitle']
                            ),
                            'image': serien_content['image']
                        }

    def __staffelContent(self, url, assetID, soup=None):
        episoden = []
        if soup is None:
            if url is None:
                return None
            r = requests.get(url)
            if r.status_code != 200:
                print("FEHLER : {0}".format(r.status_code))
                return None
            soup = BeautifulSoup(r.text, 'html.parser')
        for _ep in soup.find_all(
            "a",
            class_="teaserset__teaser",
            attrs={'data-asset-id': assetID}
        ):
            url = "http://www.watchbox.de{0}".format(_ep['href'])
            _info = _ep.find("div", class_='teaser__season-info')
            if _info:
                m = re.search(
                    "Staffel (\d*), Episode (\d*)",
                    _info.text.replace("\n", "").strip()
                )
                if m:
                    season = int(m.group(1))
                    episode = int(m.group(2))
            _header = _ep.find("div", class_="teaser__header")
            if _header:
                episodeTitle = _header.text.replace(
                    "\n", ""
                ).strip()
            episoden.append({
                'season': season,
                'episode': episode,
                'episodeTitle': episodeTitle,
                'url': url
            })
        return episoden

    def __serienContent(self, url):
        r = requests.get(url)
        if r.status_code != 200:
            return None
        soup = BeautifulSoup(r.text, 'html.parser')
        dataAssetID = soup.find(
            "div",
            class_="big-teaser-video"
        )['data-asset-id']
        details = {'data-asset-id': dataAssetID, 'seasons': []}
        _image = soup.find("div", attrs={'class': "video-details__image"})
        if _image:
            _img = _image.find('img')
            if _img['src'].startswith("/"):
                _img['src'] = "http:{0}".format(_img['src'])
            details['image'] = _img["src"]
            details['title'] = _img['alt']

        _seasons = soup.find('ul', class_="season-panel")
        if _seasons:
            details['seasons'] = [
                {
                    'nr': int(season['data-season-number']),
                    'title': season.text.replace("\n", "").strip(),
                    'url': "http://watchbox.de{0}".format(
                        season.find('a')['href']
                    )
                }
                for season in _seasons.find_all(
                    "li",
                    class_="season-panel__item"
                )
            ]
        return details

    def __episodeContent(self, url, soup=None):
        if soup is None:
            if url is None:
                return None
            r = requests.get(url)
            if r.status_code != 200:
                return None
            soup = BeautifulSoup(r.text, 'html.parser')
        m = re.search("-(\d*)\.html", url)
        if m:
            id_episode = int(m.group(1))
            _ep = soup.find(
                "a",
                class_="teaserset__teaser",
                attrs={'data-movie-id': str(id_episode)}
            )
            if _ep:
                _info = _ep.find("div", class_='teaser__season-info')
                if _info:
                    m = re.search(
                        "Staffel (\d*), Episode (\d*)",
                        _info.text.replace("\n", "").strip()
                    )
                    if m:
                        season = int(m.group(1))
                        episode = int(m.group(2))
                _header = _ep.find("div", class_="teaser__header")
                if _header:
                    episodeTitle = _header.text.replace(
                        "\n", ""
                    ).strip()
        for _js in soup.find_all('script', attrs={'type': 'text/javascript'}):
            if _js.get("src", None):
                continue
            m = re.search("var playerConf = ({.*);", _js.text)
            if not m:
                continue
            playerConf = json.loads(m.group(1))
            hls = playerConf['source']['hls']
            dash = playerConf['source']['dash']
            break

        return {
            'season': season,
            'episode': episode,
            'episodeTitle': episodeTitle,
            'hls': hls,
            'dash': dash
        }


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = MainWidget(app)
    sys.exit(app.exec_())
