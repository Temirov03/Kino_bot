import logging
from aiogram import executor
from environs import Env
from db import Database
from aiogram import Bot, Dispatcher, types
import aiogram

db_objects = Database("db.sqlite3")

env = Env()
env.read_env()

logging.basicConfig(level=logging.INFO)

bot = Bot(token=env("BOT_TOKEN"))
dp = Dispatcher(bot)

VIDEO_CODE = None
VIDEO_NAME = None
VAD = False
VIDEO_CODE_SENT = False
REFRESH = False
api_id = env("ADMINS")
channel_username = env("CHANNEL_USERNAME")




@dp.message_handler(text="/start")
async def video(message: types.Message):
    if str(message.from_user.id) == env("ADMINS"):
        await message.answer("Salom ADMIN")
    else:
        keyboard = types.InlineKeyboardMarkup()
        subscribe_button = types.InlineKeyboardButton("Kanalga obuna bo'lish", url='https://t.me'
                                                                                   '/Tarjima_kln0lar')
        keyboard.add(subscribe_button)
        await message.reply(
            "Kanalga obuna bo'lish shartini bajarish uchun quyidagi tugmani bosing va so'ngra /start "
            "tugmasini bosing:",
            reply_markup=keyboard)
        chat = await bot.get_chat(message.from_user.id)
        user_count = chat.get("member_count", 0)
        await message.reply(f"Hozirgi foydalanuvchilar soni: {user_count}")


"""@dp.message_handler(text="/count")
async def count(message: types.Message):
    chat = await bot.get_chat(message.chat.id)
    user_count = chat.get('members_count', 0)
    await message.reply(f"Hozirgi foydalanuvchilar soni: {user_count}")"""

@dp.message_handler(text="/video")
async def video(message: types.Message):
    global VIDEO_CODE_SENT, VAD, REFRESH
    if str(message.from_user.id) != env("ADMINS"):
        await message.answer("ADMIN KERAK")
    else:
        VIDEO_CODE_SENT = True
        REFRESH = False
        VAD = False
        await message.answer("Video kodini kiriting:  ")


@dp.message_handler(content_types=types.ContentTypes.VIDEO)
async def video_load(message: types.Message):
    global REFRESH
    if str(message.from_user.id) != env("ADMINS"):
        await message.answer("ADMIN KERAK")
    else:
        if VIDEO_CODE is not None and VIDEO_NAME is not None:
            db_objects.set_video_by_code(VIDEO_CODE, message.video.file_id, VIDEO_NAME)
            await message.answer("Video yuklandi ✅ 🎉🎉")
            REFRESH = True
        else:
            await message.answer("Video kod yo'q")


async def check_subscription(channel_uname, user_id):
    try:
        subscriber = await bot.get_chat_member(chat_id=channel_uname, user_id=user_id)
        if subscriber.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except Exception as e:
        print(f"Xato: {e}")
        return False


@dp.message_handler()
async def echo(message: types.Message):
    global VAD, VIDEO_NAME, VIDEO_CODE
    chat_id = message.from_user.id
    if VIDEO_CODE_SENT and REFRESH is False and str(message.from_user.id) == env("ADMINS"):
        if VAD is False:
            check_video = db_objects.check_video_code(message.text)
            if check_video == 0:
                VIDEO_CODE = message.text
                VAD = True
                await dp.bot.send_message(chat_id=chat_id, text="Video nomini kiriting: ")
            else:
                await dp.bot.send_message(chat_id=chat_id, text="Bu kod mavjud \n \n \n \n Video kodini kiriting ♻️:")
        else:
            VIDEO_NAME = message.text
            await dp.bot.send_message(chat_id=chat_id, text="Video yuklang: ")
    else:
        is_subscribed = await check_subscription(channel_username, chat_id)
        if is_subscribed:
            video_obj = db_objects.get_video_by_code(message.text)
            if video_obj == 0:
                await dp.bot.send_message(chat_id=chat_id, text="Video Yo'q")
            else:
                video_id = video_obj[0]
                video_text = video_obj[1]
                await dp.bot.send_video(chat_id=chat_id, video=video_id, caption=f"{video_text} \n {channel_username}")
        else:
            keyboard = types.InlineKeyboardMarkup()
            subscribe_button = types.InlineKeyboardButton("Kanalga obuna bo'lish", url='https://t.me'
                                                                                       '/Tarjima_kln0lar')
            keyboard.add(subscribe_button)
            await dp.bot.send_message(chat_id=chat_id,
                                      text=f"Botni ishga tushirish uchun ushbu kanalga obuna bo'ling \n",
                                      reply_markup=keyboard)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
