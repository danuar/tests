import abc
from typing import Union

from PyQt5.QtWidgets import QFormLayout, QLineEdit, QCheckBox, QPushButton, QHBoxLayout, QDoubleSpinBox

from db import Question, QuestionChoise, QuestionInputAnswer, QuestionNotCheck, AnswerTest
from desktop_app.MessageBox import *


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
    def create_entity(self, question: Question):
        pass

    @classmethod
    def setup_all(cls, number: int):
        return cls.instanses[number].setup()

    @classmethod
    def check_all(cls, number: int):
        return cls.instanses[number].check()

    @classmethod
    def create_specify_entity(cls, number_type: int, question: Question) -> \
            Union[QuestionChoise, QuestionInputAnswer, QuestionNotCheck]:
        return cls.instanses[number_type].create_entity(question)

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

    def create_entity(self, question) -> QuestionChoise:
        result = QuestionChoise(question=question)
        for i in range(self.form.rowCount() - 1):
            layout = self.form.itemAt(i, QFormLayout.FieldRole)
            line_edit: QLineEdit = layout.itemAt(0).widget()
            check_box: QCheckBox = layout.itemAt(1).widget()
            result.answers.append(AnswerTest(text=line_edit.text(), correct=check_box.isChecked()))
        return result

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
            return bool(show_msg_question("Полностью непохожие ответы",
                                          "У вас выставлена 0 схожесть ответов. Это значит, что любой ответ будет "
                                          "считаться правильным. Вы уверены что хотите продолжить?"))
        return True

    def create_entity(self, question) -> QuestionInputAnswer:
        return QuestionInputAnswer(
            question=question,
            k_misspell=self.form.itemAt(0, QFormLayout.FieldRole).widget().value() / 100,
            correct_answer=self.form.itemAt(1, QFormLayout.FieldRole).widget().text(),
        )


class ViewQuestionNotCheck(ViewQuestion):
    def __init__(self, form: QFormLayout):
        super().__init__(form)

    def setup(self):
        return

    def check(self):
        return True

    def create_entity(self, question) -> QuestionNotCheck:
        return QuestionNotCheck(question=question)

