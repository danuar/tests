import sys
from PyQt5.QtWidgets import *
import qdarkgraystyle


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        menu = QMenuBar(self)
        menu.addMenu("Добавить тест")
        menu.addMenu("Добавить теореритеский материал")

        main_splitter = QSplitter()

        scroll_created_tests = QScrollArea()
        w = QWidget()
        vbox = QVBoxLayout(w)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        for i in range(20):
            btn = QPushButton(f"Tests #{i}")
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            vbox.addWidget(btn)
        scroll_created_tests.setWidgetResizable(True)
        scroll_created_tests.setWidget(w)
        scroll_available_tests = QScrollArea()
        scroll_results_tests = QScrollArea()
        main_splitter.addWidget(scroll_available_tests)
        main_splitter.addWidget(scroll_results_tests)
        main_splitter.addWidget(scroll_created_tests)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(main_splitter)
        layout.setMenuBar(menu)

        self.setWindowTitle("Платформа для создания и проверки тестов")
        self.setMinimumSize(700, 360)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
