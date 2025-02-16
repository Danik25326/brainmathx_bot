import os
import asyncio
import re
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.default import DefaultBotProperties
from sympy import symbols, Eq, solve, sin, cos, tan, log, sqrt, pi, diff, integrate, sympify

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 8080))

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

x = symbols('x')

def fix_equation(equation_str):
    equation_str = equation_str.replace("^", "**")
    equation_str = equation_str.replace("√(", "sqrt(").replace("Sqrt", "sqrt")
    equation_str = re.sub(r'log_(\d+)\((.*?)\)', r'log(\2, \1)', equation_str)
    equation_str = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', equation_str)
    equation_str = re.sub(r'(\d)!', r'factorial(\1)', equation_str)
    return equation_str

async def solve_expression(expression):
    try:
        expression = fix_equation(expression)
        parsed_expr = sympify(expression, locals={"x": x, "sin": sin, "cos": cos, "tan": tan, "log": log, "sqrt": sqrt, "pi": pi})
        result = parsed_expr.evalf()
        return str(result)
    except Exception as e:
        return f"Помилка: {e}"

async def solve_equation(equation):
    try:
        equation = fix_equation(equation)
        left, right = equation.split("=")
        solution = solve(Eq(sympify(left), sympify(right)), x)
        return f"Розв’язок: {solution}"
    except Exception as e:
        return f"Помилка: {e}"

async def send_math_result(message: types.Message, response: str):
    try:
        await message.answer(f"📌 Відповідь: <code>{response}</code>")
    except:
        await message.answer(f"📌 Відповідь: {response}")

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📏 Рівняння", callback_data="equation"),
         InlineKeyboardButton(text="📊 Нерівності", callback_data="inequality")],
        [InlineKeyboardButton(text="📐 Тригонометрія", callback_data="trigonometry"),
         InlineKeyboardButton(text="📚 Логарифми", callback_data="logarithm")],
        [InlineKeyboardButton(text="📈 Похідна", callback_data="derivative"),
         InlineKeyboardButton(text="📉 Інтеграл", callback_data="integral")]
    ])
    await message.answer("👋 Вітаю! Це BrainMathX – бот для розв’язання математичних виразів!", reply_markup=keyboard)

@dp.callback_query()
async def process_callback(callback_query: types.CallbackQuery):
    data = callback_query.data
    prompts = {
        "equation": "✏️ Введи рівняння (наприклад, 2x + 3 = 7)",
        "inequality": "📊 Введи нерівність (наприклад, x^2 - 4 > 0)",
        "trigonometry": "📐 Введи тригонометричний вираз (наприклад, sin(30) + cos(60))",
        "logarithm": "📚 Введи логарифмічний вираз (наприклад, log_2(8))",
        "derivative": "📈 Введи функцію для похідної (наприклад, x^3 + 2x)",
        "integral": "📉 Введи функцію для інтегралу (наприклад, x^3 + 2x)"
    }
    await callback_query.message.answer(prompts.get(data, "Невідома команда"))
    await callback_query.answer()

@dp.message()
async def handle_math(message: types.Message):
    if message.text.startswith("/"):
        return
    text = message.text.strip()
    if "=" in text:
        response = await solve_equation(text)
    else:
        response = await solve_expression(text)
    await send_math_result(message, response)

async def on_startup():
    await bot.delete_webhook(drop_pending_updates=True)  # Видалення старого вебхука
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown():
    await bot.delete_webhook()

async def handle_update(request):
    update = await request.json()
    await dp.feed_update(bot, types.Update(**update))
    return web.Response()

app = web.Application()
app.router.add_post("/webhook", handle_update)

dp.startup.register(on_startup)
dp.shutdown.register(on_shutdown)

async def main():
    await web._run_app(app, host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    asyncio.run(main())
