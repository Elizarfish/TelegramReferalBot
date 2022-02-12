from aiogram.dispatcher.filters.state import StatesGroup, State


class MyData(StatesGroup):
    captcha = State()
    registration = State()
