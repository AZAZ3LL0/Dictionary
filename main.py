import logging
import asyncio
import asyncpg
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.types import ParseMode
from aiogram.utils import executor

# Установка логгера
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token="")
dp = Dispatcher(bot)


# Подключение к базе данных
async def create_pool():
    return await asyncpg.create_pool(
        user="samat",
        password="123",
        database="dictionary",
        host="localhost"
    )


loop = asyncio.get_event_loop()
pool = loop.run_until_complete(create_pool())


# Функция для добавления слова в базу данных
async def add_word(word, definition):
    async with pool.acquire() as connection:
        await connection.execute("INSERT INTO words (word, definition) VALUES ($1, $2)", word, definition)


# Функция для поиска слова в базе данных
async def find_word(word):
    async with pool.acquire() as connection:
        row = await connection.fetchrow("SELECT * FROM words WHERE word = $1", word)
        if row:
            return row["definition"]
        else:
            return None


# Функция для получения списка всех слов в базе данных
async def get_all_words():
    async with pool.acquire() as connection:
        rows = await connection.fetch("SELECT * FROM words")
        return [row["word"] for row in rows]


# Функция для удаления слова из базы данных
async def delete_word(word):
    async with pool.acquire() as connection:
        result = await connection.execute("DELETE FROM words WHERE word = $1", word)
        return result.split()[1] == "1"


# Обработчик команды /start
@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я бот-словарь. Введите /help для получения списка доступных команд.")


# Обработчик команды /help
@dp.message_handler(commands=["help"])
async def cmd_help(message: types.Message):
    help_text = "Доступные команды:\n\n" \
                "/add - добавить слово и его определение\n" \
                "/find - найти определение слова\n" \
                "/all - показать все слова в словаре"

    await message.answer(help_text)


# Обработчик команды /add
@dp.message_handler(commands=["add"])
async def cmd_add(message: types.Message):
    await message.answer("Введите слово и его определение в формате 'слово - определение'")


# Обработчик текстового сообщения для добавления слова
@dp.message_handler(lambda message: message.text and "-" in message.text)
async def add_word_handler(message: types.Message):
    word, definition = message.text.split("-", 1)
    word = word.strip()
    definition = definition.strip()

    await add_word(word, definition)
    await message.answer(f"Слово '{word}' успешно добавлено в словарь.")


# Обработчик команды /find
@dp.message_handler(commands=["find"])
async def cmd_find(message: types.Message):
    await message.answer("Введите слово, определение которого вы хотите найти")


# Обработчик текстового сообщения для поиска слова
@dp.message_handler()
async def find_word_handler(message: types.Message):
    word = message.text.strip()
    definition = await find_word(word)
    if definition:
        await message.answer(f"Определение слова '{word}': {definition}")
    else:
        await message.answer(f"Слово '{word}' не найдено в словаре.")


# Обработчик команды /all
@dp.message_handler(commands=["all"])
async def cmd_all(message: types.Message):
    all_words = await get_all_words()
    if all_words:
        await message.answer("\n".join(all_words))
    else:
        await message.answer("Словарь пуст.")


# Обработчик команды /delete
@dp.message_handler(commands=["delete"])
async def cmd_delete(message: types.Message):
    await message.answer("Введите слово, которое нужно удалить из словаря.")


# Обработчик текстового сообщения для удаления слова
@dp.message_handler(lambda message: message.text)
async def delete_word_handler(message: types.Message):
    word = message.text.strip()
    if not word:
        await message.answer("Введите корректное слово.")
        return

    success = await delete_word(word)
    if success:
        await message.answer(f"Слово '{word}' успешно удалено из словаря.")
    else:
        await message.answer(f"Слово '{word}' не найдено в словаре.")


# Обработчик ошибок
@dp.errors_handler()
async def errors_handler(update: types.Update, exception: Exception):
    logging.exception(exception)
    await update.message.answer("Произошла ошибка. Попробуйте еще раз.")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
