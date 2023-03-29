import abc
import asyncio
import re
import sys
from typing import Optional, List

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import *
from logicsDB import UserLogic, TheoryLogic, TestLogic
from db import *


class ViewQuestion(abc.ABC):
    instanses = []

    def __init__(self, form: QFormLayout):
        self.form = form

    @abc.abstractmethod
    def setup(self):
        pass

    @abc.abstractmethod
    def check(self):
        pass

    @abc.abstractmethod
    def update(self):
        pass

    @classmethod
    def setup_all(cls, number: int):
        return cls.instanses[number].setup()

    @classmethod
    def check_all(cls, number: int):
        return cls.instanses[number].check()

    @classmethod
    def update_all(cls, number: int):
        return cls.instanses[number].update()

    @classmethod
    def set_order_tests(cls, form: QFormLayout):
        cls.instanses.clear()
        cls.instanses.extend((ViewQuestionChoise(form), ViewQuestionInputAnswer(form), ViewQuestionNotCheck(form)))
        return cls


class ViewQuestionChoise(ViewQuestion):

    def __init__(self, form: QFormLayout):
        super().__init__(form)

    def check(self) -> bool:
        has_any_correct_answer = False
        for i in range(self.form.rowCount() - 1):
            layout = self.form.itemAt(i, QFormLayout.FieldRole)
            line_edit: QLineEdit = layout.itemAt(0).widget()
            check_box: QCheckBox = layout.itemAt(1).widget()
            has_any_correct_answer = has_any_correct_answer or check_box.isChecked()
            line_edit.setText(line_edit.text().rstrip())
            if len(line_edit.text()) == 0:
                show_msg_information("Ошибка при добавлении ответа на вопрос", f"Пустой {i + 1}-ый вариант ответа")
                return False
        if not has_any_correct_answer:
            show_msg_information("Ошибка при добавлении ответа на вопрос", "Ни один ответ не является верным")
        return has_any_correct_answer

    def update(self):
        return

    def setup(self):
        btn_add = QPushButton("Добавить ответ")
        btn_add.clicked.connect(self.add_choise_answer)
        btn_del = QPushButton("Удалить ответ")
        btn_del.clicked.connect(self.remove_choise_answer)
        self.form.addRow(btn_del, btn_add)
        self.add_new_answer(self.form)
        self.add_new_answer(self.form)

    @staticmethod
    def add_new_answer(form: QFormLayout):
        layout = QHBoxLayout()
        layout.addWidget(QLineEdit())
        layout.addWidget(QCheckBox("Верный ли ответ"))
        form.insertRow(form.rowCount() - 1, "Вариант ответа:", layout)

    def add_choise_answer(self):
        self.add_new_answer(self.form)

    def remove_choise_answer(self):
        if self.form.rowCount() <= 3:
            show_msg_information("Нельзя удалить ответ", "Вариантов ответа должно быть минимум два")
            return
        self.form.removeRow(self.form.rowCount() - 2)


class ViewQuestionInputAnswer(ViewQuestion):
    def __init__(self, form: QFormLayout):
        super().__init__(form)

    def setup(self):
        sb = QDoubleSpinBox()
        sb.setRange(0.0, 100.0)
        sb.setValue(90)
        sb.setSuffix(" %")
        sb.setToolTip("Минимальный процент схожести введенного ответа с правильным. Позволит не терять баллы из-за "
                      "опечаток, однако низкий процент может привести к возможности угадать ответ. Лучше от 80%")
        self.form.addRow("Минимальный процент схожести ответов:", sb)
        self.form.addRow("Правильный ответ:", QLineEdit())

    def check(self):
        k = self.form.itemAt(0, QFormLayout.FieldRole).widget()
        answer = self.form.itemAt(1, QFormLayout.FieldRole).widget()
        answer.setText(answer.text().rstrip())
        if len(answer.text()) == 0:
            show_msg_information("Ошибка при добавлении ответа на вопрос", f"Пустой правильный ответ на вопрос")
            return False
        if int(k.value()) == 0:
            return show_msg_question("Полностью непохожие ответы",
                                     "У вас выставлена 0 схожесть ответов. Это значит, "
                                     "что любой ответ будет считаться правильным. Вы уверены что хотите продолжить?")
        return True

    def update(self):
        return


class ViewQuestionNotCheck(ViewQuestion):
    def __init__(self, form: QFormLayout):
        super().__init__(form)

    def setup(self):
        return

    def check(self):
        return True

    def update(self):
        return


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


class TheoryViewWidget(QTabWidget):
    def __init__(self, theory: Optional[Theory] = None, parent: QWidget = None):
        super().__init__(parent)
        self.theory = theory
        if theory:
            for name, html in zip(*TheoryLogic().load_chapters_from_theory(theory)):
                widget = QTextEdit(html)
                widget.setReadOnly(True)
                self.addTab(widget, name)


class TheoryWidget(QWidget):
    changedTheories = pyqtSignal()

    def __init__(self, updated_theory: Optional[Theory] = None, parent: QWidget = None):
        super().__init__(parent)
        self.setWindowTitle("Теоретический материал")
        self.setMinimumSize(int(400 * 16 / 9), 400)

        self.updated_theory = updated_theory

        self.name_theory = QLineEdit()
        self.name_chapter = QLineEdit()
        self.study_time = QSpinBox()
        self.study_time.setSuffix(" мин.")
        self.study_time.setToolTip("Предполагаемое время изучения в минутах. Не обязательно к заполнению. При "
                                   "установке значения в ноль просто не будет учтен")
        self.study_time.setMaximum(1000000)

        form = QFormLayout()
        form.setSpacing(10)
        form.addRow("Название материала:", self.name_theory)
        form.addRow("Предполагаемое время изучения", self.study_time)
        form.addRow("Название раздела:", self.name_chapter)

        btn_add_chapter = QPushButton("Добавить раздел теории")
        btn_add_chapter.clicked.connect(self.add_chapter)
        btn_rename_chapter = QPushButton("Переименовать выбранный раздел теории")
        btn_rename_chapter.clicked.connect(self.rename_current_chapter)
        btn_remove_chapter = QPushButton("Удалить выбранный раздел теории")
        btn_remove_chapter.clicked.connect(self.remove_current_chapter)

        hlayout_chapter = QHBoxLayout()
        hlayout_chapter.addWidget(btn_add_chapter)
        hlayout_chapter.addWidget(btn_rename_chapter)
        hlayout_chapter.addWidget(btn_remove_chapter)

        btn_save = QPushButton("Сохранить" if updated_theory is None else "Изменить", self)
        btn_save.clicked.connect(self.save)
        btn_cancel = QPushButton("Отмена", self)
        btn_cancel.clicked.connect(self.close)
        hlayout = QHBoxLayout()
        hlayout.addWidget(btn_cancel)
        hlayout.addWidget(btn_save)

        vlayout = QVBoxLayout(self)
        vlayout.addLayout(form)
        vlayout.addLayout(hlayout_chapter)
        self.tabs_chapters = TheoryViewWidget(updated_theory, self)
        vlayout.addWidget(self.tabs_chapters)
        vlayout.addLayout(hlayout)

        if updated_theory is not None:
            self.name_theory.setText(updated_theory.name)
            if updated_theory.study_time is not None:
                self.study_time.setValue(updated_theory.study_time.minute)

    @staticmethod
    def _check_text(text: str) -> bool:
        return not (len(text) == 0 or not re.match(r"\w+|\d+", text))

    def add_chapter(self):
        if self._check_text(self.name_chapter.text()):
            self.tabs_chapters.addTab(QTextEdit(), self.name_chapter.text().rstrip())
            self.tabs_chapters.setCurrentIndex(self.tabs_chapters.count() - 1)
        else:
            show_msg_information("Ошибка добавления раздела",
                                 "Название раздела теории должен содержать хотя бы один читаемый символ")

    def rename_current_chapter(self):
        if self._check_text(self.name_chapter.text()):
            self.tabs_chapters.setTabText(self.tabs_chapters.currentIndex(), self.name_chapter.text())
            if self.updated_theory is not None:
                self.updated_theory.chapters[self.tabs_chapters.currentIndex()].name = self.name_chapter.text()
        else:
            show_msg_information("Ошибка переименования раздела",
                                 "Название раздела теории должен содержать хотя бы один читаемый символ")

    def remove_current_chapter(self):
        result = show_msg_question("Удаление раздела теории",
                                   f"Вы действительно хотите удалить раздел "
                                   f"{self.tabs_chapters.tabText(self.tabs_chapters.currentIndex())}?")
        if result:
            if self.updated_theory is not None:
                self.updated_theory.chapters.pop(self.tabs_chapters.currentIndex())
            self.tabs_chapters.removeTab(self.tabs_chapters.currentIndex())

    def save(self):
        if not self._check_text(self.name_theory.text()):
            show_msg_information("Ошибка при сохранении",
                                 "Название теоретического материала должен содержать хотя бы один читаемый символ")
        if not self.tabs_chapters.count():
            show_msg_information("Ошибка при сохранении", "Создайте хотя бы один раздел теории перед сохранением")
        else:
            if self.updated_theory is None:
                names = []
                chapters = []
                for i in range(self.tabs_chapters.count()):
                    names.append(self.tabs_chapters.tabText(i))
                    chapters.append(self.tabs_chapters.widget(i).toHtml())

                TheoryLogic().create(self.name_theory.text(), self.study_time.value(), names, chapters)
            else:
                self.updated_theory.name = self.name_theory.text()
                if self.study_time.value() <= 0:
                    self.updated_theory.study_time = None
                else:
                    self.updated_theory.study_time = datetime.time(minute=self.study_time.value())
                names = []
                chapters = []
                for i in range(len(self.updated_theory.chapters), self.tabs_chapters.count()):
                    names.append(self.tabs_chapters.tabText(i))
                    chapters.append(self.tabs_chapters.widget(i).toHtml())
                TheoryLogic().add_chapters(self.updated_theory, names, chapters)
            self.changedTheories.emit()
            show_msg_question("Теория", "Теоретический материал успешно создан")
            self.close()


class CreateTestWidget(QWidget):
    def __init__(self, theories: List[Theory], parent=None):
        super().__init__(parent)
        self.question_vlayouts = []
        self.question_complition_times = []
        self.question_weights = []
        self.question_names = []
        self.question_types = []
        self.theories = theories

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
        btn_cancel.clicked.connect(self.close)
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
        self.question_names.append(QTextEdit(self))
        self.question_weights.append(QSpinBox(self))
        self.question_weights[-1].setToolTip("По умолчанию у всех вопросов стоит вес 1. Если хотите повысить "
                                             "значимость вопроса увеличьте это значение")
        self.question_complition_times.append(QSpinBox(self))
        self.question_complition_times[-1].setSuffix(" сек.")
        self.question_complition_times[-1].setRange(1, 214748364)
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
        btn_prev = QPushButton("Назад", self)
        btn_prev.clicked.connect(self.to_prev)
        btn_next = QPushButton("Далее", self)
        btn_next.clicked.connect(self.to_next)
        btn_save = QPushButton("Завершить")
        btn_save.clicked.connect(self.to_finish)
        hlayout = QHBoxLayout(self)
        hlayout.addWidget(btn_cancel)
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

    def _get_type_layout(self) -> Optional[QFormLayout]:
        return self.question_vlayouts[self.stacked_layout.currentIndex() - 1].itemAt(1).widget().layout()

    def _check_data_question(self) -> bool:
        curr = self.stacked_layout.currentIndex() - 1
        cb: QComboBox = self.question_types[curr]
        if not self._check_text(self.question_names[curr].toPlainText()):
            show_msg_information("Ошибка заполнения вопроса", "Вопрос должен содержать хотя бы один читаемый символ")
            return False
        if not ViewQuestion.set_order_tests(self._get_type_layout()).check_all(cb.currentIndex()):
            return False
        return True

    def to_next(self):
        if self.stacked_layout.currentIndex() == 0 and not self._check_data_test() or \
                self.stacked_layout.currentIndex() and not self._check_data_question():
            return
        if self.stacked_layout.count() == self.stacked_layout.currentIndex() + 1:
            self.add_question_widget()
        else:
            self.stacked_layout.setCurrentIndex(self.stacked_layout.currentIndex() + 1)
        self.update_title()

    def to_prev(self):
        if self.stacked_layout.currentIndex() > 0:
            self.stacked_layout.setCurrentIndex(self.stacked_layout.currentIndex() - 1)
        self.update_title()

    def to_finish(self):
        pass

    def update_title(self):
        self.setWindowTitle(f"Вопрос {self.stacked_layout.currentIndex()} из {self.stacked_layout.count() - 1}")
        if self.stacked_layout.currentIndex() == 0:
            self.setWindowTitle("Мастер создания тестов")

    def to_cancel(self):
        res = show_msg_question("Отменить создание теста", "Отменить создание теста? Все данные будут потеряны.")
        if res:
            self.close()


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
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
        add_test = QAction("Добавить уже существующий тест", self)
        add_test.triggered.connect(self.add_exist_test)
        run_test = QAction("Пройти тест", self)
        run_test.triggered.connect(self.run_test)
        menu_tests = QMenu("Тест", self)
        menu_tests.addAction(create_test)
        menu_tests.addAction(add_test)
        menu_tests.addAction(run_test)

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
        self.theory = TheoryWidget(theory)
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
            res = TestLogic().get(widget.textValue())
            if res is not None:
                self.tests.append(res)
            else:
                show_msg_information(
                    "Не найден тест",
                    "Извините но по данному айди не нашлось теста. Перепроверте тест и попробуйте снова")

    def run_test(self):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
