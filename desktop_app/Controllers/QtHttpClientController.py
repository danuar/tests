from typing import Type

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QFormLayout, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QDialog

from ClientController import HttpClientController


class QtHttpClientController(HttpClientController):

    def handle_exception(self, e: BaseException, url: str, method: str, ResponseType: Type, request_body,
                         **query_params):
        widget = QDialog(parent=QApplication.instance().parent())
        widget.setWindowTitle("Возникла ошибка при запросе к серверу")

        label = QLabel(str(e))
        label.setWordWrap(True)
        label_request_body = QLabel(str(request_body))
        label_request_body.setWordWrap(True)

        form_layout = QFormLayout()
        form_layout.addRow("Url", QLabel(url))
        form_layout.addRow("Method", QLabel(method))
        form_layout.addRow("ResponseType", QLabel(ResponseType.__name__))
        form_layout.addRow("RequestBody", label_request_body)
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
