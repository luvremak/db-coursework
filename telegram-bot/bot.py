import os
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import aiohttp
import logging

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
BACKEND_API = os.getenv("BACKEND_API_URL").rstrip("/")
API_KEY = os.getenv("API_KEY")  

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()

async def backend_request(method, path, json=None, params=None):
    url = f"{BACKEND_API}{path}"
    headers = {}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.request(method, url, json=json, params=params, headers=headers) as resp:
            text = await resp.text()
            try:
                data = await resp.json()
            except Exception:
                data = {"_raw_text": text}
            return resp.status, data

@dp.message(Command(commands=["start"]))
async def start_cmd(message: types.Message):
    tg_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name

    payload = {"tg_id": tg_id, "username": username}
    status, data = await backend_request("POST", "/users", json=payload)

    if 200 <= status < 300:
        await message.answer("Welcome! You're registered. 🎉")
    else:
        logger.error("Failed to register user: %s %s", status, data)
        await message.answer("Welcome! (but registration failed — tell my friend)")

@dp.message(Command(commands=["me"]))
async def me_cmd(message: types.Message):
    tg_id = message.from_user.id
    status, data = await backend_request("GET", f"/users/{tg_id}")

    if status == 200:
        text = "<b>Your profile</b>\n"
        text += f"Username: {data.get('username')}\n"
        text += f"Joined: {data.get('created_at', '—')}\n"
        await message.answer(text)
    elif status == 404:
        await message.answer("I don't have you in the DB. Try /start to register.")
    else:
        logger.error("Error fetching profile: %s %s", status, data)
        await message.answer("Could not fetch profile. Try again later.")

@dp.message(Command(commands=["users"]))
async def users_cmd(message: types.Message):
    allowed_admins = {123456789}  
    if message.from_user.id not in allowed_admins:
        await message.answer("You are not allowed to use this.")
        return

    status, data = await backend_request("GET", "/users")
    if status == 200:
        lines = []
        for u in data:  
            lines.append(f"{u.get('tg_id')} — {u.get('username')}")
        await message.answer("Users:\n" + "\n".join(lines[:100]))
    else:
        await message.answer("Failed to fetch users.")

@dp.message()
async def fallback(message: types.Message):
    await message.answer("I don't understand. Try /start or /me.")

if __name__ == "__main__":
    import asyncio
    from aiogram import executor
    logger.info("Starting bot (polling)...")
    executor.start_polling(dp, skip_updates=True)