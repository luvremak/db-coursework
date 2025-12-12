import os
import aiohttp
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
BACKEND = os.getenv("BACKEND_URL").rstrip("/")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def api_call(method, path, json=None):
    async with aiohttp.ClientSession() as session:
        async with session.request(method, BACKEND+path, json=json) as resp:
            return await resp.json()

@dp.message(Command("register"))
async def register(message: types.Message):
    try:
        _, full_name, email = message.text.split(maxsplit=2)
    except ValueError:
        await message.answer("Usage: /register FullName Email")
        return
    payload = {"FullName": full_name, "Email": email, "PasswordHash": "dummyhash"}
    resp = await api_call("POST", "/users/", json=payload)
    await message.answer(f"Registered: {resp}")

@dp.message(Command("projects"))
async def projects(message: types.Message):
    resp = await api_call("GET", "/projects/")
    if isinstance(resp, list):
        text = "Projects:\n" + "\n".join([f"{p['ProjectID']} - {p['ProjectName']}" for p in resp])
    else:
        text = str(resp)
    await message.answer(text)

if __name__ == "__main__":
    from aiogram import executor
    executor.start_polling(dp)
