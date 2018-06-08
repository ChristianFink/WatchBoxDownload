# -*- coding: utf-8 -*-

# @Author: Christian Fink <christian>
# @Date:   2018-06-08T11:40:04+02:00
# @Email:  christian.fink@bluewin.ch
# @Last modified by:   christian
# @Last modified time: 2018-06-08T11:44:27+02:00

# Form implementation generated from reading ui file 'form.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(847, 462)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/icon"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Form.setWindowIcon(icon)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setContentsMargins(-1, 10, -1, -1)
        self.gridLayout.setObjectName("gridLayout")
        self.btn_Search = QtWidgets.QPushButton(Form)
        self.btn_Search.setObjectName("btn_Search")
        self.gridLayout.addWidget(self.btn_Search, 0, 2, 1, 1)
        self.btn_Insert = QtWidgets.QPushButton(Form)
        self.btn_Insert.setObjectName("btn_Insert")
        self.gridLayout.addWidget(self.btn_Insert, 1, 2, 1, 1)
        self.search = QtWidgets.QLineEdit(Form)
        self.search.setObjectName("search")
        self.gridLayout.addWidget(self.search, 0, 1, 1, 1)
        self.entry_URL = QtWidgets.QLineEdit(Form)
        self.entry_URL.setObjectName("entry_URL")
        self.gridLayout.addWidget(self.entry_URL, 1, 1, 1, 1)
        self.label = QtWidgets.QLabel(Form)
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.list_URL = MovieListWidget(Form)
        self.list_URL.setObjectName("list_URL")
        self.verticalLayout.addWidget(self.list_URL)
        self.btn_Download = QtWidgets.QPushButton(Form)
        self.btn_Download.setObjectName("btn_Download")
        self.verticalLayout.addWidget(self.btn_Download)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)
        Form.setTabOrder(self.btn_Download, self.list_URL)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "WatchBox Download"))
        self.btn_Search.setText(_translate("Form", "Suchen"))
        self.btn_Insert.setText(_translate("Form", "Hinzufügen"))
        self.label.setText(_translate("Form", "Suchbegriff: "))
        self.label_2.setText(_translate("Form", "URL: "))
        self.btn_Download.setText(_translate("Form", "Download Starten"))

from .MovieList import MovieListWidget
from . import resource_rc
