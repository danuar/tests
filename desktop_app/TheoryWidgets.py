import datetime
import re
from typing import Optional

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QColor, QTextCursor, QTextCharFormat
from PyQt5.QtWidgets import QTextEdit, QMenu, QTabWidget, QWidget, QAction, QLineEdit, QFormLayout, QSpinBox, \
    QPushButton, QHBoxLayout, QVBoxLayout

from desktop_app.Controllers.TheoryController import TheoryController
from desktop_app.MessageBox import *
from desktop_app.Models import Theory, ChapterTheory, PointerToAnswer


class TextEditPointer(QTextEdit):
    def __init__(self, *__args):
        super().__init__(*__args)

    def contextMenuEvent(self, e):
        menu: QMenu = self.createStandardContextMenu()
        for action in self.actions():
            menu.addAction(action)
        menu.exec_(e.globalPos())
        menu.deleteLater()


class TheoryViewWidget(QTabWidget):
    added_pointer_to_answer = pyqtSignal(QTextCursor)

    def __init__(self, theory: Optional[Theory] = None,
                 parent: QWidget = None, background_answer: QColor = QColor(0, 255, 0)):
        super().__init__(parent)
        self.prev_format_answer = None
        self.theory = theory
        self.setMinimumSize(int(300 * 16 / 9), 300)
        self.background_color_answer = background_answer
        self.cursor: Optional[QTextCursor] = None
        self.add_pointer_action = QAction("Пометить выделенную область как ответ")
        self.add_pointer_action.setShortcut("Ctrl+S")
        self.add_pointer_action.triggered.connect(self._add_pointer_to_answer)
        if theory:
            self.setWindowTitle(theory.name)
            for chapter in theory.chapters:
                widget = TextEditPointer(chapter.content)
                widget.setReadOnly(True)
                widget.copyAvailable.connect(self.add_pointer_action.setEnabled)
                widget.addAction(self.add_pointer_action)
                self.addTab(widget, chapter.name)

    def _add_pointer_to_answer(self):
        widget: TextEditPointer = self.currentWidget()
        cursor: QTextCursor = widget.textCursor()
        cursor.chapter = self.theory.chapters[self.currentIndex()]
        self.add_cursor(cursor)
        self.added_pointer_to_answer.emit(cursor)

    def set_to_pointer(self, ptr: PointerToAnswer):
        index = [i.id for i in self.theory.chapters].index(ptr.chapter.id)
        self.setCurrentIndex(index)
        cursor = QTextCursor(self.currentWidget().document())
        cursor.setPosition(ptr.start, QTextCursor.MoveAnchor)
        cursor.setPosition(ptr.end, QTextCursor.KeepAnchor)
        self.add_cursor(cursor)
        result_text = cursor.selectedText()
        c = QTextCursor(cursor)
        c.clearSelection()
        self.currentWidget().setTextCursor(c)
        return result_text

    def add_cursor(self, cursor: QTextCursor):
        self.remove_cursor()
        self.cursor = cursor
        self.prev_format_answer = self.cursor.charFormat()
        self._set_background_selected_text(self.background_color_answer)

    def remove_cursor(self):
        if self.prev_format_answer is not None:
            self.cursor.setCharFormat(self.prev_format_answer)
        self.cursor = None
        self.prev_format_answer = None

    def _set_background_selected_text(self, color: QColor):
        format_answer = QTextCharFormat()
        if color.rgb() != QColor().rgb():
            format_answer.setBackground(color)
        else:
            format_answer.clearBackground()
        self.cursor.mergeCharFormat(format_answer)

    @property
    def current_cursor(self) -> Optional[QTextCursor]:
        return self.cursor


class TheoryTabWidget(QWidget):
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
            self.tabs_chapters.addTab(TextEditPointer(), self.name_chapter.text().rstrip())
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
            m = self.study_time.value()
            study_time = datetime.time(hour=m // 60, minute=m % 60)
            if self.updated_theory is None:
                names = []
                chapters = []
                for i in range(self.tabs_chapters.count()):
                    names.append(self.tabs_chapters.tabText(i))
                    chapters.append(self.tabs_chapters.widget(i).toHtml())

                TheoryController().create_theory(Theory(
                    name=self.name_theory.text(),
                    study_time=datetime.time.isoformat(study_time), chapters=[
                        ChapterTheory(name=name, content=content) for name, content in zip(names, chapters)]))
            else:
                self.updated_theory.name = self.name_theory.text()
                if self.study_time.value() <= 0:
                    self.updated_theory.study_time = None
                else:
                    self.updated_theory.study_time = datetime.time.isoformat(study_time)
                print(self.updated_theory.chapters, self.updated_theory.chapters is None)
                if self.updated_theory.chapters is None:
                    self.updated_theory.chapters = []
                ln = len(self.updated_theory.chapters)
                self.updated_theory.chapters = []
                for i in range(ln, self.tabs_chapters.count()):
                    chapter = ChapterTheory(name=self.tabs_chapters.tabText(i), content=self.tabs_chapters.widget(i).toHtml())
                    self.updated_theory.chapters.append(chapter)
                TheoryController().update_theory(self.updated_theory)
            self.changedTheories.emit()
            t = "изменен" if self.updated_theory else "создан"
            show_msg_information("Теория", f"Теоретический материал успешно {t}")
            self.close()
