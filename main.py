from aiogram import Bot, Dispatcher
import tracemalloc
import os
import logging
from dotenv import load_dotenv
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
import pymongo
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    Message,
)


tracemalloc.start()

load_dotenv()
bot = Bot(os.getenv("TOKEN"))
dp = Dispatcher(bot=bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)

admin_id = int(os.getenv("ADMIN_ID"))


class States(StatesGroup):
    FEEDBACK = State()


class TripSearch(StatesGroup):
    START = State()
    LOCATION_FROM = State()
    LOCATION_TO = State()
    MAX_PRICE = State()


class TripCreation(StatesGroup):
    NAME = State()
    PHONE = State()
    DATE = State()
    START_LOCATION = State()
    END_LOCATION = State()
    PRICE = State()
    CAR_INFO = State()


async def db_start():
    global client, db, collection

    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["mydatabase"]
    collection = db["mycollection"]


@dp.message_handler(commands=["start"])
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Я бот от GoPark - инновационной платформы для совместных поездок и оптимизации парковочных мест. "
        "Благодаря интеграции данных в реальном времени, мы предоставляем актуальную информацию о свободных парковочных местах и помогаем в поиске попутчиков. "
        "У нас удобный интерфейс, фокус на безопасности и устойчивости. Давайте начнем!\n\n"
        "Введите /help, чтобы узнать больше команд."
    )
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        KeyboardButton(text="Искать парковки"),
        KeyboardButton(text="Искать водителей"),
        KeyboardButton(text="Создать пост о поездке"),
    ]
    keyboard.add(*buttons)

    await message.answer("Выберите действие:", reply_markup=keyboard)


@dp.message_handler(commands=["about"])
async def cmd_about(message: Message):
    about_text = (
        "Привет! Я - бот от GoPark, инновационной платформы для совместных поездок и оптимизации парковочных мест. "
        "Мы стремимся сделать перемещения удобными и экологически устойчивыми. Наша платформа объединяет водителей и пассажиров, "
        "позволяя им делить поездки и находить свободные парковочные места в реальном времени.\n\n"
        "Основные функции:\n"
        "1. **Совместные поездки:** Находите попутчиков для совместных поездок, сокращая затраты и экологические следы.\n"
        "2. **Оптимизация парковки:** Получайте информацию о свободных парковочных местах в вашем районе.\n\n"
        "Присоединяйтесь к GoPark и делайте свой город более доступным и устойчивым! Введите /help для просмотра доступных команд.\n\n\n"
        "Введите /help, чтобы узнать больше команд"
    )
    await message.answer(about_text)


@dp.message_handler(commands=["help"])
async def cmd_about(
    message: Message,
):
    about_text = "Команда /help здесь будут все команды бота"
    await message.answer(about_text)


@dp.message_handler(commands=["feedback"], state="*")
async def cmd_feedback(message: Message, state: FSMContext):
    await message.answer(
        "Вы можете отправить ваш отзыв, вопрос или пожелание. Введите текст сообщения:"
    )
    await States.FEEDBACK.set()


@dp.message_handler(state=States.FEEDBACK)
async def process_feedback(message: Message, state: FSMContext):
    user_username = message.from_user.username or "Нет никнейма"
    await bot.send_message(
        admin_id,
        f"Отзыв от пользователя {user_username} (ID {message.from_user.id}):\n\n\n{message.text}",
    )
    await message.answer("Спасибо за ваш отзыв! Мы ценим ваше мнение.")
    await state.finish()


# -----------------

@dp.message_handler(lambda message: message.text == "Создать пост о поездке")
async def cmd_create_trip(message: Message):
    await message.answer("Давайте создадим пост о поездке. Введите ваше имя:")
    await TripCreation.NAME.set()


@dp.message_handler(state=TripCreation.NAME)
async def process_name(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data["name"] = message.text
    await message.answer("Введите ваш номер телефона:")
    await TripCreation.PHONE.set()


@dp.message_handler(state=TripCreation.PHONE)
async def process_phone(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data["phone"] = message.text
    await message.answer("Введите дату вашей поездки:")
    await TripCreation.DATE.set()


@dp.message_handler(state=TripCreation.DATE)
async def process_date(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data["date"] = message.text
    await message.answer("Введите место отправления:")
    await TripCreation.START_LOCATION.set()


@dp.message_handler(state=TripCreation.START_LOCATION)
async def process_start_location(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data["start_location"] = message.text
    await message.answer("Введите место назначения:")
    await TripCreation.END_LOCATION.set()


@dp.message_handler(state=TripCreation.END_LOCATION)
async def process_end_location(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data["end_location"] = message.text
    await message.answer("Введите стоимость поездки в  сомах:")
    await TripCreation.PRICE.set()


@dp.message_handler(state=TripCreation.PRICE)
async def process_price(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data["price"] = message.text
    await message.answer(
        "Введите информацию о вашем автомобиле ( марка, модель, госномер):"
    )
    await TripCreation.CAR_INFO.set()


@dp.message_handler(state=TripCreation.CAR_INFO)
async def process_car_info(message: Message, state: FSMContext):
    async with state.proxy() as data:
        db["mycollection"].insert_one(data)
    await message.answer("Ваш пост о поездке успешно создан!")
    await state.finish()


# -----------


@dp.message_handler(lambda message: message.text == "Искать водителей")
async def cmd_search_drivers(message: Message):
    await message.answer(
        "Введите критерии поиска водителей, например, место отправления, место назначения, цену и т.д."
    )
    await TripSearch.START.set()


@dp.message_handler(state=TripSearch.START)
async def process_search_start(message: Message, state: FSMContext):
    await message.answer("Введите место отправления:")
    await TripSearch.LOCATION_FROM.set()


@dp.message_handler(state=TripSearch.LOCATION_FROM)
async def process_search_location_from(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data["location_from"] = message.text
    await message.answer("Введите место назначения:")
    await TripSearch.LOCATION_TO.set()


@dp.message_handler(state=TripSearch.LOCATION_TO)
async def process_search_location_to(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data["location_to"] = message.text
    await message.answer("Введите максимальную цену:")
    await TripSearch.MAX_PRICE.set()


@dp.message_handler(state=TripSearch.MAX_PRICE)
async def process_search_max_price(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data["max_price"] = float(message.text) 
    criteria = {
        "start_location": data["location_from"],
        "end_location": data["location_to"],
        "price": {"$lte": data["max_price"]},
    }
    trip_posts = db["mycollection"].find(criteria)

    result_text = "Результаты поиска водителей:\n"
    for post in trip_posts:
        result_text += (
            f"Имя: {post['name']}\nТелефон: {post['phone']}\nДата: {post['date']}\n"
            f"Отправление: {post['start_location']}\nНазначение: {post['end_location']}\n"
            f"Цена: {post['price']} сом\n"
            f"Информация о машине: {post.get('car_info', 'Нет информации')}\n\n"
        )
    await message.answer(result_text or "Нет результатов по вашему запросу.")
    await state.finish()



#parking slots occupied detection vnizu budet

async def on_startup(_):
    await db_start()
    print("ready")


if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
