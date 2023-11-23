import logging
from typing import Optional, List

from sqlalchemy.orm import Session

import config
from db import *
from solve_resource_one_exe import resource_path


class Context:
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        engine_psql = create_engine(
            f'postgresql://{config.DATABASE_USER}:{config.DATABASE_PASSWORD}'
            f'@{config.DATABASE_HOST}:{config.DATABASE_PORT}/{config.DATABASE_NAME}',
            pool_pre_ping=True,
        )
        self.session = Session(bind=engine_psql)
        self.session.expire_on_commit = False


class UserLogic:
    name_file_with_id = resource_path("user_id.txt")
    user = None

    @classmethod
    def setup_user(cls, ident: Optional[uuid.UUID] = None) -> None:
        if cls.user is not None:
            return
        c = Context()
        if ident is None:
            cls.user = User()
            c.session.add(cls.user)
            c.session.commit()
            logging.info(f"Создан новый пользователь: {cls.user.id}")
        else:
            cls.user = c.session.query(User).get(ident)
            if cls.user is not None:
                logging.info(f"Найден пользователь: {cls.user.id}")
            else:
                cls.user = User(id=ident)
                c.session.add(cls.user)
                c.session.commit()
                logging.info(f"Создан пользователь по id={cls.user.id}")

        if cls.user is None:
            c.session.add(User(id=ident))

    @classmethod
    def setup_user_from_file(cls):
        try:
            with open(cls.name_file_with_id, 'r') as f:
                cls.setup_user(uuid.UUID(f.readline()))
        except (FileNotFoundError, ValueError):
            cls.setup_user()
            with open(cls.name_file_with_id, 'w') as f:
                f.write(cls.user.id.__str__())


class TheoryLogic:
    path_to_save_chapters = "../chapters/"

    def create(self, name_theory: str, study_time_minuts: int, names_chapters: List[str], texts_chapters):
        session = Context().session
        logging.info(f"Создание теории: {name_theory}")
        theory = Theory(name=name_theory)
        if study_time_minuts > 0:
            theory.study_time = datetime.time(minute=study_time_minuts)
        session.add(theory)
        session.commit()
        self.add_chapters(theory, names_chapters, texts_chapters)

    def add_chapters(self, theory: Theory, names_chapters: List[str], texts_chapters):
        logging.info(f"Добавление {len(names_chapters)} разделов в теорию {theory.name}")
        start = len(theory.chapters)
        for names_chapter in names_chapters:
            theory.chapters.append(ChapterTheory(name=names_chapter))
        Context().session.commit()

        for i in range(start, len(theory.chapters)):
            chapter = theory.chapters[i]
            with open(f"{self.path_to_save_chapters}{chapter.id}.html", "x", encoding="utf-8") as f:
                f.write(texts_chapters[i - start])
            logging.info(f"Произошла запись в файл: '{chapter.id}.html' раздела: {chapter.name}")

    def get_all(self):
        return Context().session.query(Theory).all()

    def load_chapters_from_theory(self, theory) -> tuple[list[str], list[str]]:
        names = []
        chapters = []
        for chapter in theory.chapters:
            try:
                with open(f"{self.path_to_save_chapters}{chapter.id}.html", "r", encoding="utf-8") as f:
                    chapters.append(f.read())
                names.append(chapter.name)
            except FileNotFoundError:
                logging.warning(f"При попытке получить раздел теории {chapter.name}, не был найден файл"
                                f" {self.path_to_save_chapters}{chapter.id}.html")
            except UnicodeDecodeError as e:
                logging.error(f"У {f.name} неподдерживаемая кодировка. Новая кодировка: {f.encoding}", exc_info=e)
        return names, chapters


class TestLogic:
    def get(self, ident: uuid.UUID) -> Optional[Test]:
        try:
            return Context().session.query(Test).get(ident)
        except:
            logging.info(f"Не получилось найти тест по id {ident}")
            return None

    def create(self, test: Test):
        Context().session.add(test)
        Context().session.commit()

    def all_from_user(self) -> list[Test]:
        return Context().session.query(Test).filter(Test.creator == UserLogic.user).all()

    def get_count_attempts(self, test: Test) -> Optional[int]:
        if not test.count_attempts:
            return None
        s = Context().session
        completed_tests = s.query(ResultTest).filter(ResultTest.test == test, ResultTest.user == UserLogic.user).count()
        return max(0, test.count_attempts - completed_tests)


class ResultTestLogic:
    def create(self, result_test: ResultTest):
        Context().session.add(result_test)
        Context().session.commit()

    def save(self):
        Context().session.commit()

    def get_all_created(self) -> list[ResultTest]:
        return Context().session.query(ResultTest).join(Test).filter(Test.creator_id == UserLogic.user.id)

    def get_all_completed(self) -> list[ResultTest]:
        return Context().session.query(ResultTest).filter(ResultTest.user == UserLogic.user)

    def get(self, ident: uuid.UUID) -> ResultTest:
        return Context().session.query(ResultTest).get(ident)
