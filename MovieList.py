#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# @Author: Christian Fink <christian>
# @Date:   2018-05-18T09:40:20+02:00
# @Email:  christian.fink@bluewin.ch
# @Last modified by:   christian
# @Last modified time: 2018-05-19T12:43:31+02:00

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
            'progress_hooks': [self.myHook],
            'prefer-ffmpeg': True
        }
        self.url = url
        self.subClips = 2


    def __del__(self):
        self.wait()

    def run(self):
        with youtube_dl.YoutubeDL(self.__ydl_opts) as ydl:
            ydl.download([self.url])

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
        self.__thread = None

    @QtCore.pyqtSlot()
    def startDownload(self):
        if self.downloadActive:
            return False
        if self.count() == 0:
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
        self.takeItem(0)
        self.__activeItem = None
        self.downloadActive = False
        self.__thread.download_end.disconnect(self.download_end)
        self.__thread.download_progress.disconnect(self.download_progress)
        self.startDownload()

    def addURL(self, data):
        # for data in self.__mainContent(url):
        if data['url'] in self.MovieList:
            return False
        pixmap = QtGui.QPixmap()
        r = requests.get(data['image'])
        if r.status_code == 200:
            pixmap.loadFromData(r.content, "JPG")
        self.MovieList[data['url']] = {
            'url': data['url'],
            'progress_video': 0.0,
            'progress_audio': 0.0,
            'destName': "{0}.%(ext)s".format(data['title']),
            'title': data['title'],
            'content': data['contentType'],
            'image': data['image'],
            'pixmap': pixmap,
            'hls': data['hls'],
            'dash': data['dash']
        }
        self.__add_Element(self.MovieList[data['url']])
        return True

    def __add_Element(self, data):
        itemN = MovieListWidgetItem(data, self)
        self.addItem(itemN)
        self.setItemWidget(itemN, itemN.widget)

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
