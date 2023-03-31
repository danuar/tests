import re
import sys
from typing import Optional, List

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QTextCursor, QColor, QTextCharFormat
from PyQt5.QtWidgets import *

from MessageBox import *
from db import *
from logicsDB import UserLogic, TheoryLogic, TestLogic
from TheoryWidgets import *
from ViewQuestion import *


class CreateTestWidget(QWidget):
    def __init__(self, theories: List[Theory], parent=None):
        super().__init__(parent)
        self.question_vlayouts = []
        self.question_complition_times = []
        self.question_weights = []
        self.question_names = []
        self.question_types = []
        self.cursors_for_answers: list[Optional[QTextCursor]] = []
        self.theories = theories
        self.theory_widget: Optional[TheoryViewWidget] = None

        self.setWindowTitle("Мастер создания тестов")
        self.setMinimumSize(int(400 * 16 / 9), 400)

        self.name_box = QLineEdit(self)
        self.completion_time_box = QSpinBox()
        self.completion_time_box.setMaximum(10000000)
        self.completion_time_box.setToolTip(
            "Время за которое нужно пройти тест. \n"
            "Можно не указывать, но тогда надо будет указать время ответа на каждый вопрос")
        self.completion_time_box.setSuffix(" сек.")
        self.count_attempts_box = QSpinBox(self)
        self.count_attempts_box.setToolTip("0 - неограниченное количество попыток")
        self.theory = QComboBox(self)
        self.theory.addItems([i.name for i in theories])

        form = QFormLayout()
        form.addRow("Название теста:", self.name_box)
        form.addRow("Время выполнения (необязательно):", self.completion_time_box)
        form.addRow("Количество попыток:", self.count_attempts_box)
        form.addRow("Теория для теста:", self.theory)

        btn_save = QPushButton("Далее")
        btn_save.clicked.connect(self.to_next)
        btn_cancel = QPushButton("Отмена", self)
        btn_cancel.clicked.connect(self.to_cancel)
        hlayout = QHBoxLayout()
        hlayout.addWidget(btn_cancel)
        hlayout.addWidget(btn_save)

        vlayout = QVBoxLayout()
        vlayout.addLayout(form)
        vlayout.addLayout(hlayout)

        self.stacked_layout = QStackedLayout(self)
        self.stacked_layout.addWidget(self._widget(vlayout))

    @staticmethod
    def _check_text(text: str) -> bool:
        return not (len(text) == 0 or not re.match(r"\w+|\d+", text))

    def _check_data_test(self):
        if not self._check_text(self.name_box.text()):
            show_msg_information("Ошибка в поле названия теста", "В названии должен быть хотя бы один читаемый символ")
            return False
        return True

    def _widget(self, layout: QLayout) -> QWidget:
        res = QWidget(self)
        res.setLayout(layout)
        return res

    def add_question_widget(self):
        form = QFormLayout(self)
        self.cursors_for_answers.append(None)
        self.question_names.append(QTextEdit(self))
        self.question_weights.append(QSpinBox(self))
        self.question_weights[-1].setToolTip("По умолчанию у всех вопросов стоит вес 1. Если хотите повысить "
                                             "значимость вопроса увеличьте это значение")
        self.question_weights[-1].setRange(1, 99999999)
        self.question_complition_times.append(QSpinBox(self))
        self.question_complition_times[-1].setSuffix(" сек.")
        self.question_complition_times[-1].setRange(0, 214748364)
        self.question_complition_times[-1].setToolTip("Значение 0 сек. обязывает вас указать время прохождения теста в "
                                                      "общем, не ограничивая время ответа на конкретный вопрос.\n"
                                                      "Не учитывается если указано время прохождения теста")
        self.question_types.append(QComboBox(self))
        self.question_types[-1].addItems(["С вариантами ответов", "С вводимым ответом", "С ручной проверкой"])
        self.question_types[-1].currentIndexChanged.connect(self.on_changed_type_test)

        form.addRow("Вопрос:", self.question_names[-1])
        form.addRow("  ", QWidget(self))
        form.addRow("Вес вопроса:", self.question_weights[-1])
        form.addRow("Время ответа на вопрос:", self.question_complition_times[-1])
        form.addRow("Тип теста:", self.question_types[-1])

        btn_cancel = QPushButton("Отмена", self)
        btn_cancel.clicked.connect(self.to_cancel)
        btn_remove = QPushButton("Удалить вопрос")
        btn_remove.clicked.connect(self.to_remove_question)
        btn_prev = QPushButton("Назад", self)
        btn_prev.clicked.connect(self.to_prev)
        btn_next = QPushButton("Далее", self)
        btn_next.clicked.connect(self.to_next)
        btn_save = QPushButton("Завершить")
        btn_save.clicked.connect(self.to_finish)
        hlayout = QHBoxLayout(self)
        hlayout.addWidget(btn_cancel)
        hlayout.addWidget(btn_remove)
        hlayout.addWidget(btn_prev)
        hlayout.addWidget(btn_next)
        hlayout.addWidget(btn_save)

        self.question_vlayouts.append(QVBoxLayout(self))
        self.question_vlayouts[-1].addLayout(form)
        self.question_vlayouts[-1].addWidget(QWidget())
        self.question_vlayouts[-1].addSpacing(25)
        self.question_vlayouts[-1].addLayout(hlayout)
        self.stacked_layout.addWidget(self._widget(self.question_vlayouts[-1]))
        self.stacked_layout.setCurrentIndex(self.stacked_layout.count() - 1)
        self.on_changed_type_test(self.question_types[-1].currentIndex())

    def on_changed_type_test(self, index: Optional[int] = None):
        type_test_widget = QWidget()
        form = QFormLayout(type_test_widget)
        current_index = self.sender().currentIndex() if type(self.sender()) == QComboBox else index
        ViewQuestion.set_order_tests(form).setup_all(current_index)

        vlayout = self.question_vlayouts[self.stacked_layout.currentIndex() - 1]
        old_widget: QWidget = vlayout.itemAt(1).widget()
        vlayout.replaceWidget(old_widget, type_test_widget)
        old_widget.deleteLater()

    def _get_type_layout_from_index(self, index) -> Optional[QFormLayout]:
        return self.question_vlayouts[index].itemAt(1).widget().layout()

    def _get_type_layout(self) -> Optional[QFormLayout]:
        return self._get_type_layout_from_index(self.stacked_layout.currentIndex() - 1)

    def _check_data_question(self) -> bool:
        curr = self.stacked_layout.currentIndex() - 1
        new_cursor = self.theory_widget.current_cursor
        if new_cursor:
            self.cursors_for_answers[curr] = new_cursor
        cb: QComboBox = self.question_types[curr]
        if not self._check_text(self.question_names[curr].toPlainText()):
            show_msg_information("Ошибка заполнения вопроса", "Вопрос должен содержать хотя бы один читаемый символ")
            return False
        if self.completion_time_box.value() == 0 and self.question_complition_times[curr].value() == 0:
            show_msg_information(
                "Неверное время выполнения теста",
                "При создании теста вы не указали время его прохождения.\nЗначит вы должны указать время прохождения "
                "для каждого вопроса, либо вернуться и указать время прохождения")
            return False
        if not ViewQuestion.set_order_tests(self._get_type_layout()).check_all(cb.currentIndex()):
            return False
        if not (len(self.cursors_for_answers) > curr and self.cursors_for_answers[curr]):
            show_msg_information(
                f"Не был добавлен ответ на вопрос",
                f"Прежде чем перейти дальше укажите ответ на данный вопрос в теории.\n"
                f"Для этого выберите окно с теорией выделите текст, который считаете ответом\nи "
                f"правой кнопкой мыши в контекстном меню выберете {self.theory_widget.add_pointer_action.text()} или "
                f"нажмите сочетание клавиш {[i.toString() for i in self.theory_widget.add_pointer_action.shortcuts()]}")
            if not self.theory_widget.isVisible():
                self.theory_widget.show()
            return False
        self.theory_widget.remove_cursor()
        return True

    def to_next(self):
        if self.stacked_layout.currentIndex() == 0 and not self._check_data_test() or \
                self.stacked_layout.currentIndex() and not self._check_data_question():
            return
        if self.stacked_layout.currentIndex() == 0:
            th = self.theories[self.theory.currentIndex()]
            if self.theory_widget is not None and th.id != self.theory_widget.theory.id:
                self.theory_widget.close()
            if self.theory_widget is None or th.id != self.theory_widget.theory.id:
                self.theory_widget = TheoryViewWidget(th)
                self.theory_widget.show()
        if self.stacked_layout.count() == self.stacked_layout.currentIndex() + 1:
            self.add_question_widget()
        else:
            self.stacked_layout.setCurrentIndex(self.stacked_layout.currentIndex() + 1)
            self.update_cursor()
        self.update_title()

    def to_prev(self):
        self.theory_widget.remove_cursor()
        if self.stacked_layout.currentIndex() > 0:
            self.stacked_layout.setCurrentIndex(self.stacked_layout.currentIndex() - 1)
            self.update_cursor()
        self.update_title()

    def to_finish(self):
        if not self._check_data_question():
            return
        completion_time = self.completion_time_box.value()
        if completion_time == 0:
            completion_time = sum(i.value() for i in self.question_complition_times)
        if show_msg_question("Создать новый тест",
                             f"Будет создан тест содержащий {len(self.question_names)} вопроса(ов)."
                             f"\nВремя прохождения составит: {completion_time} сек. Продолжить?"):
            self.insert_test_in_db()
            show_msg_information("Создан тест", "Тест успешно создан")
            self.theory_widget.close()
            self.close()

    def insert_test_in_db(self):
        test = Test(
            name=self.name_box.text(),
            creator=UserLogic.user,
            theory=self.theory_widget.theory,
        )
        if self.completion_time_box.value():
            s = self.completion_time_box.value()
            test.completion_time = datetime.time(hour=s // 3600, minute=s // 60, second=s % 60)
        if self.count_attempts_box.value():
            test.count_attempts = self.count_attempts_box.value()
        for i in range(self.stacked_layout.count() - 1):
            question = Question()
            question.name = self.question_names[i].toPlainText()
            question.weight = self.question_weights[i].value()
            cursor = self.cursors_for_answers[i]
            question.pointer_to_answer = PointerToAnswer(
                chapter=cursor.chapter,
                start=cursor.selectionStart(),
                end=cursor.selectionEnd()
            )
            if not test.completion_time:
                s = self.question_complition_times[i].value()
                question.complition_time = datetime.time(hour=s // 3600, minute=s // 60, second=s % 60)
            ViewQuestion.set_order_tests(self._get_type_layout_from_index(i)) \
                .create_specify_entity(self.question_types[i].currentIndex(), question)
            test.questions.append(question)
        TestLogic().create(test)

    def update_cursor(self):
        curr = self.stacked_layout.currentIndex() - 1
        if 0 <= curr < len(self.cursors_for_answers) and self.cursors_for_answers[curr]:
            self.theory_widget.add_cursor(self.cursors_for_answers[curr])

    def update_title(self):
        self.setWindowTitle(f"Вопрос {self.stacked_layout.currentIndex()} из {self.stacked_layout.count() - 1}")
        if self.stacked_layout.currentIndex() == 0:
            self.setWindowTitle("Мастер создания тестов")

    def to_cancel(self):
        res = show_msg_question("Отменить создание теста", "Отменить создание теста? Все данные будут потеряны.")
        if res:
            if self.theory_widget:
                self.theory_widget.close()
            self.close()

    def to_remove_question(self):
        if show_msg_question("Удалить вопрос?", "Вы действительно хотите удалить этот вопрос? \n"
                                                "Вернуть его не получится."):
            widget = self.stacked_layout.currentWidget()
            self.stacked_layout.setCurrentIndex(self.stacked_layout.currentIndex())
            curr = self.stacked_layout.currentIndex() - 1
            self.stacked_layout.removeWidget(widget)
            if self.theory_widget:
                self.theory_widget.remove_cursor()
            self.cursors_for_answers.pop(curr)
            self.question_names.pop(curr)
            self.question_weights.pop(curr)
            self.question_complition_times.pop(curr)
            self.question_types.pop(curr)
            self.question_vlayouts.pop(curr)
            self.update_title()


class RunTestWidget(QDialog):
    def __init__(self, test: Test, parent: QWidget = None):
        super().__init__(parent)
        self.test = test

        self.setWindowTitle(f'Пройти тест: "{test.name}"')

        txt = ""
        if test.theory.study_time:
            txt = f". Примерное время изучения {test.theory.study_time.minute + test.theory.study_time.hour} мин."
        btn_get_theory = QPushButton(f"Изучить теорию {test.theory.name}" + txt)
        btn_get_theory.clicked.connect(self.on_get_theory_clicked)
        btn_get_theory.setMaximumSize(600, 100)
        btn_get_theory.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        btn_get_theory.setAutoDefault(True)
        btn_running_test = QPushButton("Начать тест")
        btn_running_test.clicked.connect(self.on_running_test)
        btn_running_test.setMaximumSize(600, 100)
        btn_running_test.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        f = lambda x: x.hour * 3600 + x.minute * 60 + x.second
        t = f(test.completion_time) if test.completion_time else sum(f(i.complition_time) for i in test.questions)
        label_info = QLabel(f"Тест: {test.name}\nВопросов: {len(test.questions)}\nВремя прохождения: {t} сек.")
        label_info.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        vlayout = QVBoxLayout()
        vlayout.setAlignment(Qt.AlignCenter)
        vlayout.addWidget(label_info)
        vlayout.addWidget(btn_get_theory)
        vlayout.addWidget(btn_running_test)

        btn = QPushButton("Вернуться к прохождению теста")
        btn.clicked.connect(self.on_get_default_window_clicked)
        vl = QVBoxLayout()
        vl.addWidget(btn)
        vl.addWidget(TheoryViewWidget(test.theory))

        self.stacked_widget = QStackedLayout(self)
        self.stacked_widget.addWidget(self._create_widget(vlayout))
        self.stacked_widget.addWidget(self._create_widget(vl))

    def _create_question_widget(self, index_question):
        question = self.test.questions[index_question]
        header = QFrame(self)
        header.setStyleSheet(".QFrame { "
                             "background: qlineargradient(x1:0, y1:1, x2:1, y2:1, stop:0 #5400c7, stop:1 #9c0ec4); } "
                             "QLabel { color: #ffffff; }"
                             ".QFrame:hover { background: qlineargradient(x1:0, y1:1, x2:1, y2:1, stop:0 #5400c7, stop:0.5 #c800ff, stop:1 #9c0ec4); }")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(2, 2, 2, 2)
        hl.addWidget(QLabel(f"Вопрос {index_question + 1} из {len(self.test.questions)}", self))
        hl.addWidget(QLabel(f"Оставшиеся время: {question.complition_time}", self), alignment=Qt.AlignRight)

        widget = QWidget(self)

        btn_to_next = QPushButton("Следующий вопрос")
        hl1 = QHBoxLayout()
        hl1.setContentsMargins(8, 8, 8, 8)
        hl1.addWidget(btn_to_next)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(header, alignment=Qt.AlignTop)
        layout.addWidget(widget)
        layout.addLayout(hl1)

        if self.stacked_widget.count() == 3:
            self.stacked_widget.removeWidget(self.stacked_widget.widget(2))
        self.stacked_widget.addWidget(self._create_widget(layout))
        self.stacked_widget.setCurrentIndex(2)

    def _create_widget(self, layout: QLayout) -> QWidget:
        r = QWidget(self)
        r.setLayout(layout)
        return r

    def on_get_theory_clicked(self):
        self.stacked_widget.setCurrentIndex(1)

    def on_get_default_window_clicked(self):
        self.stacked_widget.setCurrentIndex(0)

    def on_running_test(self):
        if show_msg_question("Начать тест", "Вы уверены что хотите начать тест?"):
            self._create_question_widget(0)


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.menu_run_test: Optional[QMenu] = None
        self.tests = []
        self.create_test_widget = None
        self.menu_update_theories = None
        self.theories = None
        self.theory = None
        self.menu = None

        UserLogic.setup_user_from_file()
        self.initUI()

    def init_menu(self):
        self.menu = QMenuBar(self)

        view_result_finish_tests = QAction("Просмотреть результаты пройденных тестов", self)
        view_result_created_tests = QAction("Просмотреть результаты ваших тестов", self)
        menu_results = QMenu("Результаты тестов", self)
        menu_results.addAction(view_result_finish_tests)
        menu_results.addAction(view_result_created_tests)

        create_test = QAction("Создать новый тест", self)
        create_test.triggered.connect(self.create_test)

        self.menu_run_test = QMenu("Пройти тест", self)
        self.tests.extend(TestLogic().all_from_user())
        for test in self.tests:
            action = QAction(test.name, self)
            action.test = test
            action.triggered.connect(self.run_test)
            self.menu_run_test.addAction(action)
        add_test = QAction("Добавить уже существующий тест", self)
        add_test.triggered.connect(self.add_exist_test)
        self.menu_run_test.addAction(add_test)

        menu_tests = QMenu("Тест", self)
        menu_tests.addAction(create_test)
        menu_tests.addMenu(self.menu_run_test)

        add_theory_action = QAction("Добавить теоретический материал", self)
        add_theory_action.triggered.connect(self.show_theory_window)
        self.menu_update_theories = QMenu("Изменить существующие теории", self)
        menu_add_theory = QMenu("Теоретический материал", self)
        menu_add_theory.addAction(add_theory_action)
        menu_add_theory.addMenu(self.menu_update_theories)
        self.load_theories()

        self.menu.addMenu(menu_tests)
        self.menu.addMenu(menu_results)
        self.menu.addMenu(menu_add_theory)

    def initUI(self):
        self.init_menu()
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
        layout.setMenuBar(self.menu)

        self.setWindowTitle("Платформа для создания и проверки тестов")
        self.setMinimumSize(700, 360)

    def load_theories(self):
        self.theories = TheoryLogic().get_all()
        self.menu_update_theories.clear()
        for theory in self.theories:
            action = QAction(theory.name, self)
            action.theory = theory
            action.triggered.connect(self.show_theory_window_for_update)
            self.menu_update_theories.addAction(action)

    def show_theory_window(self, _=None, theory: Optional[Theory] = None):
        self.theory = TheoryTabWidget(theory)
        self.theory.changedTheories.connect(self.load_theories)
        self.theory.show()

    @QtCore.pyqtSlot()
    def show_theory_window_for_update(self):
        self.show_theory_window(theory=self.sender().theory)

    def create_test(self):
        self.create_test_widget = CreateTestWidget(self.theories)
        self.create_test_widget.show()

    def add_exist_test(self):
        widget = QInputDialog(self)
        widget.setWindowTitle("Добавить тест по id")
        widget.setLabelText("Введите id теста, который дал вам создатель теста:")
        widget.show()
        if widget.exec_():
            res = TestLogic().get(uuid.UUID(widget.textValue()))
            if res is not None:
                self.tests.append(res)
                action = QAction(res.name, self)
                action.triggered.connect(self.run_test)
                self.menu_run_test.insertAction(self.menu_run_test.actions()[-1], action)
            else:
                show_msg_information(
                    "Не найден тест",
                    "Извините но по данному айди не нашлось теста. Перепроверте тест и попробуйте снова")

    def run_test(self):
        if self.theory:
            self.theory.close()
        widget = RunTestWidget(self.sender().test, self)
        return widget.exec()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    with open("Toolery.qss", "r") as f:
        app.setStyleSheet(f.read())
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
