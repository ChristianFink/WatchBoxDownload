#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# @Author: Christian Fink <christian>
# @Date:   2018-05-31T17:33:08+02:00
# @Email:  christian.fink@bluewin.ch
# @Last modified by:   christian
# @Last modified time: 2018-06-08T11:41:41+02:00
#
# Widget zur Darstellung der Suchergebnisse
#

from PyQt5 import QtWidgets, QtGui, QtCore


class SearchListWidget(QtWidgets.QListWidget):

    newSelection = QtCore.pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.itemDoubleClicked.connect(self._change)

    @QtCore.pyqtSlot(QtWidgets.QListWidgetItem)
    def _change(self):
        _items = self.selectedItems()
        if not _items:
            return None
        self.newSelection.emit(_items[0].data)

    def add_Element(self, data):
        itemN = SearchListWidgetItem(data, self)
        self.addItem(itemN)
        self.setItemWidget(itemN, itemN.widget)


class SearchListWidgetItem(QtWidgets.QListWidgetItem):

    def __init__(self, data, parent=None):
        super().__init__()
        self.data = data
        self.widget = SearchListWidgetItemWidget(self)
        self.setSizeHint(self.widget.sizeHint())


class SearchListWidgetItemWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent.data
        self.setGeometry(0, 0, 400, 100)
        hBox = QtWidgets.QHBoxLayout(self)
        label = QtWidgets.QLabel(self.parent['title'], self)
        image = QtWidgets.QLabel(self)
        image.setPixmap(self.parent['image'].scaled(
            100, 100, QtCore.Qt.KeepAspectRatio, QtCore.Qt.FastTransformation
        ))

        hBox.addWidget(image)
        hBox.addWidget(label)
        self.setLayout(hBox)
