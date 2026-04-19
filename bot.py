from aiogram import Bot, Dispatcher, types
import subprocess
import os
import asyncio

BOT_TOKEN = "TOKENING"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message()
async def handle(message: types.Message):
    if message.document:
        file = await bot.get_file(message.document.file_id)
        await bot.download_file(file.file_path, "numbers.txt")

        await message.answer("⏳ Tekshirilmoqda...")

        subprocess.run(["python3", "checker.py"])

        if os.path.exists("result.txt"):
            await message.answer_document(types.FSInputFile("result.txt"))

async def main():
    await dp.start_polling(bot)

asyncio.run(main())
