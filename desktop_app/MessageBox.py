from PyQt5.QtWidgets import QMessageBox


def show_msg_information(title: str, text: str):
    msg = QMessageBox()
    msg.setWindowTitle(title)
    msg.setIcon(QMessageBox.Information)
    msg.setText(text)
    msg.exec_()


def show_msg_question(title: str, text: str):
    msg = QMessageBox()
    msg.setWindowTitle(title)
    msg.setIcon(QMessageBox.Question)
    msg.addButton("Нет", QMessageBox.NoRole)
    msg.addButton("Да", QMessageBox.YesRole)
    msg.setText(text)
    return msg.exec_()

