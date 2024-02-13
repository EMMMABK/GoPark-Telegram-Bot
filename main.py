from aiogram import Bot, Dispatcher, types
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
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)

tracemalloc.start()

load_dotenv()
bot = Bot(os.getenv("TOKEN"))
dp = Dispatcher(bot=bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)

admin_id = int(os.getenv("ADMIN_ID"))


class FeedBackState(StatesGroup):
    FEEDBACK = State()


class TripSearch(StatesGroup):
    START = State()
    LOCATION_FROM = State()
    LOCATION_TO = State()
    MAX_PRICE = State()


class RegisterState(StatesGroup):
    NAME = State()
    PHONE = State()


class TripCreation(StatesGroup):
    DATE = State()
    START_LOCATION = State()
    END_LOCATION = State()
    PRICE = State()
    CAR_INFO = State()
    APPLICANTS = State()


async def register_user(user_id, user_name, phone):
    user_data = {
        "_id": user_id,
        "name": user_name,
        "phone": phone,
        "trips_count": 0,
    }

    if not db["users"].find_one({"_id": user_id}):
        db["users"].insert_one(user_data)


async def get_user_info(user_id):
    return db["users"].find_one({"_id": user_id})


def is_valid_phone_number(phone):
    return phone.startswith("+996") and len(phone) == 13 and phone[4:].isdigit()


async def db_start():
    global client, db, collection

    cluster = pymongo.MongoClient(os.getenv("CLUSTER"))
    db = cluster["GoPark-DataBase"]
    collection = db[os.getenv("MY_COLLECTION")]


@dp.message_handler(commands=["start"])
async def cmd_start(message: Message):
    user_id = message.from_user.id

    existing_user = await get_user_info(user_id)

    if existing_user:
        await message.answer(
            "Привет! Вы уже зарегистрированы. Вы можете воспользоваться функциями бота."
        )
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = [
            KeyboardButton(text="Искать парковки"),
            KeyboardButton(text="Искать водителей"),
            KeyboardButton(text="Создать пост о поездке"),
        ]
        keyboard.add(*buttons)
        await message.answer("Выберите действие:", reply_markup=keyboard)
    else:
        await message.answer("Введите ваше имя:")
        await RegisterState.NAME.set()


@dp.message_handler(state=RegisterState.NAME)
async def process_register_name(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_name = message.text

    async with state.proxy() as data:
        data["user_id"] = user_id
        data["user_name"] = user_name

    await message.answer(f"Отлично, {user_name}! Теперь введите ваш номер телефона:")
    await RegisterState.PHONE.set()


@dp.message_handler(state=RegisterState.PHONE)
async def process_register_phone(message: Message, state: FSMContext):
    phone = message.text

    if not is_valid_phone_number(phone):
        await message.answer(
            "Неверный формат номера. Пожалуйста, введите номер в формате +996XXXXXXXXX."
        )
        return

    async with state.proxy() as data:
        data["phone"] = phone
        data["trips"] = 0

    await register_user(data["user_id"], data["user_name"], phone)

    await message.answer(
        "Спасибо за регистрацию! Теперь вы можете воспользоваться другими функциями бота."
    )
    await state.finish()

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
    await FeedBackState.FEEDBACK.set()


@dp.message_handler(state=FeedBackState.FEEDBACK)
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
    await message.answer("Давайте создадим пост о поездке.")
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
    await message.answer("Введите стоимость поездки в сомах:")
    await TripCreation.PRICE.set()


@dp.message_handler(state=TripCreation.PRICE)
async def process_price(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data["price"] = message.text
    await message.answer(
        "Введите информацию о вашем автомобиле (марка, модель, госномер):"
    )
    await TripCreation.CAR_INFO.set()


@dp.message_handler(state=TripCreation.CAR_INFO)
async def process_car_info(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data["car_info"] = message.text
        data["applicants"] = []  # Initialize empty list for applicants

        db["mycollection"].insert_one(data)

        user_id = message.from_user.id
        user_info = await get_user_info(user_id)
        if user_info:
            trips_count = user_info["trips_count"]
            trips_count += 1
            db["users"].update_one(
                {"_id": user_id}, {"$set": {"trips_count": trips_count}}
            )

            name = user_info["name"]
            phone = user_info["phone"]

            await message.answer(
                f"Ваш пост о поездке успешно создан!\n\n"
                f"Имя: {name}\nТелефон: {phone}\n"
                f"Отправление: {data['start_location']}\n"
                f"Назначение: {data['end_location']}\n"
                f"Дата: {data['date']}\n"
                f"Цена: {data['price']} сом\n"
                f"Информация о машине: {message.text}"
            )
        else:
            await message.answer(
                "Вы не зарегистрированы. Введите /start для регистрации."
            )
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
        "applicants": {"$not": {"$size": 1}},
    }
    trip_posts = db["mycollection"].find(criteria)

    inline_keyboard = InlineKeyboardMarkup()

    result_text = "Результаты поиска водителей:\n"
    for post in trip_posts:
        result_text += (
            f"Имя: {post['name']}\nТелефон: {post['phone']}\nДата: {post['date']}\n"
            f"Отправление: {post['start_location']}\nНазначение: {post['end_location']}\n"
            f"Цена: {post['price']} сом\n"
            f"Информация о машине: {post['car_info']}\n\n"
        )

        apply_button = InlineKeyboardButton(
            text="Apply for Trip",
            callback_data=f"apply_trip_{post['_id']}",
        )
        inline_keyboard.add(apply_button)

    await message.answer(
        result_text or "Нет результатов по вашему запросу.",
        reply_markup=inline_keyboard,
    )
    await state.finish()


@dp.callback_query_handler(lambda query: query.data.startswith("apply_trip_"))
async def process_apply_button(callback_query: CallbackQuery):
    post_id = callback_query.data.split("_")[2]

    post_info = db["mycollection"].find_one({"_id": post_id})

    applicant_id = callback_query.from_user.id
    applicant_info = await get_user_info(applicant_id)

    if applicant_info and post_info:
        owner_id = post_info["user_id"]
        owner_info = await get_user_info(owner_id)

        if owner_info:
            applicant_name = applicant_info["name"]
            applicant_phone = applicant_info["phone"]

            if applicant_id not in post_info["applicants"]:
                post_info["applicants"].append(applicant_id)
                db["mycollection"].update_one(
                    {"_id": post_id}, {"$set": {"applicants": post_info["applicants"]}}
                )

                notification_text = (
                    f"New application for your trip!\n\n"
                    f"Applicant Name: {applicant_name}\nApplicant Phone: {applicant_phone}"
                )

                await bot.send_message(owner_id, notification_text)

                await bot.answer_callback_query(
                    callback_query.id, text="You have applied for the trip."
                )
            else:
                await bot.answer_callback_query(
                    callback_query.id, text="You have already applied for this trip."
                )
        else:
            await bot.answer_callback_query(
                callback_query.id, text="Trip owner information not found."
            )
    else:
        await bot.answer_callback_query(
            callback_query.id, text="Post or applicant information not found."
        )


# ///////////////
@dp.message_handler(commands=["account"])
async def cmd_account(message: Message):
    user_id = message.from_user.id
    user_info = await get_user_info(user_id)

    if user_info:
        trips_count = user_info["trips_count"]
        name = user_info["name"]
        phone = user_info["phone"]

        account_info = (
            f"Имя: {name}\nТелефон: {phone}\nКоличество поездок: {trips_count}"
        )
        await message.answer(account_info)
    else:
        await message.answer("Вы не зарегистрированы. Введите /start для регистрации.")


async def on_startup(_):
    await db_start()
    print("ready")


if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
