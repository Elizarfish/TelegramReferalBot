import glob
import logging
import random
import string

import cv2
import numpy as np
from PIL import Image, ImageFont, ImageDraw
from aiogram import Dispatcher

import settings

logger = logging.getLogger(__name__)


async def on_startup_notify(dp: Dispatcher):
    """Уведомление разрабов о запуске бота"""

    for admin in settings.ADMINS_BOT:
        try:
            await dp.bot.send_message(admin, "Бот Запущен")
        except Exception as err:
            logger.info(f"Admin chat_id not found or bot was blocked: {str(err)}")


def generate_captcha_img():
    """Создание captcha из текста и возвращение изображения"""
    fonts = glob.glob('captcha/*.ttf')
    size = random.randint(30, 35)
    length = random.randint(5, 8)
    img = np.zeros(shape=(100, 150, 3), dtype=np.uint8)
    img_pil = Image.fromarray(img + 255)

    # Drawing text and lines
    font = ImageFont.truetype(random.choice(fonts), size)
    draw = ImageDraw.Draw(img_pil)
    text = ''.join(
        random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase)
        for _ in range(length))
    draw.text((random.randint(10, 26), random.randint(10, 26)), text, font=font,
              fill=(219, 219, 219))
    draw.line([(random.randint(0, 150), random.randint(0, 100)) for _ in range(random.randint(5, 9))],
              width=2, fill=(random.randint(219, 255), random.randint(208, 219), random.randint(199, 255)))

    # Adding noise and blur
    img = np.array(img_pil)
    # cv2.imshow(f"{text}", img)
    # cv2.waitKey()
    # cv2.destroyAllWindows()
    path = f"captcha/{text}.jpg"
    cv2.imwrite(path, img)  # if you want to save the image
    return text, path
