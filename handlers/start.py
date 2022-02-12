from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.utils.markdown import hlink
from loguru import logger

import settings
from keyboards.inline.menu import keyboard_examination, keyboard_menu, keyboard_menu_conditions, \
    keyboard_menu_ref
from loader import dp
from models import UserBot
from states import MyData
from utils import generate_captcha_img


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message, state: FSMContext):
    """Обработка команды /start"""
    logger.info("Пользователь {} нажал кнопку /start".format(message.from_user.id))
    u, create = await UserBot.get_user_and_created(message.from_user)
    await state.update_data(u=u)
    if create:
        if chat_id_partner := message.get_args():
            if parent := await UserBot.get_or_none(id=int(chat_id_partner)):
                u.parent = parent
                await u.save()
        await message.answer('Для участия в конкурсе нужно подписаться на канал\n'
                             f'\n{hlink("Romanov | Crypto Analytics", settings.GROUP_URL)}\n', reply_markup=keyboard_examination)
        await MyData.registration.set()
    else:
        await message.answer('Привет!\nЭто бот канала Romanov.\nДля того чтобы принять участие в конкурсе - ознакомься с его условиями.', reply_markup=keyboard_menu)


@dp.callback_query_handler(lambda call: call.data == "examination", state=MyData.registration)
async def examination_group(call: types.CallbackQuery, state: FSMContext):
    user_channel_status = await dp.bot.get_chat_member(chat_id=settings.CHAT_ID, user_id=call.from_user.id)
    data = await state.get_data()
    if (u := data.get("u")) is None:
        u = await UserBot.get_user(call.from_user)
    if user_channel_status["status"] != 'left':
        await call.answer()
        if parent := await u.get_parent:
            await call.message.edit_text(f'Ура вы с нами, Вас пригласил {parent.full_name}')
        else:
            await call.message.edit_text(f'Ура вы с нами')
        text = 'Пожалуйста пройдите CAPTCHA'
        await call.message.answer(text)
        captcha, path = generate_captcha_img()
        u.captcha = captcha.lower()
        await u.save()
        await call.message.answer_photo(photo=open(path, 'rb'), caption='Введите код из картинки')
        await MyData.captcha.set()
        await state.update_data(u=u)
    else:
        await call.answer(text='Вы не подписаны на канал, пожалуйста подпишитесь на канал и повторите попытку',
                          show_alert=True)


@dp.message_handler(state=MyData.captcha)
async def captcha_set(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if (u := data.get("u")) is None:
        u = await UserBot.get_user(message.from_user)
    if message.text.lower() == str(u.captcha):
        await message.answer('Поздравляю вы прошли капчу. Вы в главном меню', reply_markup=keyboard_menu)
        u.pr_is = True
        await u.save()
        await state.reset_state(with_data=False)
        await state.update_data(u=u)
    else:
        await message.answer('Неверный код, попробуйте еще раз')
        captcha, path = generate_captcha_img()
        u.captcha = captcha.lower()
        await u.save()
        await message.answer_photo(photo=open(path, 'rb'), caption='Введите код из картинки')
        await state.update_data(u=u)


@dp.message_handler(lambda message: message.text == 'Меню⏮')
async def set_menu(message: types.Message):
    await message.answer('Вы в главном меню', reply_markup=keyboard_menu)


@dp.message_handler(lambda message: message.text == 'Условия⏭')
async def set_conditions(message: types.Message):
    await message.answer('Условия конкурса', reply_markup=keyboard_menu_conditions)


@dp.message_handler(lambda message: message.text == 'Партнерка⏭')
async def set_partner(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if (u := data.get("u")) is None:
        u = await UserBot.get_user(message.from_user)
    partners = await u.get_partners
    len_partners = str(len(partners))
    bot_user = await message.bot.get_me()
    url_invite = f"https://t.me/{bot_user.username}?start={u.id}"
    text_message = (f'Ваша реферальная\n\n' + url_invite + f'\n\nВаши Рефералы ' + len_partners + f':\n')
    if partners:
        for partner in partners:
            text_message += f'{partner.full_name}|{partner.tg_str}\n'
    else:
        text_message += 'У вас пока нет Рефералов'
    await message.answer(text_message, reply_markup=keyboard_menu_ref)


@dp.message_handler(lambda message: message.text.startswith('/send'), )
async def all_send(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if (u := data.get("u")) is None:
        u = await UserBot.get_user(message.from_user)
    if u.is_admin:
        async for user in UserBot.filter(is_admin=False).all():
            await message.bot.send_message(user.id, message.text[5:])
        await message.answer('Сообщение отправлено')
    else:
        await message.answer('Вы не админ')
