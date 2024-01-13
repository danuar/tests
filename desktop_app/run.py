import asyncio
import locale
import operator
import os.path
import platform
import random
import sys
import time
import uuid
from functools import reduce
from typing import List, Tuple

from PyQt5 import QtCore, QtGui
from PyQt5.QtChart import QChartView, QChart, QPieSeries, QPercentBarSeries, QBarCategoryAxis, QBarSet
from PyQt5.QtCore import Qt, QTimer, QModelIndex, QTranslator
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QPainter, QPen, QFont, QIcon
from PyQt5.QtWidgets import *

from desktop_app.Controllers.QtHttpClientController import QtHttpClientController
from desktop_app.Controllers.ResultTestController import ResultTestController
from desktop_app.Controllers.TestController import TestController
from desktop_app.Models import Test, Answer, ResultTest, User, ResultTestEasy
from desktop_app.TheoryWidgets import *
from desktop_app.ViewQuestion import *
from solve_resource_one_exe import resource_path


def sum_time(times: list[datetime.time]):
    try:
        return reduce(operator.add,
                      (datetime.timedelta(hours=i.hour, minutes=i.minute, seconds=i.second) for i in map(cast_to_time, times)))
    except TypeError:
        return 0


def cast_to_time(value):
    if isinstance(value, str):
        return datetime.time.fromisoformat(value)
    return value


class CreateTestWidget(QWidget):
    created_test = pyqtSignal(Test)

    def __init__(self, theories: List[Theory], parent=None):
        super().__init__(parent)
        self.test: Optional[Test] = None
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
        self.check_box_shuffle = QCheckBox(self)
        self.check_box_show_answers = QCheckBox()
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
        form.addRow("Перемешивать вопросы:", self.check_box_shuffle)
        form.addRow("Показывать ответы после прохождения:", self.check_box_show_answers)

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
        sender = self.sender()
        current_index = sender.currentIndex() if isinstance(sender, QComboBox) else index
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
            self.create_test_in_api()
            msg = QMessageBox()
            msg.setWindowTitle("Тест создан")
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setText(f"Тест успешно создан. Id теста: {self.test.id}")
            btn_copy = QPushButton("Скопировать id в буфер обмена")
            btn_copy.clicked.connect(self.copy_test_id)
            msg.addButton(btn_copy, QMessageBox.ButtonRole.NoRole)
            msg.addButton("Выйти", QMessageBox.ButtonRole.YesRole)
            msg.exec_()
            self.theory_widget.close()
            self.close()
            self.created_test.emit(self.test)

    def copy_test_id(self):
        if self.test is not None:
            QtGui.QGuiApplication.clipboard().setText(str(self.test.id))

    def create_test_in_api(self):
        self.test = Test(
            name=self.name_box.text(),
            theory=self.theory_widget.theory,
            shuffle=self.check_box_shuffle.isChecked(),
            show_answer=self.check_box_show_answers.isChecked(),
        )
        if self.completion_time_box.value():
            s = self.completion_time_box.value()
            self.test.complition_time = datetime.time(hour=s // 3600, minute=s // 60, second=s % 60).isoformat()
        if self.count_attempts_box.value():
            self.test.count_attempts = self.count_attempts_box.value()
        for i in range(self.stacked_layout.count() - 1):
            question = Question(name=self.question_names[i].toPlainText(), weight=self.question_weights[i].value())
            question = (ViewQuestion.set_order_tests(self._get_type_layout_from_index(i))
                        .create_specify_entity(self.question_types[i].currentIndex(), question))
            cursor = self.cursors_for_answers[i]
            question.pointer_to_answer = PointerToAnswer(
                chapter=str(cursor.chapter.id),
                start=cursor.selectionStart(),
                end=cursor.selectionEnd()
            )
            if not self.test.complition_time:
                s = self.question_complition_times[i].value()
                question.complition_time = datetime.time(hour=s // 3600, minute=s // 60, second=s % 60).isoformat()
            self.test.questions.append(question)
        self.test = TestController().create(self.test)

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
        self.is_need_open_result = False
        self.timer_test: Optional[QTimer] = None
        self.start_test_time = None
        self.is_running_test = False
        self.start_run_time = None
        self.answers_check_box: Optional[list[QCheckBox]] = None
        self.input_answer: Optional[QLineEdit] = None
        self.test = test
        if test.shuffle:
            random.shuffle(self.test.questions)
        self._question_index = -1
        self.result_test = ResultTest(test=test)

        self.setWindowTitle(f'Пройти тест: "{test.name}"')

        txt = ""
        if test.theory.study_time:
            txt = f". Примерное время изучения {test.theory.study_time.minute + test.theory.study_time.hour} мин."
        btn_get_theory = QPushButton(f"Изучить теорию {test.theory.name}{txt}")
        btn_get_theory.clicked.connect(self.on_get_theory_clicked)
        btn_get_theory.setMaximumSize(600, 100)
        btn_get_theory.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        btn_get_theory.setAutoDefault(True)
        btn_running_test = QPushButton("Начать тест")
        btn_running_test.clicked.connect(self.on_running_test)
        btn_running_test.setMaximumSize(600, 100)
        btn_running_test.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        t = self._get_seconds(test.complition_time) if test.complition_time \
            else sum(self._get_seconds(i.complition_time) for i in test.questions)
        self.end_run_time = self.completion_time = t
        txt = "Неограниченное количество попыток"
        count_attempts = TestController().get_count_attempts(test.id)
        if count_attempts == 0:
            btn_running_test.setDisabled(True)
        if count_attempts is not None:
            if count_attempts % 10 == 1 and count_attempts != 11:
                attemp = 'попытка'
            elif 2 <= count_attempts % 10 <= 4 and not 12 <= count_attempts <= 14:
                attemp = 'попытки'
            else:
                attemp = 'попыток'
            if count_attempts > 0:
                txt = f"Осталось {count_attempts} {attemp}"
            else:
                txt = "Не осталось попыток"

        label_info = QLabel(f"Тест: {test.name}\nВопросов: {len(test.questions)}\nВремя прохождения: {t} сек.\n{txt}")
        label_info.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        button_copy = QPushButton(str(test.id))
        button_copy.setObjectName("link")
        button_copy.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        button_copy.clicked.connect(self.copy_text_id)
        hl = QHBoxLayout()
        hl.setSpacing(0)
        hl.addWidget(QLabel("Скопировать id теста:"), alignment=Qt.AlignLeft)

        hl.addWidget(button_copy, alignment=Qt.AlignLeft)
        vlayout = QVBoxLayout()
        vlayout.setAlignment(Qt.AlignCenter)
        vlayout.addWidget(label_info)
        vlayout.addLayout(hl)
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

    def copy_text_id(self):
        QApplication.clipboard().setText(str(self.test.id))

    @staticmethod
    def _get_seconds(current_time: datetime.time):
        return current_time.hour * 3600 + current_time.minute * 60 + current_time.second

    def _create_question_widget(self, index_question):
        self.start_run_time = time.time()
        question = self.test.questions[index_question]
        header = QFrame(self)
        header.setObjectName("menuTest")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(2, 2, 2, 2)
        hl.addWidget(QLabel(f"Вопрос {index_question + 1} из {len(self.test.questions)}   "
                            f"Вес вопроса: {question.weight}", self))
        self.label_end_time = QLabel(self)
        self._change_complition_time()
        if not self.test.complition_time:
            self._create_timer(self._get_seconds(question.complition_time) * 1000,
                               self._change_complition_time,
                               self.to_next_question)
        hl.addWidget(self.label_end_time, alignment=Qt.AlignRight)

        widget = QWidget(self)
        question_label = QTextEdit(question.name)
        question_label.setObjectName("question")
        question_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        question_label.setReadOnly(True)
        form = QFormLayout()
        form.addRow("Вопрос:", question_label)

        main_layout = QVBoxLayout(widget)
        main_layout.addLayout(form)
        main_layout.addStretch(1)
        self.answers_check_box = None
        self.input_answer = None
        if isinstance(question, QuestionChoice):
            self.answers_check_box = []
            main_layout.addWidget(QLabel("Варианты ответа:"))
            for answer in question.answers_test:
                self.answers_check_box.append(QCheckBox(answer.text))
                self.answers_check_box[-1].stateChanged.connect(self._on_changed_test_answer)
                main_layout.addWidget(self.answers_check_box[-1])
        else:
            self.input_answer = QLineEdit(self)
            self.input_answer.textChanged.connect(self._on_changed_input_answer)
            form1 = QFormLayout()
            txt = "Проверяется автоматически"
            if isinstance(question, QuestionNotCheck):
                txt = "Проверяется вручную"
            form1.addRow(f"Ответ ({txt}):", self.input_answer)
            main_layout.addLayout(form1)

        self.btn_to_next = QPushButton("Следующий вопрос")
        if len(self.test.questions) == index_question + 1:
            self.btn_to_next.setText("Закончить тест")
        self.btn_to_next.clicked.connect(self.to_next_question)
        self.btn_to_next.setDisabled(True)
        hl1 = QHBoxLayout()
        hl1.setContentsMargins(8, 8, 8, 8)
        hl1.addWidget(self.btn_to_next)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(header, alignment=Qt.AlignTop)
        layout.addWidget(widget)
        layout.addLayout(hl1)

        if self.stacked_widget.count() == 3:
            self.stacked_widget.removeWidget(self.stacked_widget.widget(2))
        self.stacked_widget.addWidget(self._create_widget(layout))
        self.stacked_widget.setCurrentIndex(2)

    def _destroy_timer(self):
        if self.timer_test:
            self.timer_test.disconnect()
            self.timer_test.deleteLater()

    def _create_timer(self, msec: int, update_slot, timeout_slot, msec_update=1000):
        self._destroy_timer()

        self.timer_test = QTimer(self)
        self.timer_test.setSingleShot(True)

        timer_updater = QTimer(self)
        timer_updater.setSingleShot(False)
        timer_updater.start(msec_update)
        timer_updater.timeout.connect(update_slot)

        self.timer_test.timeout.connect(self.timer_test.deleteLater)
        self.timer_test.timeout.connect(timer_updater.deleteLater)
        self.timer_test.timeout.connect(lambda: timer_updater.disconnect())
        self.timer_test.timeout.connect(timeout_slot)
        self.timer_test.start(msec)

    def _create_widget(self, layout: QLayout) -> QWidget:
        r = QWidget(self)
        r.setLayout(layout)
        return r

    def _on_changed_test_answer(self):
        self.btn_to_next.setEnabled(any(i.isChecked() for i in self.answers_check_box))

    def _on_changed_input_answer(self):
        self.btn_to_next.setEnabled(len(self.input_answer.text().rstrip()))

    def _on_timeout_running_test(self):
        self.result_test.completed_date = datetime.datetime.now()
        self.save_question()
        self._change_complition_time()
        self.is_running_test = False
        show_msg_information("Тест завершен", "К сожалению, вышло время прохождения теста. Ваш результат был сохранен.")
        self.close()

    def _change_complition_time(self):
        if not self.is_running_test:
            self.sender().disconnect()
            return
        completion_time = self.test.complition_time
        diff = time.time() - self.start_test_time
        if completion_time is None:
            completion_time = self.test.questions[self._question_index].complition_time
            diff = time.time() - self.start_run_time
        seconds = int(round(self._get_seconds(completion_time) - diff))
        suffix = "" if self.test.complition_time else " для вопроса"
        res_time = datetime.time(hour=seconds // 3600, minute=(seconds // 60) % 60, second=int(seconds % 60))
        self.label_end_time.setText(f"Оставшиеся время{suffix}: {res_time}")

    def save_question(self):
        question = self.test.questions[self._question_index]
        sec = round(time.time() - self.start_run_time)
        complition_time = datetime.time(hour=sec // 3600, minute=sec // 60 % 60, second=sec % 60).isoformat()
        answer = Answer(question=question, complition_time=complition_time)
        if isinstance(question, QuestionChoice):
            answer.answers_test = [str(a.id) for i, a in enumerate(question.answers_test) if self.answers_check_box[i].isChecked()]
        else:
            answer.text_answer = self.input_answer.text()
        self.result_test.answers.append(answer)
        ResultTestController().add_answer(self.result_test.id, answer)

    def to_next_question(self):
        if self._question_index >= 0:
            self.save_question()
        self._question_index += 1
        if len(self.test.questions) == self._question_index:
            self.end_run_time = time.time()
            self.result_test = ResultTestController().complete_test(self.result_test.id)
            self.is_running_test = False
            self._change_complition_time()
            self._destroy_timer()
            self.is_need_open_result = show_msg_question("Тест завершен", "Тест пройден. Перейти к результатам?")
            self.close()
            return
        self._create_question_widget(self._question_index)

    def on_get_theory_clicked(self):
        self.stacked_widget.setCurrentIndex(1)

    def on_get_default_window_clicked(self):
        self.stacked_widget.setCurrentIndex(0)

    def on_running_test(self):
        if show_msg_question("Начать тест", "Вы уверены что хотите начать тест?"):
            self.result_test = ResultTestController().start_test(self.test.id)
            self.test = self.result_test.test
            self.is_running_test = True
            self.start_test_time = self.start_run_time = time.time()
            if self.test.complition_time:
                self._create_timer(msec=self.completion_time * 1000 - 50,
                                   update_slot=self._change_complition_time,
                                   timeout_slot=self._on_timeout_running_test)
            self.to_next_question()

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        if self.is_running_test and not show_msg_question(
                "Тест уже запущен",
                "Вы уже запустили тест. Если вы выйдете, произойдет завершение теста. Продолжить?"):
            event.ignore()
        else:
            if self.is_running_test:
                self.save_question()
                ResultTestController().complete_test(self.result_test.id)
            event.accept()


class ViewResultTestQuestion(QWidget):
    def __init__(self, result_test: ResultTest, parent: QWidget = None, show_answer: bool = False):
        super().__init__(parent)
        self.setWindowTitle(f'Просмотр ответов на тест "{result_test.test.name}"')
        self.result_test = result_test
        self.theory_widget = TheoryViewWidget(self.result_test.test.theory)
        self.theory_widget.show()
        self.answers = result_test.answers
        if not show_answer:
            show_answer = result_test.test.show_answer

        self.stacked_layout = QStackedLayout()
        for answer in self.answers:
            container = QWidget()
            form = QFormLayout(container)
            text_edit = QTextEdit(answer.question.name)
            text_edit.setReadOnly(True)
            form.addRow("Вопрос:", text_edit)
            mark = answer.mark if answer.mark is not None else "Ответ еще не проверен"
            form.addRow("Полученный балл:", self.create_readonly_line_edit(f"{mark}"))
            form.addRow("Максимальный балл:", self.create_readonly_line_edit(f"{answer.question.weight}"))
            form.addRow("Время прохождения:", self.create_readonly_line_edit(f"{answer.complition_time}"))
            if answer.text_answer:
                form.addRow("Полученный ответ:", self.create_readonly_line_edit(answer.text_answer))
            if isinstance(answer.question, QuestionInputAnswer) and show_answer:
                form.addRow("Правильный ответ:",
                            self.create_readonly_line_edit(answer.question.correct_answer))
            if isinstance(answer.question, QuestionChoice):
                for test_answer in answer.question.answers_test:
                    is_checked = test_answer in answer.answers_test
                    correct = "Правильный ответ" if test_answer.is_correct else "Неправильный ответ"
                    check_box = QCheckBox(test_answer.text)
                    check_box.setChecked(is_checked)
                    check_box.setDisabled(True)
                    if show_answer:
                        form.addRow(check_box, QLabel(correct))
                    else:
                        form.addRow(check_box)
            self.stacked_layout.addWidget(container)

        header = QFrame()
        header.setObjectName("menuTest")
        hl = QHBoxLayout(header)
        self.label_number_of_question = QLabel()
        self.update_label_question()
        hl.addWidget(self.label_number_of_question)

        hlayout = QHBoxLayout()
        self.btn_to_next = QPushButton("Следующий вопрос")
        self.btn_to_next.clicked.connect(self.on_clicked_to_next)
        self.btn_to_prev = QPushButton("Предыдущий вопрос")
        self.btn_to_prev.clicked.connect(self.on_clicked_to_prev)
        hlayout.addWidget(self.btn_to_prev)
        hlayout.addWidget(self.btn_to_next)

        vl = QVBoxLayout(self)
        vl.addWidget(header)
        vl.addLayout(self.stacked_layout)
        vl.addLayout(hlayout)
        self.index_question = 0

    @property
    def index_question(self) -> int:
        return self.stacked_layout.currentIndex()

    @index_question.setter
    def index_question(self, value: int):
        if 0 <= value < self.stacked_layout.count():
            self.theory_widget.set_to_pointer(self.answers[value].question.pointer)
            self.stacked_layout.setCurrentIndex(value)
            self.update_label_question()
            self.btn_to_next.setDisabled(value + 1 == self.stacked_layout.count())
            self.btn_to_prev.setDisabled(value == 0)

    def update_label_question(self):
        self.label_number_of_question.setText(f"Вопрос {self.index_question + 1} из {len(self.answers)}")

    def on_clicked_to_next(self):
        self.index_question += 1

    def on_clicked_to_prev(self):
        self.index_question -= 1

    @staticmethod
    def create_readonly_line_edit(text: str):
        result = QLineEdit(text)
        result.setReadOnly(True)
        return result

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.theory_widget.close()
        a0.accept()


class ViewResultTest(QWidget):
    changed_note = pyqtSignal(str)

    def __init__(self, result_test: ResultTest, parent: QWidget = None):
        super(ViewResultTest, self).__init__(parent)
        self.result_test = result_test
        self.is_allowed_show_answer = False
        self.font_legends = QFont("Calibri", 11)
        self.font_titles = QFont("Calibri", 14)
        self.current_mark_color: Tuple[QPen, QColor] = (QPen(Qt.darkGreen, 2), Qt.green)
        self.wrong_mark_color: Tuple[QPen, QColor] = (None, Qt.GlobalColor.darkMagenta)
        self.not_check_mark_color: Tuple[QPen, QColor] = (None, Qt.darkGray)

        self.setWindowTitle("Результат теста")
        layout = QVBoxLayout(self)
        current_mark = sum((i.mark for i in result_test.answers if i.mark), start=0)
        all_mark = sum((i.weight for i in result_test.test.questions), start=0)
        not_check_mark = sum(i.question.weight for i in result_test.answers if i.mark is None)
        mark = "баллов"
        if current_mark % 10 == 1 and current_mark != 11:
            mark = "балл"
        elif 2 <= current_mark % 10 <= 4 and not 12 <= current_mark <= 14:
            mark = "балла"
        not_check_questions = [i.question for i in result_test.answers if i.mark is None]
        date = "Еще не пройден"
        if self.result_test.completed_date is not None:
            date = self.result_test.completed_date.strftime("%d %B %Y год %X")
        percent = current_mark / all_mark if all_mark != 0 else 0.0
        layout.addWidget(
            QLabel(f"Набрано {current_mark} {mark} из {all_mark}. В процентах: {percent * 100:.2f}%\n"
                   f"Вопросов ожидающих проверки: {len(not_check_questions)}. "
                   f"В баллах {sum(i.weight for i in not_check_questions)}\n"
                   f"Общее время прохождения: {sum_time(i.complition_time for i in result_test.answers)}\n"
                   f"Когда был пройден тест: {date}"))

        form = QFormLayout()
        self.note_line_edit = QLineEdit(self.result_test.note if self.result_test.note else "")
        self.btn_to_save_note = QPushButton("Сохранить примечание")
        self.btn_to_save_note.clicked.connect(self.save_note)
        form.addRow("Примечание для создателя теста:", self.note_line_edit)
        form.addWidget(self.btn_to_save_note)

        hlayout = QHBoxLayout(self)
        btn_view_result_question = QPushButton("Подробнее")
        btn_view_result_question.clicked.connect(self.view_result_question)
        hlayout.addWidget(btn_view_result_question, alignment=Qt.AlignRight)
        hl = QHBoxLayout()
        hl.setContentsMargins(0, 0, 0, 0)
        hl.addWidget(self.create_pie(current_mark, not_check_mark, all_mark))
        hl.addWidget(self.create_bar())
        layout.addLayout(hl)
        layout.addLayout(form)
        layout.addLayout(hlayout)
        self.setLayout(layout)
        self.setMinimumSize(1000, int(1000 / 16 * 9))

    @staticmethod
    def set_style(element, style, include_pen=True):
        if style[0] and include_pen:
            element.setPen(style[0])
        if style[1]:
            element.setBrush(style[1])

    def create_pie(self, current_mark, nocheck_mark, all_mark, anim: QChart.AnimationOption = QChart.SeriesAnimations):
        series = QPieSeries()
        series.append(f"Набранные баллы", current_mark)
        series.append("Упущенные баллы", all_mark - current_mark - nocheck_mark)
        series.append("Непроверенные баллы", nocheck_mark)

        # adding slice
        slice_ = series.slices()[0]
        slice_.setExploded(True)
        slice_.setLabelVisible(True)
        self.set_style(slice_, self.current_mark_color)
        self.set_style(series.slices()[1], self.wrong_mark_color)
        self.set_style(series.slices()[2], self.not_check_mark_color)

        chart = QChart()
        chart.addSeries(series)
        chart.setAnimationOptions(anim)
        chart.setTitle("Распределение баллов")
        chart.legend().setFont(self.font_legends)
        chart.setTitleFont(self.font_titles)
        chart.legend().setAlignment(Qt.AlignBottom)

        chartview = QChartView(chart)
        chartview.setRenderHint(QPainter.Antialiasing)
        return chartview

    @staticmethod
    def get_marks(answers: list[Answer]) -> tuple[int, int, int]:
        current_mark = sum(i.mark for i in answers if i.mark)
        all_mark = sum(i.question.weight for i in answers)
        not_check_mark = sum(i.question.weight for i in answers if i.mark is None)
        return current_mark, all_mark - current_mark - not_check_mark, not_check_mark

    def create_bar(self, anim: QChart.AnimationOptions = QChart.SeriesAnimations):
        set0 = QBarSet("Набранные баллы")
        set1 = QBarSet("Упущенные баллы")
        set2 = QBarSet("Непроверенные баллы")
        self.set_style(set0, self.current_mark_color, False)
        self.set_style(set1, self.wrong_mark_color, False)
        self.set_style(set2, self.not_check_mark_color, False)

        answers0 = [i for i in self.result_test.answers if isinstance(i.question, QuestionChoice)]
        answers1 = [i for i in self.result_test.answers if isinstance(i.question, QuestionInputAnswer)]
        answers2 = [i for i in self.result_test.answers if isinstance(i.question, QuestionNotCheck)]

        res = []
        for i in zip(self.get_marks(answers0), self.get_marks(answers1), self.get_marks(answers2)):
            res.append(i)
        set0.append(res[0])
        set1.append(res[1])
        set2.append(res[2])

        series = QPercentBarSeries()
        series.append(set0)
        series.append(set1)
        series.append(set2)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Баллы по разным типам вопросов")
        chart.setAnimationOptions(anim)

        categories = ["с вариантами ответов", "с вводимым ответом", "с ручной проверкой"]
        axis = QBarCategoryAxis()
        axis.append(categories)
        chart.createDefaultAxes()
        chart.setAxisX(axis, series)

        chart.legend().setVisible(True)
        chart.legend().setFont(self.font_legends)
        chart.setTitleFont(self.font_titles)
        chart.legend().setAlignment(Qt.AlignBottom)

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        return chart_view

    def allow_show_answer(self, value: bool):
        self.is_allowed_show_answer = value

    def view_result_question(self):
        self.current_widget = ViewResultTestQuestion(self.result_test, show_answer=self.is_allowed_show_answer)
        self.current_widget.show()

    def save_note(self):
        if self.result_test.note != self.note_line_edit.text():
            self.result_test.note = self.note_line_edit.text()
            self.changed_note.emit(self.result_test.note)
            ResultTestController().save_note(self.result_test.id, self.result_test.note)


class PercentDelegate(QStyledItemDelegate):
    def displayText(self, value, locale_):
        if isinstance(value, (int, float)):
            return locale_.toString(value * 100, "f", 2) + "%"
        return super().displayText(value, locale_)


class ViewResultsTests(QTableWidget):
    def __init__(self, user: User, view_created_tests: bool, dict_theories=None, parent: QWidget = None):
        super().__init__(parent)
        self.dict_theories = dict_theories
        self.verify_widget: VerifyNotCheckQuestions = None
        self.current_test_widget: Optional[ViewResultTest] = None
        self.current_user = user
        self.view_created_tests = view_created_tests
        self.results_tests = []
        self.upd()

    def upd(self):
        self.results_tests = []
        self.verify_widget = None
        self.setSortingEnabled(False)
        self.setSortingEnabled(True)
        self.setMinimumWidth(600)

        if self.view_created_tests:
            self.setWindowTitle("Результаты прохождения созданных тестов")
        else:
            self.setWindowTitle("Результаты тестов")

        self.verticalHeader().sectionClicked.connect(self.open_result_test)
        headers = [
            "Номер",
            "Дата прохождения",
            "Тест",
            "Балл",
            "Процент выполнения",
            "Время прохождения",
            "Примечание",
            "Ручная проверка",
        ]
        self.setItemDelegateForColumn(4, PercentDelegate(self))
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        self.setSortingEnabled(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setColumnHidden(0, True)
        self.update_data()

    def update_data(self):
        order = self.horizontalHeader().sortIndicatorOrder()
        section = self.horizontalHeader().sortIndicatorSection()
        self.setSortingEnabled(False)
        self.setRowCount(0)
        if self.view_created_tests:
            self.results_tests = list(reversed(list(ResultTestController().get_result_test_by_created_test_in_easy_format())))
        else:
            self.results_tests = list(reversed(list(ResultTestController().get_result_test_by_user_in_easy_format())))
        for row, result_test in enumerate(self.results_tests):
            self.insertRow(row)
            self.update_row(row, result_test)
        self.setSortingEnabled(True)
        self.horizontalHeader().setSortIndicator(section, order)

    def update_row(self, row, result_test: ResultTestEasy):
        self.removeCellWidget(row, 7)
        self.setItem(row, 0, QTableWidgetItem(f"{row}"))
        self.setItem(row, 1, QTableWidgetItem(
            result_test.completed_date.strftime("%c") if result_test.completed_date is not None else "Еще не пройден"))
        self.setItem(row, 2, QTableWidgetItem(result_test.name_test))

        item = QTableWidgetItem()
        item.setData(Qt.EditRole, result_test.mark)
        self.setItem(row, 3, item)

        k = result_test.mark / result_test.all_mark if result_test.all_mark != 0 else 0.0
        item = QTableWidgetItem()
        item.setData(Qt.EditRole, k)
        self.setItem(row, 4, item)

        self.setItem(row, 5, QTableWidgetItem(f"{result_test.complition_time}"))
        self.setItem(row, 6, QTableWidgetItem(result_test.note))

        if result_test.checked and self.view_created_tests:
            item = QWidget()
            layout = QHBoxLayout(item)
            layout.setContentsMargins(0, 0, 0, 0)
            btn = QPushButton("Проверить")
            btn.setStyleSheet("padding: 2px;")
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            btn.row = row
            btn.clicked.connect(self.open_questions_not_check)
            layout.addWidget(btn)
            self.setItem(row, 7, QTableWidgetItem("Не проверено"))
            self.setCellWidget(row, 7, item)
        elif result_test.checked:
            self.setItem(row, 7, QTableWidgetItem("Не проверено"))
        else:
            self.setItem(row, 7, QTableWidgetItem("Проверено"))

    @property
    def result_test(self):
        return self.results_tests[int(self.item(self.horizontalHeader().currentIndex().row(), 0).data(Qt.EditRole))]

    def open_questions_not_check(self):
        row = self.sender().row
        result_test = ResultTestController().get_by_id(self.results_tests[row].id)
        self.verify_widget = VerifyNotCheckQuestions(result_test)
        self.verify_widget.show()
        self.verify_widget.verifyed.connect(self.upd)

    def update_note(self, note: str):
        self.item(self.horizontalHeader().currentIndex().row(), 6).setText(note)

    def open_result_test(self):
        rt = ResultTestController().get_by_id(self.result_test.id)
        rt.test.theory = self.dict_theories[rt.test.theory.id]
        self.current_test_widget = ViewResultTest(rt)
        if rt.user.id != self.current_user.id:
            self.current_test_widget.note_line_edit.setReadOnly(True)
        if self.view_created_tests:
            self.current_test_widget.allow_show_answer(True)
        self.current_test_widget.show()
        self.current_test_widget.changed_note.connect(self.update_note)


class VerifyNotCheckQuestions(QWidget):
    verifyed = pyqtSignal()

    def __init__(self, result_test: ResultTest, parent: QWidget = None):
        super().__init__(parent)
        self.setWindowTitle(f'Ручная проверка теста "{result_test.test.name}"')
        self.result_test = result_test
        self.answers = [a for a in result_test.answers if a.mark is None]
        assert len(self.answers), "Должен быть хотя бы один непроверенный ответ"
        self.index_answer = 0
        self._create_widget()

    def _create_widget(self):
        if self.layout():
            QWidget().setLayout(self.layout())
        answer = self.answers[self.index_answer]

        form = QFormLayout()
        te = QTextEdit(answer.question.name)
        te.setReadOnly(True)
        form.addRow("Вопрос:", te)
        le = QLineEdit(answer.text_answer)
        le.setReadOnly(True)
        form.addRow("Введенный ответ:", le)
        self.mark_spin_box = QSpinBox()
        self.mark_spin_box.setMaximum(answer.question.weight)
        self.mark_spin_box.setMinimum(-1)
        self.mark_spin_box.setValue(-1)
        form.addRow("Выставленный балл:", self.mark_spin_box)

        header = QFrame()
        header.setObjectName("menuTest")
        hl = QHBoxLayout(header)
        self.label_number_of_question = QLabel()
        self.label_weight_of_question = QLabel()
        self.update_label()
        hl.addWidget(self.label_number_of_question)
        hl.addWidget(self.label_weight_of_question, alignment=Qt.AlignRight)

        self.btn_verify = QPushButton("Выставить балл за вопрос")
        self.btn_verify.clicked.connect(self.on_clicked_to_next)

        layout = QVBoxLayout(self)
        layout.addWidget(header)
        layout.addLayout(form)
        layout.addWidget(self.btn_verify)

    def update_label(self):
        self.label_number_of_question.setText(f"Вопрос {self.index_answer + 1} из {len(self.answers)}")
        self.label_weight_of_question.setText(f"Максимальный балл: {self.answers[self.index_answer].question.weight}")

    def update_button(self):
        if self.index_answer + 1 == len(self.answers):
            self.btn_verify.setText("Выставить балл за вопрос и завершить проверку")

    def on_clicked_to_next(self):
        if self.mark_spin_box.value() < 0:
            show_msg_information("Не выставлен балл за ответ",
                                 "Прежде чем перейти к следующему вопросу выставите балл за этот вопрос")
            return
        self.answers[self.index_answer].mark = self.mark_spin_box.value()
        self.index_answer += 1
        if self.index_answer == len(self.answers):
            ResultTestController().set_marks_for_answers(self.answers)
            self.close()
            self.verifyed.emit()
            return
        self._create_widget()
        self.update_button()


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.dict_theories: dict[str, Theory] = {}
        self.user = None
        self.current_test_widget = None
        self.other_results_tests = []
        self.my_results_tests = []
        self.model_created_tests = QStandardItemModel()
        self.model_my_results_tests = QStandardItemModel()
        self.model_other_results_tests = QStandardItemModel()
        self.created_test_widget = None
        self.completed_test_widget = None
        self.__new_window = None  # Для игнорирования сборщиком мусора новых окон
        self.menu_run_test: Optional[QMenu] = None
        self.tests = []
        self.create_test_widget = None
        self.menu_update_theories = None
        self.theories = None
        self.theory = None
        self.menu = None

        self.initUI()
        self.update_data()
        # Thread(target=lambda: asyncio.run(self.async_update()), daemon=True).start()

        is_auto_update = False
        if is_auto_update:
            self.timer_update = QTimer(self)
            self.timer_update.start(3000)
            self.timer_update.setSingleShot(False)
            self.timer_update.timeout.connect(self.update_data)

    def init_menu(self):
        self.menu = QMenuBar(self)

        view_result_finish_tests = QAction("Просмотреть результаты пройденных тестов", self)
        view_result_finish_tests.triggered.connect(self.show_results_completed_tests)
        view_result_created_tests = QAction("Просмотреть результаты ваших тестов", self)
        view_result_created_tests.triggered.connect(self.show_results_created_tests)
        menu_results = QMenu("Результаты тестов", self)
        menu_results.addAction(view_result_finish_tests)
        menu_results.addAction(view_result_created_tests)

        create_test = QAction("Создать новый тест", self)
        create_test.triggered.connect(self.create_test)

        self.menu_run_test = QMenu("Пройти тест", self)
        menu_tests = QMenu("Тест", self)
        menu_tests.addAction(create_test)
        menu_tests.addMenu(self.menu_run_test)

        add_theory_action = QAction("Добавить теоретический материал", self)
        add_theory_action.triggered.connect(self.show_theory_window)
        self.menu_update_theories = QMenu("Изменить существующие теории", self)
        menu_add_theory = QMenu("Теоретический материал", self)
        menu_add_theory.addAction(add_theory_action)
        menu_add_theory.addMenu(self.menu_update_theories)

        self.menu.addMenu(menu_tests)
        self.menu.addMenu(menu_results)
        self.menu.addMenu(menu_add_theory)

    def initUI(self):
        self.init_menu()
        main_splitter = QSplitter()

        list_created_tests = QListView()
        list_created_tests.setObjectName("listView")
        list_created_tests.setModel(self.model_created_tests)
        list_created_tests.clicked[QModelIndex].connect(self.on_run_test)

        list_my_results_tests = QListView()
        list_my_results_tests.setObjectName("listView")
        list_my_results_tests.setModel(self.model_my_results_tests)
        list_my_results_tests.clicked[QModelIndex].connect(lambda index: self.on_show_result_test(False, index))

        list_other_results_tests = QListView()
        list_other_results_tests.setObjectName("listView")
        list_other_results_tests.setModel(self.model_other_results_tests)
        list_other_results_tests.clicked[QModelIndex].connect(lambda index: self.on_show_result_test(True, index))

        main_splitter.addWidget(self._create_widget_with_list_and_header(
            list_my_results_tests, QLabel("Результаты пройденных тестов")))
        main_splitter.addWidget(self._create_widget_with_list_and_header(
            list_other_results_tests, QLabel("Результаты созданых тестов")))
        main_splitter.addWidget(self._create_widget_with_list_and_header(list_created_tests, QLabel("Доступные тесты")))

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(main_splitter)
        layout.setMenuBar(self.menu)

        self.setWindowTitle("Платформа для создания и проверки тестов")
        self.setMinimumSize(700, 360)

    def on_run_test(self, index: QModelIndex):
        test = self.tests[index.row()]
        widget = RunTestWidget(test)
        return widget.exec_()

    def on_show_result_test(self, view_created_tests: bool, index: QModelIndex):
        rt = self.other_results_tests[index.row()] if view_created_tests else self.my_results_tests[index.row()]
        rt = ResultTestController().get_by_id(rt.id)
        rt.test.theory = self.dict_theories[rt.test.theory.id]
        self.current_test_widget = ViewResultTest(rt)
        if rt.user.id != self.user.id:
            self.current_test_widget.note_line_edit.setReadOnly(True)
        if view_created_tests:
            self.current_test_widget.allow_show_answer(True)
        self.current_test_widget.show()

    def update_data(self):
        self.load_theories()
        self.update_tests()
        self.update_model_other_results_tests()
        self.update_model_my_results_tests()
        self.user = QtHttpClientController(platform.node()).get("/", User)

    async def async_update(self):
        while True:
            self.update_model_my_results_tests()
            self.update_model_other_results_tests()
            await asyncio.sleep(1)

    def update_tests(self):
        prev_tests = set(test.id for test in self.tests)
        self.tests.extend(i for i in TestController().get_available_test() if i.id not in prev_tests)
        if len(prev_tests) == len(self.tests) and self.menu_run_test.actions():
            return
        self.menu_run_test.clear()
        for test in self.tests:
            test.theory = self.dict_theories[test.theory.id]
            action = QAction(test.name, self)
            action.test = test
            action.triggered.connect(self.run_test)
            self.menu_run_test.addAction(action)
        add_test = QAction("Добавить уже существующий тест", self)
        add_test.triggered.connect(self.add_exist_test)
        self.menu_run_test.addAction(add_test)
        self.update_model_created_tests()

    def update_model_created_tests(self):
        self.model_created_tests.clear()
        for test in self.tests:
            item = QStandardItem(test.name)
            item.setEditable(False)
            self.model_created_tests.appendRow(item)

    @staticmethod
    def _create_header(*widgets):
        header = QFrame()
        header.setObjectName("menuTest")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(2, 2, 2, 2)
        for widget in widgets:
            hl.addWidget(widget)
        return header

    def _create_widget_with_list_and_header(self, list_view: QListView, *widgets):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._create_header(*widgets))
        layout.addWidget(list_view)
        return widget

    def _create_test_item(self, result_test: ResultTestEasy):
        item = QStandardItem()
        self._set_text_test_item(item, result_test)
        item.setEditable(False)
        return item

    @staticmethod
    def _set_text_test_item(item: QStandardItem, result_test: ResultTestEasy):
        note = result_test.note if result_test.note is not None else ""
        date = result_test.completed_date if result_test.completed_date is not None else datetime.datetime.min
        text = f"{result_test.name_test}: {date:%c} - {note}"
        if text != item.text():
            item.setText(text)

    def update_model_my_results_tests(self):
        ids = {i.id for i in self.my_results_tests}
        prev = [i for i in ResultTestController().get_result_test_by_user_in_easy_format() if i.id not in ids]
        for result_test in prev:
            self.model_my_results_tests.appendRow(self._create_test_item(result_test))
            self.my_results_tests.append(result_test)
        for i, result_test in enumerate(self.my_results_tests):
            self._set_text_test_item(self.model_my_results_tests.item(i, 0), result_test)

    def update_model_other_results_tests(self):
        ids = {i.id for i in self.other_results_tests}
        prev = [i for i in ResultTestController().get_result_test_by_created_test_in_easy_format() if i.id not in ids]
        for result_test in prev:
            self.model_other_results_tests.appendRow(self._create_test_item(result_test))
            self.other_results_tests.append(result_test)
        for i, result_test in enumerate(self.other_results_tests):
            self._set_text_test_item(self.model_other_results_tests.item(i, 0), result_test)

    def load_theories(self):
        prev_theories = self.theories
        self.theories = TheoryController().get_created_theories()
        if self.theories == prev_theories:
            return
        self.menu_update_theories.clear()
        self.dict_theories.clear()
        for theory in self.theories:
            self.dict_theories[theory.id] = theory
            action = QAction(theory.name, self)
            action.theory = theory
            action.triggered.connect(self.show_theory_window_for_update)
            self.menu_update_theories.addAction(action)

    def show_results_created_tests(self):
        self.created_test_widget = ViewResultsTests(self.user, True, self.dict_theories)
        self.created_test_widget.show()

    def show_results_completed_tests(self):
        self.completed_test_widget = ViewResultsTests(self.user, False, self.dict_theories)
        self.completed_test_widget.show()

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
        self.create_test_widget.created_test.connect(self.update_tests)

    def add_exist_test(self):
        widget = QInputDialog(self)
        widget.setWindowTitle("Добавить тест по id")
        widget.setLabelText("Введите id теста, который дал вам создатель теста:")
        widget.show()
        if widget.exec_():
            try:
                res = TestController().get_by_id(uuid.UUID(widget.textValue()))
            except Exception:
                res = None
            if res is not None:
                self.tests.append(res)
                self.update_tests()
            else:
                show_msg_information(
                    "Не найден тест",
                    "Извините но по данному айди не нашлось теста. Перепроверте тест и попробуйте снова")

    def run_test(self):
        if self.theory:
            self.theory.close()
        widget = RunTestWidget(self.sender().test, self)
        widget.exec()
        if widget.is_need_open_result:
            widget.result_test.test.theory = self.dict_theories[widget.result_test.test.theory.id]
            self.__new_window = ViewResultTest(widget.result_test)
            self.__new_window.show()


if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
    translator = QTranslator()
    translator.load("resource/qt_ru.qm")
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(resource_path("resource/app_icon.ico")))
    app.setStyle("Fusion")
    app.installTranslator(translator)
    res_path = resource_path("Toolery.qss")
    path = res_path if os.path.exists(res_path) else os.path.join("desktop_app", res_path)
    with open(path, "r") as f:
        app.setStyleSheet(f.read())
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
