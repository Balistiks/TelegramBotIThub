import config
import logging
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import sqlite3

logging.basicConfig(level=logging.INFO)
db = sqlite3.connect('database/answersdb.db')
cur = db.cursor()

bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


class User(StatesGroup):
    name = State()
    phoneNumber = State()
    firstQuestion = State()
    secondQuestion = State()
    thirdQuestion = State()
    fourthQuestion = State()
    fifthQuestion = State()
    sixthQuestionGood = State()
    sixthQuestionBad = State()


@dp.message_handler(commands="start")
async def cmd_test1(message: types.Message):
    cur.execute("""
    INSERT INTO Answers(UserId)
    VALUES(?);""", (str(message.chat.id),))
    db.commit()

    cur.execute("""
    INSERT INTO DetailedAnswers(AnswersId, UserId)
    VALUES((SELECT Id FROM Answers WHERE UserId = ?),?);
    """, (str(message.chat.id), str(message.chat.id),))
    db.commit()

    await message.answer("Бот для отзывов.")
    await User.name.set()
    await message.answer("Как вас зовут?")


@dp.message_handler(state=User.name)
async def process_name(message: types.Message):
    cur.execute("""
    UPDATE Answers
    SET Name = ?
    WHERE UserId = ?;
    """, (message.text, str(message.chat.id),))
    db.commit()
    await User.next()
    await message.answer('Напишите номер телефона')


@dp.message_handler(state=User.phoneNumber)
async def process_phone(message: types.Message, state: FSMContext):
    cur.execute("""
    UPDATE Answers
    SET PhoneNumber = ?
    WHERE UserId = ?;
    """, (message.text, str(message.chat.id),))
    db.commit()
    await state.finish()
    await question1(message.chat.id)


@dp.callback_query_handler()
async def questionCallback(call: types.CallbackQuery, state: FSMContext):
    keyboardAnswer = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    buttonAnswer = types.KeyboardButton(text="Не хочу отвечать")
    keyboardAnswer.add(buttonAnswer)
    if call.data[0] == "1":
        if call.data[1::1] == "Да":
            await question2(call.message.chat.id)
        else:
            await User.firstQuestion.set()
            await bot.send_message(chat_id=call.message.chat.id,
                                   text="Ох, это обидно! Расскажите, что не удалось "
                                        "сделать и почему. "
                                        "Напишите своими словами",
                                   reply_markup=keyboardAnswer)
        cur.execute("""
        UPDATE Answers
        SET Answer1 = ?
        WHERE UserId = ?;
        """, (call.data[1::1], call.message.chat.id,))
        db.commit()
    elif call.data[0] == "2":
        if call.data[1::1] == "Да":
            await question3(call.message.chat.id)
        else:
            await User.secondQuestion.set()
            await bot.send_message(chat_id=call.message.chat.id, text="Ого! А почему так произошло?",
                                   reply_markup=keyboardAnswer)
        cur.execute("""
        UPDATE Answers
        SET Answer2 = ?
        WHERE UserId = ?;
        """, (call.data[1::1], call.message.chat.id,))
        db.commit()
    elif call.data[0] == "3":
        if call.data[1::1] == "Отлично" or call.data[1::1] == "Хорошо":
            await question4(call.message.chat.id)
        else:
            await User.thirdQuestion.set()
            await bot.send_message(chat_id=call.message.chat.id,
                                   text="Это совсем неправильно. "
                                        "Напишите, с кем вы общались и что случилось",
                                   reply_markup=keyboardAnswer)
        cur.execute("""
        UPDATE Answers
        SET Answer3 = ?
        WHERE UserId = ?;
        """, (call.data[1::1], call.message.chat.id,))
        db.commit()
    elif call.data[0] == "4":
        if call.data[1::1] == "Да":
            await question5(call.message.chat.id)
        else:
            await User.fourthQuestion.set()
            await bot.send_message(chat_id=call.message.chat.id,
                                   text="Почему?",
                                   reply_markup=keyboardAnswer)
        cur.execute("""
        UPDATE Answers
        SET Answer4 = ?
        WHERE UserId = ?;
        """, (call.data[1::1], call.message.chat.id,))
        db.commit()
    elif call.data[0] == "5":
        if call.data[1::1] == "Да" or call.data[1::1] == "Почти":
            await question6(call.message.chat.id)
        else:
            await User.fifthQuestion.set()
            await bot.send_message(chat_id=call.message.chat.id,
                                   text="Так, непорядок! Расскажите подробнее, что было не так с выступлением",
                                   reply_markup=keyboardAnswer)
        cur.execute("""
        UPDATE Answers
        SET Answer5 = ?
        WHERE UserId = ?;
        """, (call.data[1::1], call.message.chat.id,))
        db.commit()
    elif call.data[0] == "6":
        if call.data[1::1] == "Супер" or call.data[1::1] == "Хорошо" or call.data[1::1] == "Норм":
            await User.sixthQuestionGood.set()
            await bot.send_message(chat_id=call.message.chat.id,
                                   text="Спасибо! Напишите мне, что вам особенно понравилось - "
                                        "передам команде",
                                   reply_markup=keyboardAnswer)
        else:
            await User.sixthQuestionBad.set()
            await bot.send_message(chat_id=call.message.chat.id,
                                   text="Как жаль :( А вдруг мы поможем что-то сделать?",
                                   reply_markup=keyboardAnswer)
        cur.execute("""
        UPDATE Answers
        SET Answer6 = ?
        WHERE UserId = ?;
        """, (call.data[1::1], call.message.chat.id,))
        db.commit()
    await bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                        message_id=call.message.message_id,
                                        reply_markup=None)
    await call.answer()


@dp.message_handler(state=User.firstQuestion)
async def answer1(message: types.Message, state: FSMContext):
    cur.execute("""
    UPDATE DetailedAnswers
    SET Answer1 = ?
    WHERE UserId = ?;
    """, (message.text, str(message.chat.id),))
    db.commit()
    await state.finish()
    await question2(message.chat.id)


@dp.message_handler(state=User.secondQuestion)
async def answer2(message: types.Message, state: FSMContext):
    cur.execute("""
    UPDATE DetailedAnswers
    SET Answer2 = ?
    WHERE UserId = ?;
    """, (message.text, str(message.chat.id),))
    db.commit()
    await state.finish()
    await question4(message.chat.id)


@dp.message_handler(state=User.thirdQuestion)
async def answer3(message: types.Message, state: FSMContext):
    cur.execute("""
    UPDATE DetailedAnswers
    SET Answer3 = ?
    WHERE UserId = ?;
    """, (message.text, str(message.chat.id),))
    db.commit()
    await state.finish()
    await question4(message.chat.id)


@dp.message_handler(state=User.fourthQuestion)
async def answer4(message: types.Message, state: FSMContext):
    cur.execute("""
    UPDATE DetailedAnswers
    SET Answer4 = ?
    WHERE UserId = ?;
    """, (message.text, str(message.chat.id),))
    db.commit()
    await state.finish()
    await question6(message.chat.id)


@dp.message_handler(state=User.fifthQuestion)
async def answer5(message: types.Message, state: FSMContext):
    cur.execute("""
    UPDATE DetailedAnswers
    SET Answer5 = ?
    WHERE UserId = ?;
    """, (message.text, str(message.chat.id),))
    db.commit()
    await state.finish()
    await question6(message.chat.id)


@dp.message_handler(state=User.sixthQuestionGood)
async def answer6G(message: types.Message, state: FSMContext):
    cur.execute("""
    UPDATE DetailedAnswers
    SET Answer6 = ?
    WHERE UserId = ?;
    """, (message.text, str(message.chat.id),))
    db.commit()
    await state.finish()
    await finish(message.chat.id)



@dp.message_handler(state=User.sixthQuestionBad)
async def answer6B(message: types.Message, state: FSMContext):
    cur.execute("""
    UPDATE DetailedAnswers
    SET Answer6 = ?
    WHERE UserId = ?;
    """, (message.text, str(message.chat.id),))
    db.commit()
    await state.finish()
    await finish(message.chat.id)


async def question1(user):
    question_Keyboard = types.InlineKeyboardMarkup()
    question_Keyboard.add(types.InlineKeyboardButton(text='Да', callback_data="1Да"))
    question_Keyboard.add(types.InlineKeyboardButton(text='Нет', callback_data="1Нет"))
    question_Keyboard.add(types.InlineKeyboardButton(text='Не совсем', callback_data="1Не совсем"))
    question_Keyboard.add(types.InlineKeyboardButton(text='Не было цели', callback_data="1Не было цели"))
    await bot.send_message(chat_id=user,
                           text="На дне открытых дверей вы узнали и сделали всё, что планировали?",
                           reply_markup=question_Keyboard)


async def question2(user):
    question_Keyboard = types.InlineKeyboardMarkup()
    question_Keyboard.add(types.InlineKeyboardButton(text='Да', callback_data="2Да"))
    question_Keyboard.add(types.InlineKeyboardButton(text='Нет', callback_data="2Нет"))
    await bot.send_message(chat_id=user,
                           text="Общались ли вы на мероприятии со специалистом прёмной комиссии?",
                           reply_markup=question_Keyboard)


async def question3(user):
    question_Keyboard = types.InlineKeyboardMarkup()
    question_Keyboard.add(types.InlineKeyboardButton(text="Отлично", callback_data="3Отлично"))
    question_Keyboard.add(types.InlineKeyboardButton(text="Хорошо", callback_data="3Хорошо"))
    question_Keyboard.add(types.InlineKeyboardButton(text="Средне", callback_data="3Средне"))
    question_Keyboard.add(types.InlineKeyboardButton(text="Плохо", callback_data="3Плохо"))
    await bot.send_message(chat_id=user,
                           text="Оцените, как с вами общались сотрудники колледжа?",
                           reply_markup=question_Keyboard)


async def question4(user):
    question_Keyboard = types.InlineKeyboardMarkup()
    question_Keyboard.add(types.InlineKeyboardButton(text='Да', callback_data="4Да"))
    question_Keyboard.add(types.InlineKeyboardButton(text='Нет', callback_data="4Нет"))
    await bot.send_message(chat_id=user,
                           text="Посетили ли вы мастер-класс?",
                           reply_markup=question_Keyboard)


async def question5(user):
    question_Keyboard = types.InlineKeyboardMarkup()
    question_Keyboard.add(types.InlineKeyboardButton(text='Да', callback_data="5Да"))
    question_Keyboard.add(types.InlineKeyboardButton(text='Почти', callback_data="5Почти"))
    question_Keyboard.add(types.InlineKeyboardButton(text='Не очень', callback_data="5Не очень"))
    question_Keyboard.add(types.InlineKeyboardButton(text='Совсем нет', callback_data="5Совсем нет"))
    await bot.send_message(chat_id=user,
                           text="Было ли интересно слушать спикера?",
                           reply_markup=question_Keyboard)


async def question6(user):
    question_Keyboard = types.InlineKeyboardMarkup()
    question_Keyboard.add(types.InlineKeyboardButton(text='Супер', callback_data="6Супер"))
    question_Keyboard.add(types.InlineKeyboardButton(text='Хорошо', callback_data="6Хорошо"))
    question_Keyboard.add(types.InlineKeyboardButton(text='Норм', callback_data="6Норм"))
    question_Keyboard.add(types.InlineKeyboardButton(text='Не понравился', callback_data="6Не понравился"))
    await bot.send_message(chat_id=user,
                           text="Оцените, как вам наш День открытых дверей в целом?",
                           reply_markup=question_Keyboard)


async def finish(user):
    await bot.send_message(chat_id=user,
                           text="Спасибо, что нашли минутку и прошли опрос!\n"
                                "Оставайтесь на связи - наш новостной телеграм-канал! https://t.me/vvsuithub")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)