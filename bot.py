import os
import asyncio
import re
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sympy import symbols, solve, sin, cos, tan, log, sqrt, pi, diff, integrate, sympify

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = Bot(token=TOKEN, parse_mode="HTML")
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
        return eval(str(parsed_expr), {"x": x, "sin": sin, "cos": cos, "tan": tan, "log": log, "sqrt": sqrt, "pi": pi})
    except Exception as e:
        return f"Помилка: {e}"

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
    response = await solve_expression(message.text.strip())
    await message.answer(f"📌 Відповідь: <code>{response}</code>")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
