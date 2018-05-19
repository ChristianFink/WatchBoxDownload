# -*- coding: utf-8 -*-

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
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.entry_URL = QtWidgets.QLineEdit(Form)
        self.entry_URL.setObjectName("entry_URL")
        self.horizontalLayout.addWidget(self.entry_URL)
        self.btn_Insert = QtWidgets.QPushButton(Form)
        self.btn_Insert.setObjectName("btn_Insert")
        self.horizontalLayout.addWidget(self.btn_Insert)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.list_URL = MovieListWidget(Form)
        self.list_URL.setObjectName("list_URL")
        self.verticalLayout.addWidget(self.list_URL)
        self.btn_Download = QtWidgets.QPushButton(Form)
        self.btn_Download.setObjectName("btn_Download")
        self.verticalLayout.addWidget(self.btn_Download)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)
        Form.setTabOrder(self.entry_URL, self.btn_Insert)
        Form.setTabOrder(self.btn_Insert, self.btn_Download)
        Form.setTabOrder(self.btn_Download, self.list_URL)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "WatchBox Download"))
        self.btn_Insert.setText(_translate("Form", "Hinzufügen"))
        self.btn_Download.setText(_translate("Form", "Download Starten"))

from MovieList import MovieListWidget
import resource_rc
