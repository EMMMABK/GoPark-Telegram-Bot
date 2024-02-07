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

tracemalloc.start()

load_dotenv()
bot = Bot(os.getenv("TOKEN"))
dp = Dispatcher(bot=bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)

admin_id = int(os.getenv("ADMIN_ID"))


class States(StatesGroup):
    FEEDBACK = State()


async def db_start():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["mydatabase"]  
    collection = db["mycollection"]  



@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Я бот от GoPark - инновационной платформы для совместных поездок и оптимизации парковочных мест. "
        "Благодаря интеграции данных в реальном времени, мы предоставляем актуальную информацию о свободных парковочных местах и помогаем в поиске попутчиков. "
        "У нас удобный интерфейс, фокус на безопасности и устойчивости. Давайте начнем!\n\n"
        "Введите /help, чтобы узнать больше команд."
    )
    
    
@dp.message_handler(commands=['about'])
async def cmd_about(message: types.Message, state: FSMContext):
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
    
    

@dp.message_handler(commands=['help'])
async def cmd_about(message: types.Message, state: FSMContext):
    about_text = (
        "Команда /help здесь будут все команды бота"
    )
    await message.answer(about_text)





@dp.message_handler(commands=['feedback'], state="*")
async def cmd_feedback(message: types.Message, state: FSMContext):
    await message.answer("Вы можете отправить ваш отзыв, вопрос или пожелание. Введите текст сообщения:")
    await States.FEEDBACK.set()


@dp.message_handler(state=States.FEEDBACK)
async def process_feedback(message: types.Message, state: FSMContext):
    user_username = message.from_user.username or "Нет никнейма"
    await bot.send_message(admin_id, f"Отзыв от пользователя {user_username} (ID {message.from_user.id}):\n\n\n{message.text}")
    await message.answer("Спасибо за ваш отзыв! Мы ценим ваше мнение.")
    await state.finish()
    
    



async def on_startup(_):
    await db_start()
    print("ready")


if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
