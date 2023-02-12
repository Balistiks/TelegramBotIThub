from aiogram import Bot, Dispatcher, types, executor
import config
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import sqlite3
from aiogram.contrib.fsm_storage.memory import MemoryStorage

bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


db = sqlite3.connect("datebase/datebase.db")
cur = db.cursor()


directorate = [732710875]


class AddEvent(StatesGroup):
    name = State()
    number = State()
    questions = State()


class StateUser(StatesGroup):
    name = State()
    phoneNumber = State()


@dp.message_handler(commands="start")
async def start(message: types.Message):
    if message.chat.id in directorate:
        directorateKeyboard = types.InlineKeyboardMarkup()
        directorateKeyboard.add(types.InlineKeyboardButton(text="Добавить вопрос", callback_data="addEvent"))
        await message.answer("Что будем делать?", reply_markup=directorateKeyboard)
    else:
        await StateUser.name.set()
        await message.answer("Доброго времени суток!\n"
                                "На связи служба заботы IT-колледжа ВВГУ (IThub Владивосток)\n"
                                "Как вас зовут?")


@dp.message_handler(state=StateUser.name)
async def getName(message: types.Message):
    name = message.text
    await StateUser.next()
    await message.answer("Напишите номер телефона")


@dp.message_handler(state=StateUser.phoneNumber)
async def getPhoneNumber(message: types.Message, state: FSMContext):
    phoneNumber = message.text
    
    await state.finish()
    await message.answer(text="На каком мероприятии вы были?")


@dp.callback_query_handler()
async def callbackHandler(call: types.CallbackQuery):
    if call.data == "addEvent":
        await AddEvent.name.set()
        await call.message.answer(text="Напишите название мероприятия")


@dp.message_handler(state=AddEvent.name)
async def addEventName(message: types.Message, state: FSMContext):
    await state.update_data(nameEvent=message.text)
    await AddEvent.next()
    await message.answer(text="Сколько вопросов будет?")


@dp.message_handler(state=AddEvent.number)
async def addNumberQuestions(message: types.Message, state: FSMContext):
    try:
        numberQuestions = int(message.text)
        await state.update_data(numberQuestions=numberQuestions)
        data = await state.get_data()
        cur.execute("INSERT INTO Events (EventTitle, NumberOfQuestions) VALUES (?, ?)", (data["nameEvent"], numberQuestions,))
        db.commit()
        cur.execute("""
        CREATE TABLE "?"
        (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            EventId INTEGER,
            EventTitle TEXT,
            FOREIGN KEY (EventId) REFERENCES EVENTS (Id)
        )
        """, (data["nameEvent"],))
        cur.execute("""
        INSERT INTO "?" (EventId, EventTitle)
        VALUES
        (
            (SELECT Id FROM Events WHERE EventTitle='?'),
            "?"
        )
        """, (data["nameEvent"], data["nameEvent"], data["nameEvent"],))
        await AddEvent.questions.set()
    except:
        await message.answer(text="Что-то не то написал, попробуй еще раз")
        await message.answer(text="Сколько вопросов будет?")


@dp.message_handler(state=AddEvent.questions)
async def addQuestion(message: types.Message, state: FSMContext):
    data = await state.get_data()
    


executor.start_polling(dp, skip_updates=True)
