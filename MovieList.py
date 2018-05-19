#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# @Author: Christian Fink <christian>
# @Date:   2018-05-18T09:40:20+02:00
# @Email:  christian.fink@bluewin.ch
# @Last modified by:   christian
# @Last modified time: 2018-05-19T08:06:45+02:00

# import time
# import sys
# import os
import re
# import urllib2
# import requests
# from bs4 import BeautifulSoup
# import MySQLdb
from PyQt5 import QtWidgets, QtGui, QtCore
import requests
from bs4 import BeautifulSoup
import json
import youtube_dl


class DownloadThread(QtCore.QThread):

    download_progress = QtCore.pyqtSignal(float, str)
    download_end = QtCore.pyqtSignal()

    def __init__(self, url=None, destName=""):
        super().__init__()
        self.__ydl_opts = {
            'outtmpl': destName,
            'noplaylist': True,
            'quiet': True,
            'progress_hooks': [self.myHook]
        }
        self.url = url
        self.subClips = 2


    def __del__(self):
        self.wait()

    # def setData(self, url, destName):
    #     self.__ydl_opts['outtmpl'] = destName
    #     self.url = url
    #     self.subClips = 2

    def run(self):
        print("Thread wurde gestartet")
        with youtube_dl.YoutubeDL(self.__ydl_opts) as ydl:
            ydl.download([self.url])
        print("Thread wurde beendet")

    def myHook(self, d):
        if d['status'] == 'finished':
            self.subClips -= 1
            if self.subClips == 0:
                self.download_end.emit()
        elif d['status'] == "downloading":
            percent = float(d['_percent_str'][0:-1].strip())
            if 'video' in d['tmpfilename'][len(self.__ydl_opts['outtmpl'])-8:]:
                self.download_progress.emit(percent, 'video')
            else:
                self.download_progress.emit(percent, 'audio')
        else:
            print(50*"=")
            print(d)
            print(50*"=")


class MovieListWidget(QtWidgets.QListWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.MovieList = {}
        self.downloadActive = False
        self.__activeItem = None
        # self.__thread = DownloadThread()
        self.__thread = None


    @QtCore.pyqtSlot()
    def startDownload(self):
        if self.downloadActive:
            print("Download noch Aktiv")
            return False
        if self.count() == 0:
            print("Keine weitern Elemente vorhanden")
            return False

        self.downloadActive = True
        self.__activeItem = self.item(0)
        _data = self.__activeItem.dashLink

        self.__thread = DownloadThread(
            url=_data['dash'],
            destName=_data['destName']
        )

        self.__thread.download_end.connect(self.download_end)
        self.__thread.download_progress.connect(self.download_progress)

        self.__thread.start()

    @QtCore.pyqtSlot(float, str)
    def download_progress(self, progress, _type):
        if self.__activeItem:
            self.__activeItem.updateProgress(progress, _type)

    @QtCore.pyqtSlot()
    def download_end(self):
        print("Download beendet")
        self.takeItem(0)
        self.__activeItem = None
        self.downloadActive = False
        self.__thread.download_end.disconnect(self.download_end)
        self.__thread.download_progress.discconnect(self.download_progress)
        print(50*"=")
        print("Download neu starten")
        self.startDownload()

    def addURL(self, url):
        if url in self.MovieList:
            return False
        content = self.__getContent(url)
        if not content:
            return False

        if content['urlType'] == "film":
            self.MovieList[url] = {
                'url': url,
                'progress_video': 0.0,
                'progress_audio': 0.0,
                'destName': "",
                'title': "",
                'content': content,
                'image': None,
                'pixmap': None,
                'hls': content['hls'].replace("\\", ""),
                'dash': content['dash'].replace("\\", "")
            }
            self.MovieList[url]['image'] = content.get('image')
            self.MovieList[url]['destName'] = "{0}.%(ext)s".format(
                content.get('title')
            )
            self.MovieList[url]['title'] = content.get('title')
            if self.MovieList[url]['image']:
                r = requests.get(self.MovieList[url]['image'])
                if r.status_code == 200:
                    pixmap = QtGui.QPixmap()
                    pixmap.loadFromData(r.content, "JPG")
                    self.MovieList[url]['pixmap'] = pixmap
            self.__add_Element(self.MovieList[url])
        elif content['urlType'] == "serie":
            return False
        elif content['urlType'] == "season":
            return False
        elif content['urlType'] == "episode":
            self.MovieList[url] = {
                'url': url,
                'progress_video': 0.0,
                'progress_audio': 0.0,
                'destName': "",
                'title': "",
                'content': content,
                'image': None,
                'pixmap': None,
                'hls': content['hls'].replace("\\", ""),
                'dash': content['dash'].replace("\\", "")
            }
            self.MovieList[url]['image'] = content.get('image')
            title = "{0} - S{1:02d} E{2:02d} - {3}".format(
                content['serie']['title'],
                content['season'],
                content['episode'],
                content['episodeTitle']
            )
            self.MovieList[url]['destName'] = "{0}.%(ext)s".format(
                title
            )
            self.MovieList[url]['title'] = title
            if content['serie']['image']:
                r = requests.get(content['serie']['image'])
                if r.status_code == 200:
                    pixmap = QtGui.QPixmap()
                    pixmap.loadFromData(r.content, "JPG")
                    self.MovieList[url]['pixmap'] = pixmap
            self.__add_Element(self.MovieList[url])

        return True

    def __getContent(self, url):
        r = requests.get(url)
        details = {}
        if r.status_code != 200:
            return False
        soup = BeautifulSoup(r.text, 'html.parser')
        breadCrumb = url.split("/")[3:]
        details['contentType'] = breadCrumb[0]
        if details['contentType'] == "serien":
            """
                Listenlänge = 4 : Episode
                Listenlänge = 3 : Staffel
                Listenlänge = 2 : Serie
                Listenlänge = 1 : Ungültig
            """
            if len(breadCrumb) == 1:
                return False
            _l = ['http://watchbox.de', 'serien', breadCrumb[1]]
            if len(breadCrumb) == 2:
                """ Abfrage für Staffel und Episode erstellen """
                return False
                url_serie = url
                url_staffel = None
                url_episode = None

                details['urlType'] = "serie"
            elif len(breadCrumb) == 3:
                """ Abfrage für Episode erstellen """
                return False
                url_serie = "/".join(_l)
                url_staffel = url
                url_episode = None
                details['urlType'] = "season"
            elif len(breadCrumb) == 4:
                url_serie = "/".join(_l)
                _l.append(breadCrumb[2])
                url_staffel = "/".join(_l)
                url_episode = url
                m = re.search("-(\d*)\.html", url_episode)
                if m:
                    details['id_episode'] = int(m.group(1))
                    _ep = soup.find(
                        "a",
                        class_="teaserset__teaser",
                        attrs={'data-movie-id': str(details['id_episode'])}
                    )
                    if _ep:
                        _info = _ep.find("div", class_='teaser__season-info')
                        if _info:
                            m = re.search(
                                "Staffel (\d*), Episode (\d*)",
                                _info.text.replace("\n", "").strip()
                            )
                            if m:
                                details['season'] = int(m.group(1))
                                details['episode'] = int(m.group(2))
                        _header = _ep.find("div", class_="teaser__header")
                        if _header:
                            details['episodeTitle'] = _header.text.replace(
                                "\n", ""
                            ).strip()
                    details['urlType'] = "episode"
            details['serie'] = self.__getSerienContent(url_serie)

            # print("Serie    : {0}".format(url_serie))
            # print("Staffel  : {0}".format(url_staffel))
            # print("Episode  : {0}".format(url_episode))
        elif details['contentType'] == "filme":
            _image = soup.find("div", attrs={'class': "video-details__image"})
            if _image:
                _img = _image.find('img')
                if _img['src'].startswith("/"):
                    _img['src'] = "http:{0}".format(_img['src'])
                details['image'] = _img["src"]
                details['title'] = _img['alt']
                details['urlType'] = "film"
            #
            # EPISODEN BILD
            #     _image = soup.find("meta", attrs={'name': "twitter:image"})
            #     if _image:
            #         details['image'] = _image['content']
            #     _title = soup.find("meta", attrs={'name': "twitter:title"})
            #     if _title:
            #         details['title'] = _title['content'].replace(
            #             " im Online-Stream", ""
            #         )

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
        return details

    def __getSerienContent(self, url):
        r = requests.get(url)
        if r.status_code != 200:
            return None
        soup = BeautifulSoup(r.text, 'html.parser')
        details = {'seasons': []}
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
                    'title': season.text.replace("\n", "").strip()
                }
                for season in _seasons.find_all(
                    "li",
                    class_="season-panel__item"
                )
            ]
        return details

    def __add_Element(self, data):
        itemN = MovieListWidgetItem(data, self)
        self.addItem(itemN)
        self.setItemWidget(itemN, itemN.widget)

    def __add_Episode(self, data):
        pass

class MovieListWidgetItem(QtWidgets.QListWidgetItem):

    def __init__(self, data, parent=None):
        super().__init__()
        self.data = data
        self.widget = MovieListeWidgetItemWidget(self)
        self.setSizeHint(self.widget.sizeHint())

    @property
    def dashLink(self):
        return {
            'destName': self.data['destName'],
            'dash': self.data['dash'],
            'title': self.data['title']
        }

    @QtCore.pyqtSlot(float, str)
    def updateProgress(self, progress, _type):
        if _type == 'audio':
            self.data['progress_audio'] = progress
        else:
            self.data['progress_video'] = progress
        self.widget.updateProgress()


class MovieListeWidgetItemWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.setGeometry(0, 0, 300, 100)
        hLayout = QtWidgets.QHBoxLayout(self)
        vLayout = QtWidgets.QVBoxLayout()
        vLayout_progress = QtWidgets.QVBoxLayout()
        lbl_image = QtWidgets.QLabel(self)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed,
            QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(80)
        sizePolicy.setVerticalStretch(100)
        sizePolicy.setHeightForWidth(
            lbl_image.sizePolicy().hasHeightForWidth()
        )
        lbl_image.setSizePolicy(sizePolicy)
        lbl_image.setScaledContents(False)

        pixmap = self.parent.data.get('pixmap', None)
        if pixmap:
            lbl_image.setPixmap(pixmap.scaled(
                80, 80, QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation
            ))

        hLayout.addWidget(lbl_image)
        hLayout.addLayout(vLayout)

        self.progress_video = QtWidgets.QProgressBar(self)
        self.progress_video.setOrientation(QtCore.Qt.Horizontal)
        self.progress_video.setMaximum(100)

        self.progress_audio = QtWidgets.QProgressBar(self)
        self.progress_audio.setOrientation(QtCore.Qt.Horizontal)
        self.progress_audio.setMaximum(100)

        sizePolicy.setHorizontalStretch(80)
        sizePolicy.setVerticalStretch(30)
        sizePolicy.setHeightForWidth(
            self.progress_video.sizePolicy().hasHeightForWidth()
        )
        self.progress_video.setSizePolicy(sizePolicy)

        sizePolicy.setHeightForWidth(
            self.progress_audio.sizePolicy().hasHeightForWidth()
        )
        self.progress_audio.setSizePolicy(sizePolicy)

        hLayout.addLayout(vLayout_progress)

        vLayout_progress.addWidget(QtWidgets.QLabel("Video:"))
        vLayout_progress.addWidget(self.progress_video)
        vLayout_progress.addWidget(QtWidgets.QLabel("Audio:"))
        vLayout_progress.addWidget(self.progress_audio)

        # lbl_url = QtWidgets.QLabel(self.parent.data['url'])
        lbl_title = QtWidgets.QLabel(self.parent.data['title'])
        # lbl_hls = QtWidgets.QLabel(self.parent.data['hls'])
        # lbl_dash = QtWidgets.QLabel(self.parent.data['dash'])

        vLayout.addWidget(lbl_title)
        # vLayout.addWidget(lbl_url)
        # vLayout.addWidget(lbl_hls)
        # vLayout.addWidget(lbl_dash)

        self.setLayout(hLayout)

    @QtCore.pyqtSlot(float)
    def updateProgress(self):
        self.progress_video.setValue(self.parent.data['progress_video'])
        self.progress_audio.setValue(self.parent.data['progress_audio'])
