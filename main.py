import asyncio
import logging

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import BufferedInputFile

from selenium.webdriver.chrome.options import Options
from selenium import webdriver

from config import config

import buff_163_parser

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher()

# Установка параметров Selenium Driver
# Set Selenium Web Driver's options
options = Options()
# options.add_argument('--headless=new')
# options.add_argument("--blink-settings=imagesEnabled=false")
options.add_argument("--lang=ru-RU")
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36")  # Установка user-agent

# Создание драйвера Chrome
# Creating Chrome Driver
driver = webdriver.Chrome(options=options)


# Класс для FSMContext
# Class for FSMContext
class login(StatesGroup):
    PHONE_NUMBER = State()
    SMS = State()


# Обработка команды /start
# /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id


    kb = [
        [
            types.KeyboardButton(text="Начать"),
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="нажми Начать"
    )

    await bot.send_message(user_id, f'Привет, {message.from_user.first_name}!\n'
                                    f'Нажми "Начать" для начала работы', reply_markup=keyboard)


# Обработка кнопки 'Начать;
#
@dp.message(F.text == "Начать")
async def start(message: types.Message, state: FSMContext):
    await message.reply("Отлично!\n"
                        "Для начала введи номер телефона от аккаунта buff.163.com\n\n"
                        "Формат 7xxxxxxxxxx", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(login.PHONE_NUMBER)


# Обработка ввода номера
#
@dp.message(login.PHONE_NUMBER)
async def get_phone_number(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    phone_number = message.text

    if phone_number[0] == '7' and len(phone_number) == 11:
        await state.clear()
        await bot.send_message(user_id, 'Номер телефона принят, пожалуйста, ожидайте⏳')

        try:
            buff_163_parser.buff_login(driver, phone_number[1:])
        except Exception as e:
            print(e)
            await bot.send_message(user_id, 'Что-то пошло не так')
            return False

        await bot.send_message(user_id, 'Введите SMS полученное от buff.163.com')
        await state.set_state(login.SMS)
    else:
        await bot.send_message(user_id, 'Введите корректный номер телефона')


# Обработка ввода SMS
# SMS
@dp.message(login.SMS)
async def get_phone_number(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    code = message.text

    await state.clear()
    await bot.send_message(user_id, 'Код принят, ожидайте⏳')

    try:
        buff_163_parser.buff_sms(driver, code)
    except Exception as e:
        print(e)
        await bot.send_message(user_id, 'Что-то пошло не так, похоже код не верный')
        return False

    response = 'Вход произведен успешно!\n\nВ течении минуты боты начнет работу'

    await bot.send_message(user_id, response)
    await buff_163_parser.start_search(driver, bot, user_id, 100)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())