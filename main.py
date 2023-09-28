from aiogram import Bot, Dispatcher, types, executor
from decouple import config
import logging

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config('BOT_TOKEN'))
dp = Dispatcher(bot=bot)

admin_chat_id = int(config('ADMIN_CHAT_ID'))


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    logging.info(f"Пользователь {message.from_user.id} запустил бота")
    await message.reply("Привет! Отправь мне контент и я перешлю его Шарону для участия в рубрике!")


async def who_sent(message: types.Message):
    logging.info(f"Пользователь {message.from_user.id} отправил контент")
    await bot.send_message(chat_id=admin_chat_id,
                           text=f"=Контент отправил=\nusername: @{message.chat.username}\nИмя: {message.chat.full_name}\nID: {message.from_user.id}")
    await bot.send_message(chat_id=admin_chat_id, text="=========================")


async def send_one_media(message: types.Message):
    if message.content_type == types.ContentType.VIDEO:
        await bot.send_video(chat_id=admin_chat_id, video=message.video.file_id)
        await who_sent(message)
        await message.reply("Видео отправлено! Огромное спасибо❤️")
    elif message.content_type == types.ContentType.PHOTO:
        photo = max(message.photo, key=lambda x: x.file_size)
        await bot.send_photo(chat_id=admin_chat_id, photo=photo.file_id)
        await who_sent(message)
        await message.reply("Фото отправлено! Огромное спасибо❤️")
    elif message.content_type == types.ContentType.DOCUMENT:
        await bot.send_document(chat_id=admin_chat_id, document=message.document.file_id)
        await who_sent(message)
        await message.reply("Документ отправлен! Огромное спасибо❤️")
    elif message.content_type == types.ContentType.TEXT:
        await bot.send_message(chat_id=admin_chat_id,text=f"{message.text}\n\n=Контент отправил=\nusername: @{message.chat.username}\nИмя: {message.chat.full_name}\nID: {message.from_user.id}")
        await message.reply("Текст отправлен! Огромное спасибо❤️")


@dp.message_handler(content_types=types.ContentTypes.ANY)
async def send_video(message: types.Message):
    if message.chat.type == types.ChatType.PRIVATE:
        if message.media_group_id is None:
            await send_one_media(message)
        else:
            await send_one_media(message)
    else:
        await message.reply("Вы не можете отправлять файлы в этом чате! Это можно делать только в лс боту")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
