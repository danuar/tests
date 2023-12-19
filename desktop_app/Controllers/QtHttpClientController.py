from typing import Type, Optional

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QWindow
from PyQt5.QtWidgets import QWidget, QApplication, QFormLayout, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame, \
    QInputDialog, QMessageBox, QDialog

from ClientController import HttpClientController


class QtHttpClientController(HttpClientController):

    def handle_exception(self, e: BaseException, url: str, method: str, ResponseType: Type, request_body,
                         **query_params):
        widget = QDialog(parent=QApplication.instance().parent())
        widget.setWindowTitle("Возникла ошибка при запросе к серверу")

        label = QLabel(str(e))
        label.setWordWrap(True)

        form_layout = QFormLayout()
        form_layout.addRow("Url", QLabel(url))
        form_layout.addRow("Method", QLabel(method))
        form_layout.addRow("ResponseType", QLabel(ResponseType.__name__))
        form_layout.addRow("RequestBody", QLabel(str(request_body, wordWrap=True)))
        form_layout.addRow("QueryParams", QLabel(str(query_params)))
        form_layout.addRow("Exception", label)

        hlayout = QHBoxLayout()
        hlayout.setAlignment(Qt.AlignRight)
        hlayout.addWidget(QPushButton("Продолжить"))

        vlayout = QVBoxLayout()
        vlayout.addLayout(form_layout)
        vlayout.addLayout(hlayout)

        widget.setLayout(vlayout)
        widget.exec_()
