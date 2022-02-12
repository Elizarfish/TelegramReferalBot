# Запуск бота
from loguru import logger
from tortoise import Tortoise

from handlers import dp as handlers_dp
from settings import DATABASE_URL


async def on_startup(dp):
    logger.info("Starting bot")

    await Tortoise.init(db_url=DATABASE_URL, modules={"models": ["models"]})
    await Tortoise.generate_schemas()
    from utils import on_startup_notify  # pylint: disable=import-outside-toplevel

    await on_startup_notify(dp)
    logger.info("Admins notified")


def handle():
    from aiogram import executor  # pylint: disable=import-outside-toplevel

    logger.info("Starting bot")
    executor.start_polling(handlers_dp, on_startup=on_startup)


if __name__ == "__main__":
    handle()
