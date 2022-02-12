from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

keyboard_examination = InlineKeyboardMarkup().add(InlineKeyboardButton(text="Проверить✅", callback_data="examination"))
bnt_menu = KeyboardButton(text="Меню⏮")
bnt_conditions = KeyboardButton(text="Условия⏭")
btn_ref = KeyboardButton(text="Партнерка⏭")
keyboard_menu = ReplyKeyboardMarkup(resize_keyboard=True).row(bnt_conditions, btn_ref)
keyboard_menu_conditions = ReplyKeyboardMarkup(resize_keyboard=True).row(bnt_menu, btn_ref)
keyboard_menu_ref = ReplyKeyboardMarkup(resize_keyboard=True).row(bnt_menu, bnt_conditions)
