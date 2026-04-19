import asyncio
from telethon import TelegramClient
from telethon.errors import *
import random

api_id = 25703573
api_hash = "754684e4b38847ccd0251441e408e839"

SEM = asyncio.Semaphore(3)

async def check(phone):
    async with SEM:
        client = TelegramClient(f's_{phone}', api_id, api_hash)
        await client.connect()

        try:
            await client.send_code_request(phone)
            res = f"{phone} ✅ GOOD"

        except FloodWaitError as e:
            if "Too many attempts" in str(e):
                res = f"{phone} ❄️ FROZEN"
            else:
                res = f"{phone} ⚠️ LIMIT"

        except PhoneNumberBannedError:
            res = f"{phone} 🚫 BANNED"

        except PhoneNumberInvalidError:
            res = f"{phone} ❌ INVALID"

        except Exception as e:
            res = f"{phone} ⚠️ {e}"

        await client.disconnect()
        await asyncio.sleep(random.uniform(2,4))
        return res


async def main():
    with open("numbers.txt") as f:
        nums = [x.strip() for x in f][:10]

    tasks = [check(n) for n in nums]
    results = await asyncio.gather(*tasks)

    with open("result.txt", "w") as f:
        f.write("\n".join(results))

asyncio.run(main())
