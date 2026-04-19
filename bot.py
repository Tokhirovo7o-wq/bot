import os
import asyncio
import subprocess
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message

# Telegram bot token (Railway ENV dan olinadi)
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# 📥 fayl qabul qilish handler
@dp.message()
async def handle_file(message: Message):
    if not message.document:
        await message.answer("📂 Iltimos numbers.txt yuboring")
        return

    # faylni yuklab olish
    file = await bot.get_file(message.document.file_id)
    await bot.download_file(file.file_path, "numbers.txt")

    await message.answer("⏳ Tekshirilmoqda... 10 ta limit bilan")

    # checker ishga tushirish
    process = subprocess.run(["python3", "checker.py"])

    # natijani yuborish
    try:
        with open("result.txt", "r") as f:
            result = f.read()

        await message.answer(f"✅ NATIJA:\n\n{result}")

    except FileNotFoundError:
        await message.answer("❌ result.txt topilmadi")


# 🚀 botni ishga tushirish
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
