from PyQt5 import QtWidgets, QtGui, QtCore


class SearchListWidget(QtWidgets.QListWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

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
        # return self
