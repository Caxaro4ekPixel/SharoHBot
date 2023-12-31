from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher import filters
from decouple import config
import logging
from os import path

logging.basicConfig(level=logging.INFO)

admin_chat_id = int(config('ADMIN_CHAT_ID'))

bot = Bot(token=config('BOT_TOKEN'))
dp = Dispatcher(bot=bot)

baned_users = set()

if not path.exists('baned_users'):
    with open('baned_users', "a+") as f:
        pass
else:
    with open('baned_users', "r") as f:
        for line in f:
            baned_users.add(int(line.strip()))


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    logging.info(f"Пользователь {message.from_user.id} запустил бота")
    await message.reply("Привет! Отправь мне контент и я перешлю его Шарону для участия в рубрике!")


@dp.message_handler(commands=['ban'])
async def ban_user(message: types.Message):
    if message.chat.id == admin_chat_id:
        if message.get_args().isdigit():
            user_banned_id = int(message.get_args())
            baned_users.add(user_banned_id)
            with open('baned_users', 'w') as f:
                for user in baned_users:
                    f.write(str(user) + '\n')
            await message.reply("Пользователь забанен!")
            await bot.send_message(chat_id=user_banned_id, text=f"Вы были заблокированы! Желаем удачи!")
        else:
            await message.reply("Введите id пользователя!")


@dp.message_handler(commands=['unban'])
async def ban_user(message: types.Message):
    if message.chat.id == admin_chat_id:
        if message.get_args().isdigit():
            user_unbanned_id = int(message.get_args())
            baned_users.remove(user_unbanned_id)
            with open('baned_users', 'w') as f:
                for user in baned_users:
                    f.write(str(user) + '\n')
            await message.reply("Пользователь разблокирован!")
            await bot.send_message(chat_id=user_unbanned_id, text=f"Вы были разблокированы!")
        else:
            await message.reply("Введите id пользователя!")


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
    elif message.content_type == types.ContentType.AUDIO:
        await bot.send_audio(chat_id=admin_chat_id, audio=message.audio.file_id)
        await who_sent(message)
        await message.reply("Аудио отправлено! Огромное спасибо❤️")
    elif message.content_type == types.ContentType.TEXT:
        await bot.send_message(chat_id=admin_chat_id,
                               text=f"{message.text}\n\n=Контент отправил=\nusername: @{message.chat.username}\nИмя: {message.chat.full_name}\nID: {message.from_user.id}")
        await message.reply("Текст отправлен! Огромное спасибо❤️")


@dp.message_handler(filters.ChatTypeFilter(types.ChatType.PRIVATE))
@dp.message_handler(content_types=types.ContentTypes.ANY)
async def send_video(message: types.Message):
    logging.info(f"Пользователь {message.from_user.id} отправил контент")
    if message.chat.id not in baned_users:
        if message.media_group_id is None:
            await send_one_media(message)
        else:
            await send_one_media(message)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
