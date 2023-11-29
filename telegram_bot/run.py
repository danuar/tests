import asyncio
import difflib
import enum
import locale
import operator
import os
import sys
import time
import uuid
import datetime
import random
from functools import reduce

from PyQt5.QtChart import QChart
from PyQt5.QtWidgets import QApplication
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, MediaGroup, InputFile

from desktop_app.TheoryWidgets import TheoryViewWidget
from desktop_app.run import ViewResultTest
from logicsDB import *

bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot)
app = QApplication(sys.argv)

inline_get_theory = InlineKeyboardButton("Изучить теорию", callback_data="on_get_theory")
inline_run_test = InlineKeyboardButton("Начать прохождение теста", callback_data="on_run_test")
inline_view_questions = InlineKeyboardButton("Подробнее", callback_data="on_view_questions")
inline_set_note = InlineKeyboardButton("Оставить примечание", callback_data="on_set_note")


class TelegramUser:
    class State(enum.Enum):
        unknown = 3
        answer = 0
        answered = 1
        timeout = 2
        wait_input = 4

    def __init__(self, ident, tests: set[Test], results_tests: list[ResultTest]):
        UserLogic.user = None
        UserLogic().setup_user(uuid.uuid3(uuid.NAMESPACE_OID, str(ident)))
        self.tests = tests
        self.results_tests = results_tests
        self.tg_id = ident
        self.db_user = UserLogic.user
        self.state = self.State.unknown
        self.answer: Optional[Answer] = None
        self.answered_message: Optional[types.Message] = None
        self.msg_view_questions: Optional[types.Message] = None

    @staticmethod
    def create(tg_id: int):
        return users.setdefault(tg_id, TelegramUser(tg_id, set(), []))


users: dict[int, TelegramUser] = {}


def get_seconds(current_time: datetime.time) -> int:
    return current_time.hour * 3600 + current_time.minute * 60 + current_time.second


def get_time(seconds: int) -> datetime.time:
    return datetime.time(hour=seconds // 3600, minute=seconds // 60 % 60, second=seconds % 60)


def sum_time(times: list[datetime.time]):
    if not times:
        return 0
    return reduce(operator.add, (datetime.timedelta(hours=i.hour, minutes=i.minute, seconds=i.second) for i in times))


def filter_by_state(state: TelegramUser.State, user_id: int):
    return users.get(user_id) and users[user_id].state == state


@dp.message_handler(lambda x: filter_by_state(TelegramUser.State.answer, x.from_user.id) or
                    filter_by_state(TelegramUser.State.wait_input, x.from_user.id))
async def input_answer(message: types.Message):
    user = users[message.from_user.id]
    state = user.state
    user.state = TelegramUser.State.answered
    if state == TelegramUser.State.wait_input:
        user.answered_message = message
        return
    answer = user.answer
    await message.reply("Ответ засчитан")
    answer.text_answer = message.text
    if answer.question.question_input_answer:
        ratio = answer.question.question_input_answer.k_misspell
        result_ratio = difflib.SequenceMatcher(None, answer.text_answer,
                                               answer.question.question_input_answer.correct_answer, True).ratio()
        if result_ratio > ratio:
            answer.mark = answer.question.weight
        else:
            answer.mark = 0


@dp.poll_answer_handler(lambda x: filter_by_state(TelegramUser.State.answer, x.user.id))
async def get_answers(poll_answer: types.PollAnswer):
    user = users[poll_answer.user.id]
    user.state = TelegramUser.State.answered
    answer = user.answer
    count_correct = current_count_correct = 0
    for i, answer_test in enumerate(answer.question.question_choice.answers_test):
        if i in poll_answer.option_ids:
            answer.answers_test.append(answer_test)
            current_count_correct = current_count_correct + (1 if answer_test.correct else -1)
        if answer_test.correct:
            count_correct += 1
    if current_count_correct > 0:
        answer.mark = current_count_correct * answer.question.weight // count_correct
    else:
        answer.mark = 0


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Бот предназначеный для прохождения различных тестов созданных другими пользователями.\n"
                        "Для прохождения теста введите команду /test id, "
                        "где id идентификатор, который дал вам создатель теста.")


@dp.message_handler(Command('test'))
async def get_test(message: types.Message):
    ident = message.get_args()
    try:
        test = TestLogic().get(uuid.UUID(ident))
        user = TelegramUser.create(message.from_user.id).tests.add(test)
    except Exception as e:
        test = None
        logging.warning("Произошла ошибка при попытке получить тест: ", exc_info=e)
    if test is None:
        await message.reply("К сожалению по данному идентификатору не нашлось теста. \n\n"
                            "Перепроверьте его и попробуйте еще раз.")
        return
    logging.info(f"Получен тест: '{test.name}' по команде /test")
    t = get_seconds(test.completion_time) if test.completion_time \
        else sum(get_seconds(i.complition_time) for i in test.questions)
    txt = "Неограниченное количество попыток."
    not_available_test_text = ""
    count_attempts = TestLogic().get_count_attempts(test)
    if count_attempts == 0:
        not_available_test_text = "\nНе осталось попыток для прохождения."
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
            txt = ""

    label_info = f"Пройти тест: <b>{test.name}</b>\n" \
                 f"Вопросов: <b>{len(test.questions)}</b>\n" \
                 f"Время прохождения: <b>{t} сек.</b>\n{txt}"
    inline_get_theory.callback_data = 'on_get_theory' + str(test.id)
    inline_run_test.callback_data = 'on_run_test' + str(test.id)
    if not_available_test_text:
        inline_markup_for_test = None
    else:
        inline_markup_for_test = InlineKeyboardMarkup().add(inline_get_theory, inline_run_test)
    await message.reply(label_info + not_available_test_text, parse_mode='html', reply_markup=inline_markup_for_test)


@dp.callback_query_handler(lambda c: c.data[:13] == 'on_get_theory')
async def send_theory(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    test: Test = TestLogic().get(uuid.UUID(callback_query.data[13:]))
    study_time_text = f"\n\nПримерное время изучения *{test.theory.study_time}*" if test.theory.study_time else ""
    media_group = MediaGroup()
    for i, chapter in enumerate(test.theory.chapters):
        doc = InputFile(os.path.join(TheoryLogic.path_to_save_chapters, f"{chapter.id}.html"), chapter.name)
        if i == len(test.theory.chapters) - 1:  # Заголовок сообщения
            media_group.attach_document(doc, caption=f'Теория *{test.theory.name}*{study_time_text}',
                                        parse_mode='markdown')
        else:
            media_group.attach_document(doc)
    await bot.send_media_group(callback_query.from_user.id, media_group)


async def set_header_test(header_msg: types.Message, template_str: str, current_time: time, diff: int):
    return await header_msg.edit_text(template_str.format(datetime.datetime.combine(
        datetime.datetime.min, current_time) - datetime.timedelta(seconds=diff)), 'markdown')


@dp.callback_query_handler(lambda c: c.data[:11] == 'on_run_test')
async def run_test(info: types.CallbackQuery):
    await bot.answer_callback_query(info.id)
    test = TestLogic().get(uuid.UUID(info.data[11:]))
    count_attempts = TestLogic().get_count_attempts(test)
    if count_attempts == 0:
        await bot.send_message(info.from_user.id, "Не осталось попыток для прохождения.")
        return
    user = TelegramUser.create(info.from_user.id)
    result_test = ResultTest(test=test, user=user.db_user, completed_date=datetime.datetime.now())
    ResultTestLogic().create(result_test)
    current_time = test.completion_time
    random.shuffle(test.questions)
    cnt = len(test.questions)
    start_time = time.time()

    for i, question in enumerate(test.questions):
        user.state = TelegramUser.State.answer
        if question.complition_time:
            current_time = question.complition_time
        text_question = f"\n\nВопрос: {question.name}"
        tmp = f"Вес вопроса: *{question.weight}*\nОставшиеся время: *{{0:%X}}*\n" \
              f"Вопрос *{i + 1}* из *{cnt}* {text_question}"
        header_msg = await bot.send_message(info.from_user.id, tmp, parse_mode='markdown')
        if question.question_choice:
            poll = await bot.send_poll(info.from_user.id, question.name,
                                       options=[i.text for i in question.question_choice.answers_test],
                                       allows_multiple_answers=True,
                                       is_anonymous=False,
                                       )
        if i == 0:
            start_time = time.time()
        is_timeout = False
        user.answer = Answer(question=question)
        while True:
            diff = time.time() - start_time
            try:
                await header_msg.edit_text(tmp.format(datetime.datetime.combine(
                    datetime.datetime.min, current_time) - datetime.timedelta(seconds=diff)), 'markdown')
            except OverflowError:
                is_timeout = True
                break
            await asyncio.sleep(1)

            if diff > get_seconds(current_time):  # timeout
                is_timeout = True
                break
            if user.state == TelegramUser.State.answered:
                break
        s = int(diff)
        user.answer.complition_time = datetime.time(hour=s // 3600, minute=s // 60 % 60, second=s % 60)

        if is_timeout:
            user.answer.mark = 0
        result_test.answers.append(user.answer)
        if is_timeout and test.completion_time:
            await bot.send_message(info.from_user.id, "Упс... Время для прохождения теста закончилось.\n\n"
                                                      "Ваши ответы будут сохранены")
            break
        elif is_timeout:
            await bot.send_message(info.from_user.id, "Упс...Вы не успели ответить на этот вопрос. "
                                                      "Переходим к следующему")
            continue
    result_test.completed_date = datetime.datetime.now()
    user.results_tests.append(result_test)
    ResultTestLogic().save()

    btn = InlineKeyboardButton("Посмотреть результат", callback_data="on_view_result" + str(result_test.id))
    await bot.send_message(info.from_user.id, "Результат теста был успешно сохранен",
                           reply_markup=InlineKeyboardMarkup().add(btn))


@dp.callback_query_handler(lambda c: c.data[:14] == 'on_view_result')
async def view_result_test(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    user = TelegramUser.create(callback_query.from_user.id)
    result_test = ResultTestLogic().get(uuid.UUID(callback_query.data[14:]))
    current_mark = sum(i.mark for i in result_test.answers if i.mark)
    all_mark = sum(i.weight for i in result_test.test.questions)
    not_check_mark = sum(i.question.weight for i in result_test.answers if i.mark is None)
    mark = "баллов"
    if current_mark % 10 == 1 and current_mark != 11:
        mark = "балл"
    elif 2 <= current_mark % 10 <= 4 and not 12 <= current_mark <= 14:
        mark = "балла"
    not_check_questions = [i.question for i in result_test.answers if i.mark is None]
    output = (f"Набрано {current_mark} {mark} из {all_mark}. В процентах: {current_mark / all_mark * 100:.2f}%\n"
              f"Вопросов ожидающих проверки: {len(not_check_questions)}. "
              f"В баллах {sum(i.weight for i in not_check_questions)}\n"
              f"Общее время прохождения: {sum_time([i.complition_time for i in result_test.answers])}\n"
              f"Когда был пройден тест: {result_test.completed_date:%d %B %Y год %X}")

    w = ViewResultTest(result_test)
    x, y = 700, 700
    pie = w.create_pie(current_mark, not_check_mark, all_mark, anim=QChart.AnimationOption.NoAnimation)
    pie.setMinimumSize(x, y)
    pie.grab().save("pie.png")
    bar = w.create_bar(QChart.AnimationOption.NoAnimation)
    bar.setMinimumSize(x, y)
    bar.grab().save("bar.png")

    user.answer = None
    inline_view_questions.callback_data = "on_view_questions" + str(result_test.id) + ";"
    inline_set_note.callback_data = "on_set_note" + str(result_test.id)
    inline_markup_for_result_test = InlineKeyboardMarkup().add(inline_view_questions, inline_set_note)

    media_group = MediaGroup()
    media_group.attach_photo(InputFile("pie.png"), caption="Диаграммы с результами")
    media_group.attach_photo(InputFile("bar.png"))

    await bot.send_media_group(callback_query.from_user.id, media_group)

    await bot.send_message(callback_query.from_user.id, output, reply_markup=inline_markup_for_result_test)


@dp.callback_query_handler(lambda c: c.data[:17] == 'on_view_questions')
async def view_questions(callback_query: types.CallbackQuery):
    user = TelegramUser.create(callback_query.from_user.id)
    arg: str = callback_query.data[17:]
    result_test = ResultTestLogic().get(uuid.UUID(arg[:arg.find(";")]))
    start = arg.find("<")
    end = arg.rfind(">")
    is_new = start == -1 or end == -1 or not len(arg[start+1:end])
    question_index = 0 if is_new else int(arg[start+1:end])
    answer = result_test.answers[question_index]

    mark = "Вопрос еще не проверен" if answer.mark is None else f"Балл *{answer.mark}* из *{answer.question.weight}*"
    info = f"*№{question_index+1} из {len(result_test.answers)}* \n\n" \
           f"Вопрос: *{answer.question.name}*\n\n{mark}\nВремя прохождения: *{answer.complition_time}*"
    if answer.text_answer:
        info += f"\n\nПолученный ответ: {answer.text_answer}"
    if answer.question.question_input_answer and result_test.test.show_answer:
        info += f"\n\nПравильный ответ: {answer.question.question_input_answer.correct_answer}"
    if answer.question.question_choice:
        info += "\n"
        for test_answer in answer.question.question_choice.answers_test:
            is_checked = "☑" if test_answer in answer.answers_test else "\t ☐\t"
            correct = "Правильный ответ" if test_answer.correct else "Неправильный ответ"
            info += f"\n{is_checked} - {test_answer.text}"
            if result_test.test.show_answer:
                info += f" - {correct}"

    ptr = answer.question.pointer_to_answer
    txt = TheoryViewWidget(result_test.test.theory).set_to_pointer(ptr)
    info += f'\n\nОтрывок из теории *"{ result_test.test.theory.name}"* раздела *{ptr.chapter.name}* ' \
            f'помеченный как ответ: \n"{txt}"'

    prev_btn = InlineKeyboardButton("<<", callback_data=f"on_view_questions{result_test.id};<{question_index-1}>")
    next_btn = InlineKeyboardButton(">>", callback_data=f"on_view_questions{result_test.id};<{question_index+1}>")
    mrk = InlineKeyboardMarkup(3)
    if 0 < question_index < len(result_test.answers) - 1:
        mrk.add(prev_btn, next_btn)
    elif question_index != 0:
        mrk.add(prev_btn)
    elif question_index + 1 != len(result_test.answers):
        mrk.add(next_btn)

    if is_new or user.msg_view_questions is None:
        user.msg_view_questions = await bot.send_message(callback_query.from_user.id, info, 'markdown', reply_markup=mrk)
    else:
        await user.msg_view_questions.edit_text(info, 'markdown', reply_markup=mrk)


@dp.callback_query_handler(lambda c: c.data[:11] == 'on_set_note')
async def set_note(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    user = TelegramUser.create(callback_query.from_user.id)
    user.state = TelegramUser.State.wait_input
    result_test = ResultTestLogic().get(uuid.UUID(callback_query.data[11:]))
    await bot.send_message(callback_query.from_user.id, "Оставьте примечание для создателя теста:")
    while user.state == TelegramUser.State.wait_input:
        await asyncio.sleep(0.8)
    result_test.note = user.answered_message.text
    ResultTestLogic().save()
    await user.answered_message.reply("Примечание сохранено")


@dp.callback_query_handler(lambda c: c.data[:11] == 'on_get_test')
async def set_note(callback_query: types.CallbackQuery):
    msg = types.Message()
    msg.from_user = callback_query.from_user
    msg.text = "/test " + callback_query.data[11:]
    msg.chat = callback_query.message.chat
    await get_test(msg)


@dp.message_handler(Command("tests"))
async def get_available_tests(message: types.Message):
    user = TelegramUser.create(message.from_user.id)
    await message.reply("Вот список добавленных тестов:", reply_markup=InlineKeyboardMarkup(1).add(
        *[InlineKeyboardButton(f"Тест: {test.name}", callback_data="on_get_test"+str(test.id)) for test in user.tests]
    ))


@dp.message_handler(Command("results_tests"))
async def get_all_results_tests(message: types.Message):
    user = TelegramUser.create(message.from_user.id)
    await message.reply("Вот все ваши результаты тестов:", reply_markup=InlineKeyboardMarkup(1).add(
        *[InlineKeyboardButton(f"{res.test.name} - {sum(i.mark for i in res.answers)} б.",
                               callback_data="on_view_result"+str(res.id)) for res in user.results_tests]
    ))


if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
    executor.start_polling(dp, skip_updates=True)
