import os
import asyncio
import re
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand, MenuButtonCommands
from aiogram.fsm.storage.memory import MemoryStorage
from sympy import symbols, Eq, solve, sin, cos, tan, log, sqrt, pi, diff, integrate
from aiogram.client.default import DefaultBotProperties

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="Markdown"))
dp = Dispatcher(storage=MemoryStorage())

x = symbols('x')

def fix_equation(equation_str):
    equation_str = equation_str.replace("^", "**")
    equation_str = equation_str.replace("√(", "sqrt(")
    equation_str = equation_str.replace("Sqrt", "sqrt")
    equation_str = re.sub(r'log_(\d+)\((.*?)\)', r'log(\2, \1)', equation_str)
    equation_str = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', equation_str)
    return equation_str

async def start_server():
    app = web.Application()
    app.router.add_get("/", lambda request: web.Response(text="Bot is running!"))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.getenv("PORT", 8080)))
    await site.start()

async def set_menu():
    await bot.set_my_commands([
        BotCommand(command="start", description="Запустити бота"),
        BotCommand(command="help", description="Як користуватися ботом?")
    ])
    await bot.set_chat_menu_button(menu_button=MenuButtonCommands())

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📏 Рівняння", callback_data="equation"),
         InlineKeyboardButton(text="📊 Нерівності", callback_data="inequality")],
        [InlineKeyboardButton(text="📐 Тригонометрія", callback_data="trigonometry"),
         InlineKeyboardButton(text="📚 Логарифми", callback_data="logarithm")],
        [InlineKeyboardButton(text="📈 Похідні", callback_data="derivative"),
         InlineKeyboardButton(text="🔄 Інтеграли", callback_data="integral")]
    ])
    await message.answer("👋 **Вітаю!** Це BrainMathX – бот для розв’язання математичних виразів!", reply_markup=keyboard)

@dp.callback_query()
async def process_callback(callback_query: types.CallbackQuery):
    data = callback_query.data
    responses = {
        "equation": "📏 **Введи рівняння (наприклад, `2x + 3 = 7`)**",
        "inequality": "📊 **Введи нерівність (наприклад, `x^2 > 4`)**",
        "trigonometry": "📐 **Введи тригонометричний вираз (наприклад, `sin(30) + cos(60)`)**",
        "logarithm": "📚 **Введи логарифм (наприклад, `log_2(8)`)**",
        "derivative": "📈 **Введи функцію для знаходження похідної (наприклад, `diff(x^2 + 3x)`)**",
        "integral": "🔄 **Введи функцію для знаходження інтегралу (наприклад, `integrate(x^2 + 3x)`)**"
    }
    await callback_query.message.answer(responses.get(data, "❌ Невідома команда"))
    await callback_query.answer()

@dp.message()
async def solve_math(message: types.Message):
    user_input = message.text.strip()
    if user_input.startswith("/"):
        return
    
    try:
        expression = fix_equation(user_input)
        
        if "=" in expression:
            left, right = expression.split("=")
            equation = Eq(eval(left, {"x": x}), eval(right, {"x": x}))
            solution = solve(equation, x)
            await message.answer(f"✏️ **Розв’язок:** `x = {solution}` ✅")
        elif "diff(" in expression:
            expr = eval(expression.replace("diff", ""), {"x": x})
            derivative = diff(expr, x)
            await message.answer(f"📈 **Похідна:** `{derivative}` ✅")
        elif "integrate(" in expression:
            expr = eval(expression.replace("integrate", ""), {"x": x})
            integral = integrate(expr, x)
            await message.answer(f"🔄 **Інтеграл:** `{integral}` ✅")
        else:
            result = eval(expression, {"x": x, "sin": sin, "cos": cos, "tan": tan, "log": log, "sqrt": sqrt, "pi": pi})
            await message.answer(f"🔢 **Відповідь:** `{result}` ✅")
    except Exception as e:
        await message.answer(f"❌ **Помилка:** {e}")

async def main():
    await set_menu()
    await asyncio.gather(start_server(), dp.start_polling(bot, skip_updates=True))

if __name__ == "__main__":
    asyncio.run(main())
