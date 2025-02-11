import os
import asyncio
import re
import json
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand, MenuButtonCommands
from sympy import symbols, Eq, solve, sin, cos, tan, log, sqrt, pi

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = Bot(token=TOKEN, parse_mode="Markdown")
dp = Dispatcher()

x = symbols('x')

USERS_FILE = "users.json"

# 📌 Завантаження даних
def load_users():
    try:
        with open(USERS_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_users(users):
    with open(USERS_FILE, "w") as file:
        json.dump(users, file, indent=4)

# 📌 Ліміти користувачів
def update_user_limits(user_id):
    users = load_users()
    today = datetime.now().strftime("%Y-%m-%d")

    if user_id not in users:
        users[user_id] = {"date": today, "count": 0, "premium": False}

    if users[user_id]["date"] != today:
        users[user_id]["date"] = today
        users[user_id]["count"] = 0

    users[user_id]["count"] += 1
    save_users(users)
    return users[user_id]

def is_limited(user_id):
    users = load_users()
    user = users.get(user_id, {"count": 0, "premium": False})
    return user["count"] >= 10 and not user["premium"]

def is_premium(user_id):
    users = load_users()
    return users.get(user_id, {}).get("premium", False)

def upgrade_to_premium(user_id):
    users = load_users()
    users[user_id] = {"date": datetime.now().strftime("%Y-%m-%d"), "count": 0, "premium": True}
    save_users(users)

# 📌 Обробка команди /start
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📏 Рівняння", callback_data="equation"),
         InlineKeyboardButton(text="📊 Нерівності", callback_data="inequality")],
        [InlineKeyboardButton(text="📐 Тригонометрія", callback_data="trigonometry"),
         InlineKeyboardButton(text="💎 Отримати Pro", callback_data="premium")]
    ])
    
    await message.answer("👋 **Вітаю! Це BrainMathX! Вибери, що ти хочеш розв’язати:", reply_markup=keyboard)

# 📌 Обробка команди /premium
@dp.message(Command("premium"))
async def send_premium_info(message: types.Message):
    await message.answer("💎 **Як отримати Pro-версію?**\n"
                         "🔹 Купити підписку (доступ до всіх функцій без обмежень)\n"
                         "🔹 Або чекати 24 години, щоб ліміт обнулився\n\n"
                         "**Підтримати проєкт та отримати Pro:**\n"
                         "🔹 Monobank: `https://send.monobank.ua/jar/ТВОЄ_ПОСИЛАННЯ`\n"
                         "🔹 PayPal: [Підтримати через PayPal](https://www.paypal.com/donate/?hosted_button_id=UK58MWKCMVVJA)\n"
                         "🔹 ПриватБанк: [Підтримати через Приват](ТВОЄ_ПОСИЛАННЯ_НА_БАНКУ)")

# 📌 Обробка натискання кнопок
@dp.callback_query()
async def process_callback(callback_query: types.CallbackQuery):
    data = callback_query.data
    if data == "equation":
        await callback_query.message.answer("📏 **Введи рівняння (наприклад, `2x + 3 = 7`)**")
    elif data == "inequality":
        await callback_query.message.answer("📊 **Введи нерівність (наприклад, `x^2 > 4`)**")
    elif data == "trigonometry":
        await callback_query.message.answer("📐 **Введи тригонометричний вираз (наприклад, `sin(30) + cos(60)`)**")
    elif data == "premium":
        await send_premium_info(callback_query.message)
    
    await callback_query.answer()

# 📌 Автоматична обробка математичних виразів
@dp.message()
async def solve_math(message: types.Message):
    user_id = str(message.from_user.id)

    # 📌 Ігнорувати команди (щоб не було "invalid syntax")
    if message.text.startswith("/"):
        return

    # 📌 Блокування логарифмів
    if "log" in message.text and not is_premium(user_id):
        await message.answer("🚫 **Логарифми доступні тільки в Pro-версії.**\n"
                             "Отримай доступ через /premium або зачекай 24 години.")
        return

    # 📌 Перевірка ліміту
    if is_limited(user_id):
        await message.answer("⏳ **Ти вичерпав 10 рішень на сьогодні.**\n"
                             "Отримай Pro через /premium або зачекай 24 години.")
        return

    try:
        update_user_limits(user_id)
        expression = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', message.text.replace("^", "**"))
        if "=" in expression:
            left, right = expression.split("=")
            equation = Eq(eval(left.strip(), {"x": x, "sin": sin, "cos": cos, "tan": tan, "log": log, "sqrt": sqrt, "pi": pi}),
                          eval(right.strip(), {"x": x, "sin": sin, "cos": cos, "tan": tan, "log": log, "sqrt": sqrt, "pi": pi}))
            solution = solve(equation, x)
            await message.answer(f"✏️ **Розв’язок:** `x = {solution}` ✅")
        else:
            result = eval(expression, {"x": x, "sin": lambda a: sin(a * pi / 180).evalf(),
                                       "cos": lambda a: cos(a * pi / 180).evalf(),
                                       "tan": lambda a: tan(a * pi / 180).evalf(),
                                       "log": log, "sqrt": sqrt, "pi": pi})
            await message.answer(f"🔢 **Відповідь:** `{result}` ✅")

    except Exception as e:
        await message.answer(f"❌ **Помилка:** {e}")

# 📌 Запуск бота
async def main():
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    asyncio.run(main())
