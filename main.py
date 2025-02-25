from random import randint

import requests
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram import F
from aiogram.utils.keyboard import InlineKeyboardBuilder



# Вместо BOT TOKEN HERE нужно вставить токен вашего бота, полученный у @BotFather
BOT_TOKEN = '7678996231:AAHW1_FBmzChfCTnSXT5dbC86ei3gao-g9c'

# Создаем объекты бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# Этот хэндлер будет срабатывать на команду "/start"
@dp.message(Command(commands=["start"]))
async def process_start_command(message: Message):
    await message.answer('Привет!\nМеня зовут Эхо-бот!\nНапиши мне что-нибудь')


# # Этот хэндлер будет срабатывать на команду "/help"
# @dp.message(Command(commands=['help']))
# async def process_help_command(message: Message):
#     await message.answer(
#         'Напиши мне что-нибудь и в ответ '
#         'я пришлю тебе твое сообщение'
#     )

# @dp.message(Command(commands=['start']))
# async def cmd_start(message: Message):
#     kb = [
#         [KeyboardButton(text="слова")],
#         [KeyboardButton(text="тесты")]
#     ]
#     keyboard = ReplyKeyboardMarkup(keyboard=kb)
#     await message.answer("Я бот для изучения английского, выбери, ты хочешь проходить тесты или учить новые слова", reply_markup=keyboard)
#
#
# @dp.message(F.text.lower() == "слова")
# async def with_puree(message: Message):
#     await message.reply("Супер, давай приступим")

# Этот хэндлер будет срабатывать на любые ваши текстовые сообщения,
# кроме команд "/start" и "/help"


@dp.message(Command(commands=['create_group']))
async def create_group(message: Message):
    # Используем метод createChatInviteLink для создания группы
    response = requests.post(
        f'https://api.telegram.org/bot{BOT_TOKEN}/createChatInviteLink',
        data={'chat_id': message.chat.id}
    )
    if response.status_code == 200:
        invite_link = response.json().get('result', {}).get('invite_link')
        await message.answer(f'Создана новая группа! Пригласительная ссылка: {invite_link}')
    else:
        await message.answer('Не удалось создать группу.')




@dp.message(Command("random"))
async def cmd_random(message: Message):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="Нажми меня",
        callback_data="random_value")
    )
    await message.answer(
        "Нажмите на кнопку, чтобы бот отправил число от 1 до 10",
        reply_markup=builder.as_markup()
    )



@dp.callback_query(F.data == "random_value")
async def send_random_value(callback: CallbackQuery):
    await callback.message.answer(str(randint(1, 10)))

@dp.message()
async def send_echo(message: Message):
    await message.reply(text=message.text)



if __name__ == '__main__':
    dp.run_polling(bot)