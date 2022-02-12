from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

keyboard_phone = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton("Отправить свой контакт ☎️", request_contact=True)
)
